"""Tests for `main.py` — poll_once, polling_loop, and the FastAPI lifespan.

Covers every scenario in
`openspec/changes/backend-api/specs/polling-loop/spec.md`:
- poll_once: success order, error containment (get_fixture + check_and_push)
- polling_loop: cancellable, respects interval
- lifespan: live startup starts polling, mock startup no polling, shutdown order
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock

import httpx
from httpx import ASGITransport

from backend.main import poll_once, polling_loop


# ---------------------------------------------------------------------------
# poll_once — single polling iteration
# ---------------------------------------------------------------------------


class TestPollOnce:
    async def test_poll_once_success_order(self):
        """Spec: GIVEN a data source, initialized manager, and milestone
        detector, WHEN poll_once is called, THEN get_fixture, update_fixture,
        and check_and_push are called in that order.
        """
        call_order: list[str] = []
        fake_state = object()  # sentinel — update_fixture is mocked

        data_source = MagicMock()
        data_source.get_fixture = AsyncMock(
            side_effect=lambda: call_order.append("get_fixture") or fake_state
        )

        match_state = MagicMock()
        match_state.update_fixture = MagicMock(
            side_effect=lambda state: call_order.append("update_fixture")
        )

        detector = MagicMock()
        detector.check_and_push = AsyncMock(
            side_effect=lambda: call_order.append("check_and_push")
        )

        await poll_once(data_source, match_state, detector)

        assert call_order == ["get_fixture", "update_fixture", "check_and_push"]
        match_state.update_fixture.assert_called_once_with(fake_state)

    async def test_poll_once_get_fixture_logged(self, caplog):
        """Spec: GIVEN data_source.get_fixture raises an exception, WHEN
        poll_once is called, THEN the error is logged and no exception
        propagates to the caller.
        """
        data_source = MagicMock()
        data_source.get_fixture = AsyncMock(side_effect=RuntimeError("network down"))

        match_state = MagicMock()
        detector = MagicMock()
        detector.check_and_push = AsyncMock()

        with caplog.at_level(logging.ERROR):
            await poll_once(data_source, match_state, detector)  # must NOT raise

        # Error was logged at ERROR level
        assert any(
            "network down" in r.message for r in caplog.records if r.levelno >= logging.ERROR
        )
        # Subsequent calls did NOT happen (error contained early)
        match_state.update_fixture.assert_not_called()
        detector.check_and_push.assert_not_awaited()

    async def test_poll_once_check_push_logged(self, caplog):
        """Spec: GIVEN update_fixture succeeds but check_and_push raises,
        WHEN poll_once is called, THEN the error is logged and no exception
        propagates to the caller.
        """
        fake_state = object()
        data_source = MagicMock()
        data_source.get_fixture = AsyncMock(return_value=fake_state)

        match_state = MagicMock()
        match_state.update_fixture = MagicMock()

        detector = MagicMock()
        detector.check_and_push = AsyncMock(side_effect=RuntimeError("n8n down"))

        with caplog.at_level(logging.ERROR):
            await poll_once(data_source, match_state, detector)  # must NOT raise

        # Error was logged at ERROR level
        assert any(
            "n8n down" in r.message for r in caplog.records if r.levelno >= logging.ERROR
        )
        # update_fixture WAS called (succeeded before check_and_push raised)
        match_state.update_fixture.assert_called_once_with(fake_state)


# ---------------------------------------------------------------------------
# polling_loop — repeated poll_once with interval sleep
# ---------------------------------------------------------------------------


class _StopLoop(BaseException):
    """Control-flow sentinel to break out of the infinite loop in tests.

    Inherits from ``BaseException`` (not ``Exception``) so it bypasses
    ``poll_once``'s ``except Exception`` boundary — same mechanism as
    ``asyncio.CancelledError``.
    """


class _FakePollingTask:
    """Stand-in for an ``asyncio.Task`` used to assert the live-mode
    shutdown sequence.

    A real ``Task`` exposes a sync ``cancel()`` and is awaitable, but
    neither can be cleanly intercepted to record call order. This
    helper records both: ``cancel()`` appends ``"cancel"`` to the
    shared order list, and ``await fake_task`` appends ``"await"`` then
    completes without raising — so ``with suppress(CancelledError):
    await task`` runs the same code path as a real cancelled task.

    See ``test_shutdown_order_live``: the real polling task the lifespan
    started is cancelled and awaited FIRST (clean up), THEN this fake
    is swapped onto ``app.state.polling_task`` so shutdown's
    ``cancel()``/``await`` land here and become observable.
    """

    def __init__(self, order: list[str]) -> None:
        self._order = order
        self.cancel = MagicMock(
            side_effect=lambda *a, **k: self._order.append("cancel")
        )

    def __await__(self):
        self._order.append("await")
        yield from ()


class TestPollingLoop:
    async def test_polling_loop_cancellable(self):
        """Spec: GIVEN polling_loop running as an asyncio.Task, WHEN
        task.cancel() is called, THEN the loop stops and the task
        completes.
        """
        data_source = MagicMock()
        data_source.get_fixture = AsyncMock(return_value=object())
        match_state = MagicMock()
        detector = MagicMock()
        detector.check_and_push = AsyncMock()

        task = asyncio.create_task(
            polling_loop(data_source, match_state, detector, interval=0.01)
        )
        # Let it run at least one iteration
        await asyncio.sleep(0.05)
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

        assert task.done()
        assert task.cancelled()

    async def test_polling_loop_runs_and_respects_interval(self, monkeypatch):
        """Spec: GIVEN POLLING_INTERVAL=90 and live mode, WHEN polling_loop
        runs, THEN poll_once is invoked, followed by a 90-second wait,
        repeatedly.

        Triangulation: we pass interval=90 and verify ``asyncio.sleep``
        receives exactly 90 on every call.  A hardcoded value would
        fail this assertion.
        """
        real_sleep = asyncio.sleep
        sleep_intervals: list[float] = []
        sleep_call = 0

        async def tracking_sleep(seconds):
            nonlocal sleep_call
            sleep_call += 1
            sleep_intervals.append(seconds)
            if sleep_call >= 3:
                raise _StopLoop()
            await real_sleep(0)

        monkeypatch.setattr(asyncio, "sleep", tracking_sleep)

        poll_count = 0
        data_source = MagicMock()

        async def _get_fixture():
            nonlocal poll_count
            poll_count += 1
            return object()

        data_source.get_fixture = AsyncMock(side_effect=_get_fixture)
        match_state = MagicMock()
        detector = MagicMock()
        detector.check_and_push = AsyncMock()

        with suppress(_StopLoop):
            await polling_loop(data_source, match_state, detector, interval=90)

        assert sleep_intervals == [90, 90, 90]
        assert poll_count == 3

    async def test_polling_loop_continues_after_get_fixture_error(
        self, monkeypatch, caplog
    ):
        """Spec (raise→log→continue): GIVEN ``get_fixture`` raises on
        the first tick, WHEN ``polling_loop`` runs, THEN the error is
        logged AND the loop continues to the next tick —
        ``update_fixture`` runs on the successful second tick and no
        exception escapes the loop.

        Integrated test: drives the real ``polling_loop`` + ``poll_once``
        together, not ``poll_once`` in isolation. Triangulates with
        ``test_polling_loop_continues_after_check_and_push_error`` (a
        different failing step, same continue behaviour).
        """
        real_sleep = asyncio.sleep
        sleep_call = 0

        async def tracking_sleep(seconds):
            nonlocal sleep_call
            sleep_call += 1
            if sleep_call >= 2:
                raise _StopLoop()
            await real_sleep(0)

        monkeypatch.setattr(asyncio, "sleep", tracking_sleep)

        tick = 0

        async def _get_fixture():
            nonlocal tick
            tick += 1
            if tick == 1:
                raise RuntimeError("first tick boom")
            return object()

        data_source = MagicMock()
        data_source.get_fixture = AsyncMock(side_effect=_get_fixture)
        match_state = MagicMock()
        match_state.update_fixture = MagicMock()
        detector = MagicMock()
        detector.check_and_push = AsyncMock()

        with caplog.at_level(logging.ERROR):
            with suppress(_StopLoop):
                await polling_loop(
                    data_source, match_state, detector, interval=0.01
                )

        # raise → log: the first-tick error was logged at ERROR level.
        assert any(
            "first tick boom" in r.message
            for r in caplog.records
            if r.levelno >= logging.ERROR
        )
        # → continue: the loop reached a second tick (get_fixture ran twice).
        assert tick == 2
        # The successful second tick reached update_fixture (exactly once
        # — the failed first tick never got there).
        match_state.update_fixture.assert_called_once()
        detector.check_and_push.assert_awaited_once()
        # No exception escaped: only _StopLoop (a BaseException) broke the
        # loop — poll_once contained the RuntimeError.

    async def test_polling_loop_continues_after_check_and_push_error(
        self, monkeypatch, caplog
    ):
        """Spec (raise→log→continue): GIVEN ``check_and_push`` raises on
        the first tick (after ``get_fixture`` and ``update_fixture``
        succeed), WHEN ``polling_loop`` runs, THEN the error is logged
        AND the loop continues to the next tick — proving containment is
        not specific to ``get_fixture``.
        """
        real_sleep = asyncio.sleep
        sleep_call = 0

        async def tracking_sleep(seconds):
            nonlocal sleep_call
            sleep_call += 1
            if sleep_call >= 2:
                raise _StopLoop()
            await real_sleep(0)

        monkeypatch.setattr(asyncio, "sleep", tracking_sleep)

        tick = 0

        async def _check_and_push():
            nonlocal tick
            tick += 1
            if tick == 1:
                raise RuntimeError("detector boom")
            # second tick: no-op success

        data_source = MagicMock()
        data_source.get_fixture = AsyncMock(return_value=object())
        match_state = MagicMock()
        match_state.update_fixture = MagicMock()
        detector = MagicMock()
        detector.check_and_push = AsyncMock(side_effect=_check_and_push)

        with caplog.at_level(logging.ERROR):
            with suppress(_StopLoop):
                await polling_loop(
                    data_source, match_state, detector, interval=0.01
                )

        assert any(
            "detector boom" in r.message
            for r in caplog.records
            if r.levelno >= logging.ERROR
        )
        # → continue: the loop reached a second tick.
        assert tick == 2
        # get_fixture + update_fixture succeeded on BOTH ticks (only
        # check_and_push raised on tick 1).
        assert match_state.update_fixture.call_count == 2
        assert detector.check_and_push.await_count == 2


# ---------------------------------------------------------------------------
# lifespan — FastAPI startup/shutdown context manager
# ---------------------------------------------------------------------------


class TestLifespan:
    async def test_lifespan_live_starts_polling(self, monkeypatch, mock_datasource):
        """Spec: GIVEN MOCK_MODE=false, WHEN the app lifespan starts,
        THEN services are created, the manager is initialized, and the
        polling task is running.
        """
        from backend.config import Settings
        from backend.main import app, lifespan

        mock_settings = Settings(
            MOCK_MODE=False,
            API_FOOTBALL_KEY="test-key",
            FIXTURE_ID=868019,
        )
        monkeypatch.setattr("backend.main.Settings", lambda: mock_settings)
        monkeypatch.setattr(
            "backend.main.create_data_source", lambda s: mock_datasource
        )

        async with lifespan(app):
            assert app.state.settings is mock_settings
            assert app.state.data_source is mock_datasource
            assert hasattr(app.state, "match_state")
            assert hasattr(app.state, "milestone_detector")
            assert app.state.polling_task is not None
            assert isinstance(app.state.polling_task, asyncio.Task)
            assert not app.state.polling_task.done()

    async def test_lifespan_mock_no_polling_task(self, monkeypatch, mock_datasource):
        """Spec: GIVEN MOCK_MODE=true, WHEN the app lifespan starts,
        THEN services are created and the manager is initialized, but
        no polling task exists.
        """
        from backend.config import Settings
        from backend.main import app, lifespan

        mock_settings = Settings(MOCK_MODE=True)
        monkeypatch.setattr("backend.main.Settings", lambda: mock_settings)
        monkeypatch.setattr(
            "backend.main.create_data_source", lambda s: mock_datasource
        )

        async with lifespan(app):
            assert app.state.settings is mock_settings
            assert app.state.data_source is mock_datasource
            assert hasattr(app.state, "match_state")
            assert hasattr(app.state, "milestone_detector")
            assert app.state.polling_task is None

    async def test_shutdown_order_live(self, monkeypatch, mock_datasource):
        """Spec: GIVEN a running app with an active polling task (live
        mode), WHEN the app lifespan shuts down, THEN shutdown runs all
        four steps in order: 1) ``polling_task.cancel()``, 2) ``await
        polling_task`` (``CancelledError`` suppressed), 3)
        ``milestone_detector.aclose()``, 4) ``client.aclose()``.
        """
        from backend.config import Settings
        from backend.data_source import LiveDataSource
        from backend.main import app, lifespan

        mock_settings = Settings(
            MOCK_MODE=False,
            API_FOOTBALL_KEY="test-key",
            FIXTURE_ID=868019,
        )
        monkeypatch.setattr("backend.main.Settings", lambda: mock_settings)

        # Create a real LiveDataSource with a mock client so
        # isinstance(_, LiveDataSource) passes and _client.aclose exists.
        fake_state = await mock_datasource.get_fixture()
        mock_client = MagicMock()
        live_ds = LiveDataSource(client=mock_client, fixture_id=868019)
        live_ds.get_fixture = AsyncMock(return_value=fake_state)
        live_ds.get_details = AsyncMock(return_value=([], None, None, [], []))
        monkeypatch.setattr(
            "backend.main.create_data_source", lambda s: live_ds
        )

        order: list[str] = []

        async with lifespan(app):
            # The lifespan started a real polling task. Cancel and await
            # it (clean up), then swap in a fake that records cancel() +
            # the await — so all four shutdown steps are observable
            # (cancel/await on a real Task can't be intercepted cleanly).
            real_task = app.state.polling_task
            assert real_task is not None
            real_task.cancel()
            with suppress(asyncio.CancelledError):
                await real_task
            app.state.polling_task = _FakePollingTask(order)

            # Replace aclose methods with tracking mocks AFTER startup
            # so the shutdown path uses them.
            app.state.milestone_detector.aclose = AsyncMock(
                side_effect=lambda: order.append("detector_aclose")
            )
            mock_client.aclose = AsyncMock(
                side_effect=lambda: order.append("client_aclose")
            )

        # Shutdown order: cancel → await → detector → client (all 4 steps).
        assert order == ["cancel", "await", "detector_aclose", "client_aclose"]

    async def test_lifespan_mock_shutdown_closes_detector_not_client(
        self, monkeypatch, mock_datasource
    ):
        """Spec (mock-mode shutdown): GIVEN MOCK_MODE=true, WHEN the app
        lifespan starts AND shuts down, THEN the milestone detector IS
        closed, but the API client is NOT closed — the data source is a
        ``MockDataSource`` so ``isinstance(_, LiveDataSource)`` is False
        and the client-close branch is skipped.

        End-to-end lifespan test (startup + shutdown) in mock mode.
        Triangulates against ``test_shutdown_order_live`` (live mode):
        together they cover both branches of the ``isinstance`` guard
        (live → client closed; mock → client not closed). A sentinel
        client is attached to the data source so "client NOT closed" is
        a concrete assertion that proves the isinstance guard — not the
        absence of ``_client`` — protects the client.
        """
        from backend.config import Settings
        from backend.data_source import LiveDataSource
        from backend.main import app, lifespan

        mock_settings = Settings(MOCK_MODE=True)
        monkeypatch.setattr("backend.main.Settings", lambda: mock_settings)
        monkeypatch.setattr(
            "backend.main.create_data_source", lambda s: mock_datasource
        )

        # Attach a sentinel client so "client NOT closed" is a concrete,
        # verifiable assertion — proves the isinstance guard (not the
        # absence of _client) skips the client-close branch.
        sentinel_client = MagicMock()
        sentinel_client.aclose = AsyncMock()
        mock_datasource._client = sentinel_client

        order: list[str] = []

        async with lifespan(app):
            # Mock mode → no polling task; data source is not live.
            assert app.state.polling_task is None
            assert not isinstance(app.state.data_source, LiveDataSource)
            # Replace detector.aclose AFTER startup so shutdown uses it.
            app.state.milestone_detector.aclose = AsyncMock(
                side_effect=lambda: order.append("detector_aclose")
            )

        # Detector WAS closed; client was NOT (isinstance guard held).
        assert order == ["detector_aclose"]
        app.state.milestone_detector.aclose.assert_awaited_once()
        sentinel_client.aclose.assert_not_called()


# ---------------------------------------------------------------------------
# Lifespan — lineups fetch on startup (enrich-context)
# ---------------------------------------------------------------------------


class TestLifespanLineups:
    async def test_lifespan_fetches_lineups_on_startup(self, monkeypatch, mock_datasource):
        """Spec: lineups are fetched on startup and stored on the match state.

        After lifespan startup, `app.state.match_state.get_state()`
        must have `home_lineup` and `away_lineup` populated (not None)
        when the data source provides lineups.
        """
        from backend.config import Settings
        from backend.main import app, lifespan

        mock_settings = Settings(MOCK_MODE=True)
        monkeypatch.setattr("backend.main.Settings", lambda: mock_settings)
        monkeypatch.setattr(
            "backend.main.create_data_source", lambda s: mock_datasource
        )

        async with lifespan(app):
            state = app.state.match_state.get_state()
            assert state.home_lineup is not None
            assert state.away_lineup is not None
            assert state.home_lineup.formation == "4-3-3"
            assert state.away_lineup.formation == "3-4-1-2"

    async def test_lifespan_none_lineups_no_op(self, monkeypatch, tmp_path, mock_data_dir):
        """Spec: when get_lineups returns (None, None), update_lineups
        is still called (stores None/None, no error)."""
        import shutil

        from backend.config import Settings
        from backend.data_source import MockDataSource
        from backend.main import app, lifespan

        # Copy fixture.json so get_fixture works, but DON'T copy
        # lineups.json so get_lineups returns (None, None).
        shutil.copy(mock_data_dir / "fixture.json", tmp_path / "fixture.json")
        mock_settings = Settings(MOCK_MODE=True)
        empty_ds = MockDataSource(tmp_path)
        monkeypatch.setattr("backend.main.Settings", lambda: mock_settings)
        monkeypatch.setattr(
            "backend.main.create_data_source", lambda s: empty_ds
        )

        async with lifespan(app):
            state = app.state.match_state.get_state()
            assert state.home_lineup is None
            assert state.away_lineup is None


# ---------------------------------------------------------------------------
# app — FastAPI instance with router wired
# ---------------------------------------------------------------------------


class TestApp:
    def test_app_imports_and_includes_router(self):
        """Spec: the app must import successfully and include the
        partido router with all 8 routes.
        """
        from backend.main import app

        route_paths = [r.path for r in app.routes]
        expected_paths = [
            "/health",
            "/partido/estado",
            "/partido/contexto",
            "/partido/predicciones",
            "/partido/prediccion",
            "/mock/avanzar",
            "/mock/set-minute",
            "/stats/requests",
        ]
        for path in expected_paths:
            assert path in route_paths, f"missing route: {path}"
