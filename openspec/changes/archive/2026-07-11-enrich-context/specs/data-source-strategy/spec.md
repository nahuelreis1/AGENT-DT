# Delta for data-source-strategy

## ADDED Requirements

### Requirement: MockDataSource Loads Lineups

`MockDataSource` MUST expose `async get_lineups() -> tuple[LineupTeam | None, LineupTeam | None]` that reads `mock_dir / "lineups.json"` and parses it via `parse_lineups`. Lineups are loaded once (not per-momento) — there is a single `lineups.json` file, unlike the per-momento `events_{key}.json` / `statistics_{key}.json` / `players_{key}.json` files. If `lineups.json` does not exist, the method MUST return `(None, None)` (graceful degradation, NOT `FileNotFoundError`) so the pre-lineup fallback path is exercisable in mock mode.

#### Scenario: MockDataSource returns parsed lineups

- GIVEN `mock_data/lineups.json` containing Argentina 4-3-3 and Netherlands 3-4-1-2 for fixture 868019
- WHEN `MockDataSource(mock_dir).get_lineups()` is called
- THEN it returns `(LineupTeam, LineupTeam)` with formations `"4-3-3"` and `"3-4-1-2"`

#### Scenario: Missing lineups.json returns (None, None)

- GIVEN `mock_dir` with no `lineups.json`
- WHEN `MockDataSource(mock_dir).get_lineups()` is called
- THEN it returns `(None, None)` (no `FileNotFoundError`)

### Requirement: LiveDataSource get_lineups Delegates to Client and Parser

`LiveDataSource` MUST expose `async get_lineups() -> tuple[LineupTeam | None, LineupTeam | None]` that calls `await self._client.fetch_lineups(self._fixture_id)`, passes the returned list to `parse_lineups()`, and returns the resulting tuple. A `fetch_lineups` result of `[]` (204 case) MUST round-trip to `(None, None)` via `parse_lineups`.

#### Scenario: Live mode returns parsed lineups

- GIVEN `client.fetch_lineups(868019)` returns the API-Football v3 lineups response array
- WHEN `await source.get_lineups()` is called
- THEN a `(LineupTeam, LineupTeam)` tuple is returned with correct formations
- AND the result was produced by `parse_lineups` (shared parser seam)

#### Scenario: Empty fetch returns (None, None)

- GIVEN `client.fetch_lineups(868019)` returns `[]` (204 pre-kickoff)
- WHEN `await source.get_lineups()` is called
- THEN it returns `(None, None)`

## MODIFIED Requirements

### Requirement: DataSource Protocol

The system MUST define a `DataSource` Protocol with three async methods:
- `async get_fixture() -> MatchState` — current fixture identity (teams, score, status, no events)
- `async get_details(momento: int) -> tuple[list[MatchEvent], TeamStats | None, TeamStats | None, list[PlayerStats], list[PlayerStats]]` — detail snapshot for the given moment
- `async get_lineups() -> tuple[LineupTeam | None, LineupTeam | None]` — team lineups (formation, starting XI, substitutes, coach); loaded once, not per-momento

The Protocol MUST be structural (any class implementing all three methods with matching signatures is a `DataSource`).
(Previously: two async methods — get_fixture and get_details; now adds get_lineups as the third)

#### Scenario: DataSource structural typing

- GIVEN any class implementing all three async methods with the documented signatures
- WHEN `isinstance(obj, DataSource)` is checked
- THEN the check returns `True`

#### Scenario: get_lineups is part of the Protocol contract

- GIVEN a class implementing `get_fixture` and `get_details` but NOT `get_lineups`
- WHEN `isinstance(obj, DataSource)` is checked
- THEN the check returns `False` (get_lineups is now required)

### Requirement: MockDataSource Loads JSON By Minute

The system MUST provide a `MockDataSource` constructed with `mock_dir: Path`. `get_fixture()` MUST read `mock_dir / "fixture.json"` and parse it via `parse_fixture`. `get_details(momento)` MUST map `momento` to a file-suffix key per the table below, then load `events_{key}.json`, `statistics_{key}.json`, and `players_{key}.json`, parse each via the shared `parse_*` functions, and return the parsed tuple in the documented order. `get_lineups()` MUST read the single `lineups.json` (see the "MockDataSource Loads Lineups" requirement).

| Momento | File key |
|---------|----------|
| 1 | `15` |
| 2 | `30` |
| 3 | `ht` |
| 4 | `60` |
| 5 | `75` |
| 6 | `ft` |

#### Scenario: MockDataSource returns parsed fixture

- GIVEN `mock_data/fixture.json` containing fixture 868019 (Argentina vs Netherlands, Qatar 2022)
- WHEN `MockDataSource(mock_dir).get_fixture()` is called
- THEN it returns a `MatchState` with `fixture_id == 868019`

#### Scenario: MockDataSource minuto 6 returns final snapshot

- GIVEN `mock_data/events_ft.json` containing both Weghorst goals
- WHEN `MockDataSource(mock_dir).get_details(momento=6)` is called
- THEN the returned events list includes a `MatchEvent(minute=101, ...)` for the 90+11 equalizer

#### Scenario: MockDataSource raises on missing per-momento JSON

- GIVEN `mock_dir` lacks `events_99.json`
- WHEN `MockDataSource(mock_dir).get_details(momento=99)` is called
- THEN a `FileNotFoundError` (or a domain error subclass) is raised

### Requirement: LiveDataSource get_details Aggregates Three Fetches

`get_details(momento)` MUST call `await self._client.fetch_events(self._fixture_id)`, `fetch_statistics(self._fixture_id)`, and `fetch_players(self._fixture_id)`, pipe each through the matching `parse_*` function, and return the 5-tuple `(events, home_stats, away_stats, home_players, away_players)`. The `momento` argument is accepted for Protocol conformance but does not change which endpoints are hit. Lineups are NOT fetched here — they are fetched once via `get_lineups()` (see the dedicated requirement).
(Previously: get_details was the only detail method; now lineups are fetched separately via get_lineups)

#### Scenario: All three fetches are issued

- GIVEN `respx` mocks returning 200 for events, statistics, and players
- WHEN `await source.get_details(momento=3)` is called
- THEN the client is hit at `/fixtures/events`, `/fixtures/statistics`, and `/fixtures/players` (each exactly once)
- AND the returned tuple unpacks as `(events, home_stats, away_stats, home_players, away_players)`

### Requirement: Mock and Live Share the Parse Path (Structural Invariant)

`LiveDataSource` MUST call the SAME `parse_fixture` / `parse_events` / `parse_statistics` / `parse_players` / `parse_lineups` functions as `MockDataSource`. There MUST be no other code path that turns a v3 envelope into a model. This is a structural invariant — verified by static inspection of `backend/data_source.py`.
(Previously: shared parse_fixture/events/statistics/players; now parse_lineups is added to the shared seam)

#### Scenario: Live mode lineups output is parser-seam-symmetric to mock

- GIVEN any valid `/fixtures/lineups` response array for fixture 868019
- WHEN fed through `LiveDataSource.get_lineups()` (or piped manually through `parse_lineups()`)
- THEN the resulting `(LineupTeam, LineupTeam)` has the same field shape as `MockDataSource(mock_dir).get_lineups()` for the same fixture
