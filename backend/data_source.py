"""Data source strategy for AI DT backend match data.

A `DataSource` Protocol defines the contract for fetching a fixture
and its per-momento details. `MockDataSource` reads local JSON
files (the 19 files in `backend/mock_data/`), `LiveDataSource` is
a stub for change 2, and `create_data_source(config)` selects the
right one based on `Settings.MOCK_MODE`.

CRITICAL invariant: both implementations call the SAME `parse_*`
functions from `backend.parsers`. There is no second path to a
`MatchState` — the mock/live distinction is purely about WHERE the
raw v3 envelope comes from, never HOW it is parsed.

Spec: openspec/changes/backend-foundation/specs/data-source-strategy/spec.md
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Protocol, runtime_checkable

from backend.config import Settings
from backend.models import MatchEvent, MatchState, PlayerStats, TeamStats
from backend.parsers import (
    parse_events,
    parse_fixture,
    parse_players,
    parse_statistics,
)

log = logging.getLogger(__name__)

# Map a momento (1-6) to the file-key suffix used in the JSON
# filenames. The keys are NOT the actual minutes — `ht` is "halftime"
# (minute 45) and `ft` is "full time" (minute 90+, with stoppage time
# up to 101 in this fixture). Changing this map is the only way to
# add a new snapshot.
MOMENTO_FILE_KEYS: dict[int, str] = {
    1: "15",
    2: "30",
    3: "ht",
    4: "60",
    5: "75",
    6: "ft",
}

# Default mock data directory. Resolved relative to this file so the
# data source is importable from anywhere (tests, REPL, container).
_MOCK_DATA_DIR = Path(__file__).parent / "mock_data"


@runtime_checkable
class DataSource(Protocol):
    """Structural protocol for any match data source.

    Any class implementing both async methods with the documented
    signatures passes `isinstance(_, DataSource)`, regardless of
    inheritance. Mock and live sources are interchangeable at the
    type level — downstream code branches only on the shape of the
    returned models.
    """

    async def get_fixture(self) -> MatchState: ...

    async def get_details(
        self, momento: int
    ) -> tuple[list[MatchEvent], TeamStats | None, TeamStats | None, list[PlayerStats], list[PlayerStats]]: ...


class MockDataSource:
    """Reads pre-recorded API-Football v3 JSONs from a local directory.

    The `mock_dir` is injected via the constructor so tests can point
    at a fixture-specific directory. The factory in
    `create_data_source()` uses the default `_MOCK_DATA_DIR`.
    """

    def __init__(self, mock_dir: Path):
        self.mock_dir = mock_dir

    def _load_json(self, filename: str) -> list[dict]:
        """Read one mock JSON file and return its `response` array.

        Raises `FileNotFoundError` if the file is missing. Surfaces
        API-level errors (the v3 envelope has an `errors` key) via a
        warning log so silent corrupt fixtures are visible in CI.
        """
        path = self.mock_dir / filename
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("errors"):
            log.warning("mock %s contains errors: %s", filename, data["errors"])
        return data.get("response") or []

    async def get_fixture(self) -> MatchState:
        """Return the bare-bones MatchState for the fixture.

        Events, stats, and players are NOT populated here — they
        come from `get_details(momento)`. This matches the spec:
        `get_fixture()` returns "current fixture identity (teams,
        score, status, no events)".
        """
        raw = self._load_json("fixture.json")
        return parse_fixture(raw[0])

    async def get_details(
        self, momento: int
    ) -> tuple[list[MatchEvent], TeamStats | None, TeamStats | None, list[PlayerStats], list[PlayerStats]]:
        """Return the per-momento detail snapshot.

        Loads `events_{key}.json`, `statistics_{key}.json`, and
        `players_{key}.json` where `key` is `MOMENTO_FILE_KEYS[momento]`.
        A missing key (e.g. momento=99) raises `FileNotFoundError`
        from the underlying `open()`, satisfying the spec.
        """
        try:
            key = MOMENTO_FILE_KEYS[momento]
        except KeyError as exc:
            raise FileNotFoundError(
                f"no mock data for momento={momento}; valid momenti are {sorted(MOMENTO_FILE_KEYS)}"
            ) from exc

        events = parse_events(self._load_json(f"events_{key}.json"))
        home_stats, away_stats = parse_statistics(self._load_json(f"statistics_{key}.json"))
        home_players, away_players = parse_players(self._load_json(f"players_{key}.json"))
        return events, home_stats, away_stats, home_players, away_players


class LiveDataSource:
    """Adapter that turns an `APIFootballClient` into a `DataSource`.

    The live source is structurally identical to the mock source:
    `get_fixture` returns a `MatchState`, `get_details(momento)`
    returns a 5-tuple of (events, home_stats, away_stats, home_players,
    away_players). The only difference is WHERE the raw v3 envelope
    comes from — the live source fetches it from the API, the mock
    source reads it from disk. Both share the same `parse_*` path
    in `backend.parsers`.

    `momento` is accepted for Protocol compatibility but currently
    has no effect on the live side — the API does not expose a
    "momento" concept, the live source always fetches the current
    snapshot. The argument is reserved for future caching / snapshot
    layers.
    """

    def __init__(self, client: "APIFootballClient", fixture_id: int) -> None:
        self._client = client
        self._fixture_id = fixture_id

    async def get_fixture(self) -> MatchState:
        """Fetch the fixture and parse it into a `MatchState`."""
        raw = await self._client.fetch_fixture(self._fixture_id)
        return parse_fixture(raw)

    async def get_details(
        self, momento: int
    ) -> tuple[list[MatchEvent], TeamStats | None, TeamStats | None, list[PlayerStats], list[PlayerStats]]:
        """Fetch events, statistics, and players; return the 5-tuple.

        `momento` is currently ignored — see class docstring.
        """
        events = parse_events(await self._client.fetch_events(self._fixture_id))
        home_stats, away_stats = parse_statistics(
            await self._client.fetch_statistics(self._fixture_id)
        )
        home_players, away_players = parse_players(
            await self._client.fetch_players(self._fixture_id)
        )
        return events, home_stats, away_stats, home_players, away_players


def create_data_source(config: Settings) -> DataSource:
    """Factory: return a `MockDataSource` or `LiveDataSource` per `config.MOCK_MODE`.

    The returned object ALWAYS satisfies the `DataSource` Protocol,
    so callers can treat both modes uniformly. Live mode constructs
    a fresh `APIFootballClient` per process and wraps it in a
    `LiveDataSource` — the polling loop's lifespan owns the client
    shutdown via `LiveDataSource._client.aclose()` (or via the
    detector's own client lifecycle in change 3).

    The `APIFootballClient` import is local to keep this module
    importable even when httpx is not installed (e.g. lightweight
    tooling) — the live code path is never hit in mock mode.
    """
    if config.MOCK_MODE:
        return MockDataSource(_MOCK_DATA_DIR)
    from backend.services.api_football import APIFootballClient

    client = APIFootballClient(api_key=config.API_FOOTBALL_KEY)
    return LiveDataSource(client=client, fixture_id=config.FIXTURE_ID)
