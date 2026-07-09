"""Shared pytest fixtures for the AI DT backend test suite.

Exposes:
- `mock_data_dir`: path to `backend/mock_data/` (the 19 API-Football v3 JSONs).
- `mock_datasource`: a `MockDataSource` rooted at `mock_data_dir`.

The conftest lives at `backend/tests/conftest.py` so it is auto-discovered
by pytest without an explicit import. It imports `MockDataSource` from
`backend.data_source`, which means **a missing or broken `data_source`
module will fail to collect the fixture, not just fail a test** — this is
the gate that keeps RED honest.
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
