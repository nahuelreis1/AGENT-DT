"""Shared pytest fixtures for the AI DT backend test suite.

Exposes:
- `mock_data_dir`: path to `backend/mock_data/` (the 19 API-Football v3 JSONs).
- `mock_datasource`: a `MockDataSource` rooted at `mock_data_dir`.
- `match_state`: a fresh `MatchStateManager` (change 2, PR 1).
- `populated_match_state`: a `MatchStateManager` already seeded with
  the bare-bones `MatchState` from `mock_datasource.get_fixture()`.

The conftest lives at `backend/tests/conftest.py` so it is auto-discovered
by pytest without an explicit import. It imports `MockDataSource` and
`MatchStateManager` lazily so a missing or broken module will fail at
the test site, not at collection time — this is the gate that keeps
RED honest.
"""
from pathlib import Path

import pytest


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
