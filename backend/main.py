"""FastAPI application entry point for the AI DT backend.

Creates the FastAPI app, the async lifespan context manager that
wires all services onto ``app.state``, and the polling loop that
drives live-mode updates.

Spec: openspec/changes/backend-api/specs/polling-loop/spec.md
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from backend.config import Settings
from backend.data_source import LiveDataSource, create_data_source
from backend.routers.partido import router as partido_router
from backend.services.match_state import MatchStateManager
from backend.services.milestones import MilestoneDetector

log = logging.getLogger(__name__)


async def poll_once(data_source, match_state, milestone_detector) -> None:
    """Single polling iteration.

    Executes the sequence ``get_fixture`` -> ``update_fixture`` ->
    ``check_and_push`` in order.  Errors are contained (logged, not
    raised) so the polling loop never crashes on a single bad
    iteration.
    """
    try:
        state = await data_source.get_fixture()
        match_state.update_fixture(state)
        await milestone_detector.check_and_push()
    except Exception as exc:
        log.error("polling error: %s", exc)


async def polling_loop(
    data_source, match_state, milestone_detector, interval: float
) -> None:
    """Repeatedly call :func:`poll_once` every *interval* seconds.

    The loop has **no** try/except — it relies on :func:`poll_once`
    swallowing all ``Exception`` subclasses.  The only exception that
    escapes is ``asyncio.CancelledError`` (a ``BaseException``), which
    is the intended cancellation path via ``task.cancel()``.
    """
    while True:
        await poll_once(data_source, match_state, milestone_detector)
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: create services on startup, tear down on shutdown.

    Startup:
    1. Create ``Settings`` (reads env / ``.env``).
    2. Create the data source via ``create_data_source(settings)``.
    3. Create ``MatchStateManager`` and prime it with the first fixture.
    4. Create ``MilestoneDetector``.
    5. In live mode (``not MOCK_MODE``) start the polling task.

    Shutdown (strict order):
    1. Cancel the polling task and await it (suppress ``CancelledError``).
    2. ``aclose`` the milestone detector.
    3. ``aclose`` the API client (only in live mode — ``isinstance`` check).

    Deviation from design: ``app.state.settings`` is used instead of
    ``app.state.config`` to match the router's ``get_settings``
    dependency, which reads ``request.app.state.settings``.
    """
    settings = Settings()
    app.state.settings = settings
    app.state.data_source = create_data_source(settings)
    app.state.match_state = MatchStateManager()

    # Prime the manager with the first fixture so endpoints work on
    # the very first request (no cold-start 500).
    initial_state = await app.state.data_source.get_fixture()
    app.state.match_state.update_fixture(initial_state)

    # Fetch lineups once at startup (not per-momento). Lineups are
    # loaded before any milestone fires so the context text can
    # include FORMACIONES and TODOS LOS JUGADORES from the first
    # prediction. A (None, None) result (204 pre-kickoff, or missing
    # lineups.json in mock mode) is a no-op — update_lineups stores
    # None/None and the sections collapse to their fallbacks.
    try:
        home_lineup, away_lineup = await app.state.data_source.get_lineups()
        app.state.match_state.update_lineups(home_lineup, away_lineup)
    except Exception as exc:
        log.warning("lineups fetch failed: %s", exc)

    app.state.milestone_detector = MilestoneDetector(
        data_source=app.state.data_source,
        match_state=app.state.match_state,
        n8n_url=settings.N8N_WEBHOOK_BASE_URL,
    )

    if not settings.MOCK_MODE:
        app.state.polling_task = asyncio.create_task(
            polling_loop(
                app.state.data_source,
                app.state.match_state,
                app.state.milestone_detector,
                settings.POLLING_INTERVAL,
            )
        )
    else:
        app.state.polling_task = None

    yield

    # Shutdown: cancel task FIRST so no in-flight request hits a
    # closed httpx connection.
    if app.state.polling_task is not None:
        app.state.polling_task.cancel()
        with suppress(asyncio.CancelledError):
            await app.state.polling_task

    await app.state.milestone_detector.aclose()

    if isinstance(app.state.data_source, LiveDataSource):
        await app.state.data_source._client.aclose()


app = FastAPI(title="AI DT Backend", lifespan=lifespan)
app.include_router(partido_router)
