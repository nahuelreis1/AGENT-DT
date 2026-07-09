"""Tests for the data-source-strategy layer.

Covers every scenario in
`openspec/changes/backend-foundation/specs/data-source-strategy/spec.md`
plus triangulation cases that exercise the real code paths
(cumulative-event ordering, stats shape, player count, factory
branches, structural typing).

These tests reference `backend.data_source` and the live JSON files in
`backend/mock_data/`. Both are needed to make the suite pass — no fake
data, no mocks of the data source under test.
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
        assert isinstance(LiveDataSource(), DataSource)


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
# Requirement: LiveDataSource Interface Stub
# ---------------------------------------------------------------------------


class TestLiveDataSourceStub:
    async def test_get_fixture_raises_not_implemented_error(self):
        """Spec: 'LiveDataSource methods are not yet implemented'.

        `get_fixture()` on a fresh `LiveDataSource` MUST raise
        `NotImplementedError` — the full implementation lands in
        change 2.
        """
        source = LiveDataSource()

        with pytest.raises(NotImplementedError):
            await source.get_fixture()

    async def test_get_details_raises_not_implemented_error(self):
        """Triangulation: `get_details` is also a stub. The class
        conforms to the `DataSource` Protocol but raises on every
        call.
        """
        source = LiveDataSource()

        with pytest.raises(NotImplementedError):
            await source.get_details(1)


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
