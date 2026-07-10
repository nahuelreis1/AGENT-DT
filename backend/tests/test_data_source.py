"""Tests for the data-source-strategy layer.

Covers every scenario in
`openspec/changes/backend-foundation/specs/data-source-strategy/spec.md`
plus triangulation cases that exercise the real code paths
(cumulative-event ordering, stats shape, player count, factory
branches, structural typing).

These tests reference `backend.data_source` and the live JSON files in
`backend/mock_data/`. Both are needed to make the suite pass — no fake
data, no mocks of the data source under test.

`LiveDataSource` is tested via a `FakeAPIFootballClient` that records
calls and returns canned v3 envelopes. This isolates the
`LiveDataSource` layer from the httpx client — the integration of the
two is exercised in `test_api_football.py`.
"""
from __future__ import annotations

import pytest

from backend.config import Settings
from backend.data_source import (
    DataSource,
    LiveDataSource,
    MockDataSource,
    create_data_source,
)
from backend.models import MatchEvent, MatchState, PlayerStats, TeamStats
from backend.parsers import parse_fixture, parse_players, parse_statistics


# ---------------------------------------------------------------------------
# FakeAPIFootballClient — records calls, returns canned v3 data.
# Used to verify `LiveDataSource` delegates to the client + parsers
# without spinning up a real httpx stack.
# ---------------------------------------------------------------------------


class FakeAPIFootballClient:
    """Stand-in for `APIFootballClient` in `LiveDataSource` tests.

    Each `fetch_*` method records the `fixture_id` it was called with
    and returns the canned payload. The payloads are shaped like the
    real v3 envelope inner arrays so the parsers handle them
    unchanged.
    """

    def __init__(self, fixture: dict, events: list, statistics: list, players: list) -> None:
        self._fixture = fixture
        self._events = events
        self._statistics = statistics
        self._players = players
        self.fixture_calls: list[int] = []
        self.events_calls: list[int] = []
        self.statistics_calls: list[int] = []
        self.players_calls: list[int] = []

    async def fetch_fixture(self, fixture_id: int) -> dict:
        self.fixture_calls.append(fixture_id)
        return self._fixture

    async def fetch_events(self, fixture_id: int) -> list:
        self.events_calls.append(fixture_id)
        return self._events

    async def fetch_statistics(self, fixture_id: int) -> list:
        self.statistics_calls.append(fixture_id)
        return self._statistics

    async def fetch_players(self, fixture_id: int) -> list:
        self.players_calls.append(fixture_id)
        return self._players

    async def aclose(self) -> None:
        pass


def fixture_payload() -> dict:
    """Minimal v3 fixture envelope element that `parse_fixture` accepts."""
    return {
        "fixture": {
            "id": 868019,
            "status": {"elapsed": 15, "short": "1H", "long": "First Half"},
        },
        "teams": {
            "home": {"id": 26, "name": "Argentina"},
            "away": {"id": 33, "name": "Netherlands"},
        },
        "goals": {"home": 0, "away": 0},
    }


def events_payload() -> list:
    """Minimal v3 events envelope array that `parse_events` accepts."""
    return [
        {
            "time": {"elapsed": 35, "extra": None},
            "team": {"name": "Argentina"},
            "player": {"name": "N. Molina"},
            "assist": {"name": "L. Messi"},
            "type": "Goal",
            "detail": "Normal Goal",
        }
    ]


def statistics_payload() -> list:
    """Minimal v3 statistics envelope array (two teams, all 10 stat types).

    `TeamStats` requires every field declared on the Pydantic model;
    the parser only populates fields whose stat type is in
    `STAT_TYPE_MAP`. So the payload must include all 10 stat types
    or the parser raises a ValidationError on the missing fields.
    """
    stats_block = [
        {"type": "Ball Possession", "value": "55%"},
        {"type": "Shots on Goal", "value": 3},
        {"type": "Total Shots", "value": 8},
        {"type": "Corner Kicks", "value": 4},
        {"type": "Fouls", "value": 10},
        {"type": "Offsides", "value": 1},
        {"type": "Yellow Cards", "value": 1},
        {"type": "Red Cards", "value": 0},
        {"type": "Passes Accurate", "value": "85%"},
        {"type": "Expected Goals", "value": "1.23"},
    ]
    return [
        {"team": {"name": "Argentina"}, "statistics": stats_block},
        {
            "team": {"name": "Netherlands"},
            "statistics": [{**s, "value": 0 if isinstance(v := s["value"], int) else v} for s in stats_block],
        },
    ]


def players_payload() -> list:
    """Minimal v3 players envelope array (two teams, empty rosters)."""
    return [
        {"team": {"name": "Argentina"}, "players": []},
        {"team": {"name": "Netherlands"}, "players": []},
    ]


# ---------------------------------------------------------------------------
# Requirement: DataSource Protocol (structural typing)
# ---------------------------------------------------------------------------


class TestDataSourceProtocol:
    def test_structural_typing_accepts_mock_datasource(self, mock_datasource):
        """Spec: 'DataSource structural typing'.

        A `MockDataSource` instance MUST pass `isinstance(_, DataSource)`
        even though the Protocol is structural and `MockDataSource` does
        not explicitly subclass it.
        """
        assert isinstance(mock_datasource, DataSource)

    def test_structural_typing_accepts_live_datasource(self):
        """Triangulation: a freshly-constructed `LiveDataSource` also
        passes the structural check. The Protocol is about shape, not
        inheritance.
        """
        client = FakeAPIFootballClient(
            fixture=fixture_payload(),
            events=events_payload(),
            statistics=statistics_payload(),
            players=players_payload(),
        )

        assert isinstance(LiveDataSource(client=client, fixture_id=868019), DataSource)


# ---------------------------------------------------------------------------
# Requirement: MockDataSource.get_fixture
# ---------------------------------------------------------------------------


class TestMockDataSourceGetFixture:
    async def test_get_fixture_returns_matchstate_with_fixture_id_868019(self, mock_datasource):
        """Spec: 'MockDataSource returns parsed fixture'.

        `get_fixture()` must read `fixture.json` and return a
        `MatchState` for fixture 868019.
        """
        state = await mock_datasource.get_fixture()

        assert isinstance(state, MatchState)
        assert state.fixture_id == 868019
        assert state.home.name == "Argentina"
        assert state.away.name == "Netherlands"

    async def test_get_fixture_uses_parse_fixture_path(self, mock_datasource, mock_data_dir):
        """Spec: 'Same parser path for both modes' (triangulation).

        The `MatchState` produced by `get_fixture()` MUST be byte-
        identical to the one produced by `parse_fixture()` called
        directly on the same JSON. The ONLY path to a `MatchState`
        is `parse_fixture` — no shortcuts, no fakes.

        We compare every field except `last_updated` because that
        field is set to `datetime.now()` per call and is therefore
        non-deterministic. The parser-path invariant is about the
        data fields, not the wall-clock stamp.
        """
        import json

        with open(mock_data_dir / "fixture.json", encoding="utf-8") as f:
            raw = json.load(f)["response"][0]

        from_get_fixture = await mock_datasource.get_fixture()
        from_parse_fixture = parse_fixture(raw)

        # Compare every meaningful field. last_updated is set to
        # datetime.now() per parse_fixture() call, so it cannot
        # match — we assert it's tz-aware UTC instead.
        assert from_get_fixture.fixture_id == from_parse_fixture.fixture_id
        assert from_get_fixture.status == from_parse_fixture.status
        assert from_get_fixture.home == from_parse_fixture.home
        assert from_get_fixture.away == from_parse_fixture.away
        assert from_get_fixture.events == from_parse_fixture.events == []
        assert from_get_fixture.home_stats == from_parse_fixture.home_stats is None
        assert from_get_fixture.away_stats == from_parse_fixture.away_stats is None
        assert from_get_fixture.home_players == from_parse_fixture.home_players == []
        assert from_get_fixture.away_players == from_parse_fixture.away_players == []
        assert from_get_fixture.last_updated.tzinfo is not None

    async def test_get_fixture_has_no_events_or_stats(self, mock_datasource):
        """Triangulation: `get_fixture()` returns a bare-bones MatchState.
        Events/stats/players are populated by `get_details`, not here.
        """
        state = await mock_datasource.get_fixture()

        assert state.events == []
        assert state.home_stats is None
        assert state.away_stats is None
        assert state.home_players == []
        assert state.away_players == []


# ---------------------------------------------------------------------------
# Requirement: MockDataSource.get_details (momento → file mapping)
# ---------------------------------------------------------------------------


class TestMockDataSourceGetDetails:
    async def test_momento_1_returns_minute_15_snapshot_with_empty_events(self, mock_datasource):
        """Spec: 'MockDataSource minuto 1 returns minute-15 snapshot'.

        At minute 15 no goals have been scored yet, so events are
        empty and the home/away stats are populated.
        """
        events, home_stats, away_stats, home_players, away_players = await mock_datasource.get_details(1)

        assert events == []
        assert isinstance(home_stats, TeamStats)
        assert isinstance(away_stats, TeamStats)
        assert home_stats.name == "Argentina"
        assert away_stats.name == "Netherlands"

    async def test_momento_6_includes_weghorst_90_11_equalizer(self, mock_datasource):
        """Spec: 'MockDataSource minuto 6 returns final snapshot with 90+11 equalizer'.

        The events_ft.json file must surface the Weghorst equalizer at
        minute 101 (90 + 11).
        """
        events, _, _, _, _ = await mock_datasource.get_details(6)

        assert any(
            e.minute == 101 and e.player == "W. Weghorst" and e.type == "Goal"
            for e in events
        ), f"expected Weghorst goal at minute 101, got: {[(e.minute, e.player, e.type) for e in events]}"

    async def test_momento_6_events_are_cumulative_and_chronological(self, mock_datasource):
        """Triangulation: events_ft.json is the cumulative record. The
        parser preserves input order, so the returned list must
        include Molina 35', Messi 43', Weghorst 73', and Weghorst 101
        in that order.
        """
        events, _, _, _, _ = await mock_datasource.get_details(6)

        minutes = [e.minute for e in events]
        assert minutes == [35, 43, 73, 78, 82, 101]
        assert [e.player for e in events] == [
            "N. Molina",
            "L. Messi",
            "W. Weghorst",
            "G. Montiel",
            "L. Martínez",
            "W. Weghorst",
        ]

    async def test_momento_3_returns_ht_snapshot_with_one_event(self, mock_datasource):
        """Triangulation: at HT only Molina 35' has been scored.
        Stats and players are populated.
        """
        events, home_stats, away_stats, home_players, away_players = await mock_datasource.get_details(3)

        assert len(events) == 1
        assert events[0].minute == 35
        assert events[0].player == "N. Molina"
        assert events[0].assist == "L. Messi"
        assert isinstance(home_stats, TeamStats)
        assert isinstance(away_stats, TeamStats)
        assert len(home_players) == 11
        assert len(away_players) == 11

    async def test_get_details_returns_five_tuple_in_documented_order(self, mock_datasource):
        """Triangulation: the return tuple must be exactly
        (events, home_stats, away_stats, home_players, away_players).
        Unpacking in the wrong order would silently swap Argentina and
        Netherlands.
        """
        result = await mock_datasource.get_details(6)

        assert isinstance(result, tuple)
        assert len(result) == 5
        events, home_stats, away_stats, home_players, away_players = result
        assert isinstance(events, list)
        assert isinstance(home_stats, TeamStats)
        assert isinstance(away_stats, TeamStats)
        assert isinstance(home_players, list)
        assert isinstance(away_players, list)
        assert all(isinstance(p, PlayerStats) for p in home_players)
        assert all(isinstance(p, PlayerStats) for p in away_players)

    async def test_momento_4_includes_messi_penalty_minute_43(self, mock_datasource):
        """Triangulation: the second goal is Messi's penalty at
        40+3 (minute 43). This pins the `time.elapsed + time.extra`
        arithmetic from the parser, exercised through the data
        source.
        """
        events, _, _, _, _ = await mock_datasource.get_details(4)

        assert any(e.minute == 43 and e.player == "L. Messi" and e.detail == "Penalty" for e in events)

    async def test_unknown_momento_raises_filenotfounderror(self, mock_data_dir):
        """Spec: 'MockDataSource raises on missing JSON'.

        Momento 99 has no file mapping, so the data source must raise
        `FileNotFoundError` (not return empty data silently and not
        raise a bare `KeyError`).
        """
        source = MockDataSource(mock_data_dir)

        with pytest.raises(FileNotFoundError):
            await source.get_details(99)

    async def test_load_json_warns_when_response_envelope_has_errors(self, tmp_path, caplog):
        """Triangulation: when a mock JSON has a populated `errors`
        key (the v3 envelope's API-error channel), `_load_json` must
        log a warning and STILL return the `response` array. This
        keeps mock corruption visible in CI without crashing the
        data source.
        """
        import json
        import logging

        # Build a temp mock file with both a populated `errors` key
        # AND a non-empty `response`. The data source must surface
        # the warning but return the response.
        bad_file = tmp_path / "fixture.json"
        bad_file.write_text(
            json.dumps(
                {
                    "get": "fixtures",
                    "parameters": {},
                    "errors": ["rate limit"],
                    "results": 0,
                    "paging": {"current": 1, "total": 1},
                    "response": [],
                }
            ),
            encoding="utf-8",
        )

        source = MockDataSource(tmp_path)

        with caplog.at_level(logging.WARNING, logger="backend.data_source"):
            response = source._load_json("fixture.json")

        assert response == []
        assert any("rate limit" in record.message for record in caplog.records)


# ---------------------------------------------------------------------------
# Requirement: LiveDataSource delegates to the client + parsers
# ---------------------------------------------------------------------------


class TestLiveDataSourceDelegation:
    """`LiveDataSource` is a thin adapter: it calls the
    `APIFootballClient` and pipes the result through the same parsers
    the mock source uses. These tests pin the delegation contract.
    """

    async def test_get_fixture_calls_client_fetch_fixture_with_fixture_id(self):
        """Spec: 'LiveDataSource.get_fixture delegates to client.fetch_fixture'.

        The live source MUST call the client's `fetch_fixture` with
        the `fixture_id` it was constructed with, then return the
        parsed `MatchState`.
        """
        client = FakeAPIFootballClient(
            fixture=fixture_payload(),
            events=events_payload(),
            statistics=statistics_payload(),
            players=players_payload(),
        )
        source = LiveDataSource(client=client, fixture_id=868019)

        state = await source.get_fixture()

        assert client.fixture_calls == [868019]
        assert isinstance(state, MatchState)
        assert state.fixture_id == 868019
        assert state.home.name == "Argentina"
        assert state.away.name == "Netherlands"

    async def test_get_details_calls_all_four_client_methods_with_fixture_id(self):
        """Spec: 'LiveDataSource.get_details fans out to events/statistics/players'.

        A single `get_details(momento)` call must invoke all three
        collection endpoints on the client, in the documented order,
        all with the same `fixture_id`. The returned tuple is
        (events, home_stats, away_stats, home_players, away_players).
        """
        client = FakeAPIFootballClient(
            fixture=fixture_payload(),
            events=events_payload(),
            statistics=statistics_payload(),
            players=players_payload(),
        )
        source = LiveDataSource(client=client, fixture_id=868019)

        result = await source.get_details(1)

        assert client.events_calls == [868019]
        assert client.statistics_calls == [868019]
        assert client.players_calls == [868019]
        # Tuple shape: (events, home_stats, away_stats, home_players, away_players)
        assert len(result) == 5
        events, home_stats, away_stats, home_players, away_players = result
        assert isinstance(events, list)
        assert isinstance(home_stats, TeamStats)
        assert isinstance(away_stats, TeamStats)
        assert isinstance(home_players, list)
        assert isinstance(away_players, list)

    async def test_get_details_parses_events_via_parse_events(self):
        """Triangulation: the events returned by `get_details` MUST
        be `MatchEvent` instances, parsed via the same
        `parse_events` the mock source uses. This is the
        "same parser path for both modes" invariant.
        """
        client = FakeAPIFootballClient(
            fixture=fixture_payload(),
            events=events_payload(),
            statistics=statistics_payload(),
            players=players_payload(),
        )
        source = LiveDataSource(client=client, fixture_id=868019)

        events, _, _, _, _ = await source.get_details(1)

        assert len(events) == 1
        assert isinstance(events[0], MatchEvent)
        assert events[0].minute == 35
        assert events[0].player == "N. Molina"
        assert events[0].team == "Argentina"
        assert events[0].type == "Goal"

    async def test_get_details_ignores_momento_argument(self):
        """Triangulation: `get_details` is called with `momento` but
        the live source passes only `fixture_id` to the client (the
        live API has no `momento` concept — the milestone is
        decided locally by the detector, not by the API). The
        momento argument is reserved for future use.
        """
        client = FakeAPIFootballClient(
            fixture=fixture_payload(),
            events=events_payload(),
            statistics=statistics_payload(),
            players=players_payload(),
        )
        source = LiveDataSource(client=client, fixture_id=868019)

        # Both calls must produce the same data — the live source
        # does not switch snapshots by momento.
        events_a, _, _, _, _ = await source.get_details(1)
        events_b, _, _, _, _ = await source.get_details(6)

        assert events_a == events_b
        # The client was hit twice for each endpoint — once per call.
        assert client.events_calls == [868019, 868019]


# ---------------------------------------------------------------------------
# Requirement: create_data_source factory
# ---------------------------------------------------------------------------


class TestCreateDataSourceFactory:
    def test_factory_returns_mock_datasource_in_mock_mode(self):
        """Spec: 'Factory returns MockDataSource in mock mode'.

        `Settings(MOCK_MODE=True)` (the default) must produce a
        `MockDataSource`.
        """
        from backend.config import Settings

        config = Settings(MOCK_MODE=True)

        source = create_data_source(config)

        assert isinstance(source, MockDataSource)

    def test_factory_returns_live_datasource_in_live_mode(self):
        """Spec: 'Factory returns LiveDataSource in live mode'.

        `Settings(MOCK_MODE=False, API_FOOTBALL_KEY="k", FIXTURE_ID=868019)`
        must produce a `LiveDataSource`.
        """
        config = Settings(MOCK_MODE=False, API_FOOTBALL_KEY="k", FIXTURE_ID=868019)

        source = create_data_source(config)

        assert isinstance(source, LiveDataSource)
        assert isinstance(source, DataSource)

    def test_factory_result_always_passes_structural_typing(self):
        """Triangulation: regardless of mode, the factory's return
        value MUST pass `isinstance(_, DataSource)`. This is the
        invariant the downstream router relies on.
        """
        mock_config = Settings(MOCK_MODE=True)
        live_config = Settings(MOCK_MODE=False, API_FOOTBALL_KEY="k", FIXTURE_ID=868019)

        assert isinstance(create_data_source(mock_config), DataSource)
        assert isinstance(create_data_source(live_config), DataSource)


# ---------------------------------------------------------------------------
# Requirement: Mock vs Live Mode Behavior (same parser path)
# ---------------------------------------------------------------------------


class TestMockAndLiveBehavior:
    async def test_mock_get_fixture_returned_object_is_from_parse_fixture(self, mock_datasource):
        """Spec: 'Same parser path for both modes'.

        The `MatchState` returned by `MockDataSource.get_fixture()`
        must carry the same data a `parse_fixture()` call would
        produce. We compare field-by-field because `last_updated`
        is set to `datetime.now()` per call and is non-deterministic.
        The parser-path invariant is about the data fields, not
        the wall-clock stamp.
        """
        import json

        state = await mock_datasource.get_fixture()

        # Rebuild the raw dict and parse it directly.
        with open(mock_datasource.mock_dir / "fixture.json", encoding="utf-8") as f:
            raw = json.load(f)["response"][0]

        from_parse_fixture = parse_fixture(raw)

        # Compare every field except `last_updated` (non-deterministic).
        assert state.fixture_id == from_parse_fixture.fixture_id
        assert state.status == from_parse_fixture.status
        assert state.home == from_parse_fixture.home
        assert state.away == from_parse_fixture.away
        assert state.events == from_parse_fixture.events == []
        assert state.home_stats == from_parse_fixture.home_stats is None
        assert state.away_stats == from_parse_fixture.away_stats is None
        assert state.home_players == from_parse_fixture.home_players == []
        assert state.away_players == from_parse_fixture.away_players == []


# ---------------------------------------------------------------------------
# Reusable autouse fixture: strip Settings env vars so the factory tests
# never read a stale value from the developer's shell. This is the same
# pattern used in `test_config.py`.
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _strip_settings_env(monkeypatch):
    """Prevent the host shell's env vars from contaminating `Settings`."""
    for name in (
        "API_FOOTBALL_KEY",
        "FIXTURE_ID",
        "N8N_WEBHOOK_BASE_URL",
        "MOCK_MODE",
        "POLLING_INTERVAL",
    ):
        monkeypatch.delenv(name, raising=False)
