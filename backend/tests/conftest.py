"""Shared pytest fixtures for the AI DT backend test suite.

Exposes:
- `mock_data_dir`: path to `backend/mock_data/` (the 19 API-Football v3 JSONs).
- `mock_datasource`: a `MockDataSource` rooted at `mock_data_dir`.
- `match_state`: a fresh `MatchStateManager` (change 2, PR 1).
- `populated_match_state`: a `MatchStateManager` already seeded with
  the bare-bones `MatchState` from `mock_datasource.get_fixture()`.
- `mock_settings`/`live_settings`: `Settings` in mock/live mode.
- `live_ds`: a `LiveDataSource` wrapping a fake API client with a
  configurable `request_count` (for the `/stats/requests` live test).
- `mock_state`/`live_state`: populated `MatchStateManager` instances.
- `mock_app`/`live_app`: FastAPI apps with pre-populated `app.state`
  (no lifespan) — the router reads services via `Depends(get_*)`.
- `mock_client`/`live_client`: `httpx.AsyncClient` over `ASGITransport`
  so endpoint tests drive the app end-to-end without a network socket.

The conftest lives at `backend/tests/conftest.py` so it is auto-discovered
by pytest without an explicit import. It imports `MockDataSource` and
`MatchStateManager` lazily so a missing or broken module will fail at
the test site, not at collection time — this is the gate that keeps
RED honest.
"""
from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport


class _FakeApiClient:
    """Minimal stand-in for `APIFootballClient` in live-mode router tests.

    The only attribute the `/stats/requests` endpoint reads is
    `request_count` (via `LiveDataSource._client.request_count`).
    Keeping the fake here avoids spinning up a real httpx stack and
    keeps the live stats test deterministic.
    """

    def __init__(self, request_count: int = 5) -> None:
        self.request_count = request_count


@pytest.fixture
def mock_data_dir() -> Path:
    """Absolute path to the `backend/mock_data/` directory."""
    return Path(__file__).parent.parent / "mock_data"


@pytest.fixture
def mock_datasource(mock_data_dir: Path):
    """A `MockDataSource` instance rooted at the real mock JSONs.

    Imported lazily so the fixture is collected AFTER the test file
    imports it — keeps the import error visible at the test site.
    """
    from backend.data_source import MockDataSource

    return MockDataSource(mock_data_dir)


@pytest.fixture
def match_state():
    """A fresh `MatchStateManager` (no fixture, no events).

    Imported lazily so a broken `match_state` module fails at the
    test site, not at collection time.
    """
    from backend.services.match_state import MatchStateManager

    return MatchStateManager()


@pytest.fixture
def populated_match_state(mock_datasource):
    """A `MatchStateManager` already seeded with the bare-bones
    `MatchState` from `mock_datasource.get_fixture()`.

    `get_fixture()` is async; we drive it with `asyncio.run` so the
    fixture stays sync (matches the rest of the conftest surface).
    """
    import asyncio

    from backend.services.match_state import MatchStateManager

    ms = MatchStateManager()
    state = asyncio.run(mock_datasource.get_fixture())
    ms.update_fixture(state)
    return ms


# ---------------------------------------------------------------------------
# Router test fixtures — mock/live mode apps + async clients
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_settings():
    """`Settings` in mock mode (the safe default, no live credentials)."""
    from backend.config import Settings

    return Settings(MOCK_MODE=True)


@pytest.fixture
def live_settings():
    """`Settings` in live mode with test credentials (satisfies the
    model validator that requires API_FOOTBALL_KEY + positive FIXTURE_ID).
    """
    from backend.config import Settings

    return Settings(MOCK_MODE=False, API_FOOTBALL_KEY="test-key", FIXTURE_ID=868019)


@pytest.fixture
def live_ds():
    """A `LiveDataSource` wrapping a fake API client.

    The fake client carries `request_count=5` so the `/stats/requests`
    live-mode test can assert a non-zero count without real network I/O.
    """
    from backend.data_source import LiveDataSource

    return LiveDataSource(client=_FakeApiClient(request_count=5), fixture_id=868019)


@pytest.fixture
def mock_state(populated_match_state):
    """A populated `MatchStateManager` for mock-mode router tests."""
    return populated_match_state


@pytest.fixture
def live_state(mock_datasource):
    """A populated `MatchStateManager` for live-mode router tests.

    A separate instance from `mock_state` so mutations in one mode's
    tests never leak into the other.
    """
    import asyncio

    from backend.services.match_state import MatchStateManager

    ms = MatchStateManager()
    state = asyncio.run(mock_datasource.get_fixture())
    ms.update_fixture(state)
    return ms


@pytest.fixture
def mock_detector(mock_datasource, mock_state):
    """A `MilestoneDetector` with an empty n8n URL (no-op push).

    `/mock/avanzar` calls `check_and_push()`; the empty URL short-circuits
    it so no HTTP is made and no webhook payload leaves the process.
    """
    from backend.services.milestones import MilestoneDetector

    return MilestoneDetector(
        data_source=mock_datasource,
        match_state=mock_state,
        n8n_url="",
    )


@pytest.fixture
def live_detector(live_ds, live_state):
    """A `MilestoneDetector` for the live app (unused by `/mock/*` since
    those routes 404 in live mode, but kept on `app.state` for parity).
    """
    from backend.services.milestones import MilestoneDetector

    return MilestoneDetector(
        data_source=live_ds,
        match_state=live_state,
        n8n_url="",
    )


def _build_app(settings, data_source, match_state, milestone_detector):
    """Build a FastAPI app with a pre-populated `app.state`.

    No lifespan runs — the router reads services via `Depends(get_*)`
    which resolve against `request.app.state`. This is the test seam.
    """
    from fastapi import FastAPI

    from backend.routers.partido import router

    app = FastAPI()
    app.include_router(router)
    app.state.settings = settings
    app.state.data_source = data_source
    app.state.match_state = match_state
    app.state.milestone_detector = milestone_detector
    return app


@pytest.fixture
def mock_app(mock_settings, mock_datasource, mock_state, mock_detector):
    """FastAPI app in mock mode with pre-populated `app.state`."""
    return _build_app(mock_settings, mock_datasource, mock_state, mock_detector)


@pytest.fixture
def live_app(live_settings, live_ds, live_state, live_detector):
    """FastAPI app in live mode with pre-populated `app.state`."""
    return _build_app(live_settings, live_ds, live_state, live_detector)


@pytest.fixture
async def mock_client(mock_app):
    """`httpx.AsyncClient` over `ASGITransport` for mock-mode endpoint tests."""
    transport = ASGITransport(app=mock_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def live_client(live_app):
    """`httpx.AsyncClient` over `ASGITransport` for live-mode endpoint tests."""
    transport = ASGITransport(app=live_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def uninit_state():
    """A fresh, UN-populated `MatchStateManager` (raises `RuntimeError`
    on `get_state`/`get_context_text`). Used by the 500-path endpoint tests.
    """
    from backend.services.match_state import MatchStateManager

    return MatchStateManager()


@pytest.fixture
def uninit_app(mock_settings, mock_datasource, uninit_state):
    """FastAPI app whose `match_state` is uninitialized — for the
    `/partido/estado` and `/partido/contexto` 500-path tests.
    """
    from backend.services.milestones import MilestoneDetector

    detector = MilestoneDetector(
        data_source=mock_datasource,
        match_state=uninit_state,
        n8n_url="",
    )
    return _build_app(mock_settings, mock_datasource, uninit_state, detector)


@pytest.fixture
async def uninit_client(uninit_app):
    """`httpx.AsyncClient` over `ASGITransport` for the 500-path tests."""
    transport = ASGITransport(app=uninit_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
