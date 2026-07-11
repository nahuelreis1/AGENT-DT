# data-source-strategy Specification

## Purpose

Strategy pattern for match data sources. A `DataSource` Protocol defines the contract, `MockDataSource` returns data from local JSON files (replicating the API-Football v3 envelope), `LiveDataSource` delegates to `APIFootballClient` and the shared `parse_*` functions, and `create_data_source(config)` selects the right one based on `Settings.MOCK_MODE`.

## Requirements

### Requirement: DataSource Protocol

The system MUST define a `DataSource` Protocol with two async methods:
- `async get_fixture() -> MatchState` — current fixture identity (teams, score, status, no events)
- `async get_details(momento: int) -> tuple[list[MatchEvent], TeamStats | None, TeamStats | None, list[PlayerStats], list[PlayerStats]]` — detail snapshot for the given moment

The Protocol MUST be structural (any class implementing both methods with matching signatures is a `DataSource`).

#### Scenario: DataSource structural typing

- GIVEN any class implementing both async methods with the documented signatures
- WHEN `isinstance(obj, DataSource)` is checked
- THEN the check returns `True`

### Requirement: MockDataSource Loads JSON By Minute

The system MUST provide a `MockDataSource` constructed with `mock_dir: Path`. `get_fixture()` MUST read `mock_dir / "fixture.json"` and parse it via `parse_fixture`. `get_details(momento)` MUST map `momento` to a file-suffix key per the table below, then load `events_{key}.json`, `statistics_{key}.json`, and `players_{key}.json`, parse each via the shared `parse_*` functions, and return the parsed tuple in the documented order.

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

#### Scenario: MockDataSource minuto 1 returns minute-15 snapshot

- GIVEN `mock_data/events_15.json` with the goal list at minute 15
- WHEN `MockDataSource(mock_dir).get_details(momento=1)` is called
- THEN the returned events list equals the JSON content (parsed via `parse_events`)

#### Scenario: MockDataSource minuto 6 returns final snapshot with 90+11 equalizer

- GIVEN `mock_data/events_ft.json` containing both Weghorst goals
- WHEN `MockDataSource(mock_dir).get_details(momento=6)` is called
- THEN the returned events list includes a `MatchEvent(minute=101, ...)` for the 90+11 equalizer

#### Scenario: MockDataSource raises on missing JSON

- GIVEN `mock_dir` lacks `events_99.json`
- WHEN `MockDataSource(mock_dir).get_details(momento=99)` is called
- THEN a `FileNotFoundError` (or a domain error subclass) is raised

### Requirement: LiveDataSource Construction

`LiveDataSource` MUST be constructed with two positional arguments: `client: APIFootballClient` and `fixture_id: int`. The instance MUST store both and conform to the `DataSource` Protocol (both async methods implemented).

#### Scenario: Constructor accepts client and fixture_id

- GIVEN an `APIFootballClient("k")` and `fixture_id=868019`
- WHEN `LiveDataSource(client, 868019)` is constructed
- THEN the instance stores both the client and the fixture id

### Requirement: LiveDataSource get_fixture Delegates to Client and Parser

`get_fixture()` MUST call `await self._client.fetch_fixture(self._fixture_id)`, pass the returned dict (response[0]) to `parse_fixture()`, and return the resulting `MatchState`.

#### Scenario: Live mode returns a parsed MatchState

- GIVEN `client.fetch_fixture(868019)` returns the API-Football v3 response element for fixture 868019
- WHEN `await source.get_fixture()` is called
- THEN a `MatchState` is returned with `fixture_id == 868019`
- AND its `events == []`, `home_stats is None`, `away_stats is None` (parser contract)

### Requirement: LiveDataSource get_details Aggregates Three Fetches

`get_details(momento)` MUST call `await self._client.fetch_events(self._fixture_id)`, `fetch_statistics(self._fixture_id)`, and `fetch_players(self._fixture_id)`, pipe each through the matching `parse_*` function (`parse_events`, `parse_statistics`, `parse_players`), and return the 5-tuple `(events, home_stats, away_stats, home_players, away_players)` in the order documented by the `DataSource` Protocol. The `momento` argument is accepted for Protocol conformance but does not change which endpoints are hit (the API returns the cumulative snapshot).

#### Scenario: All three fetches are issued

- GIVEN `respx` mocks returning 200 for events, statistics, and players
- WHEN `await source.get_details(momento=3)` is called
- THEN the client is hit at `/fixtures/events`, `/fixtures/statistics`, and `/fixtures/players` (each exactly once)
- AND the returned tuple unpacks as `(events, home_stats, away_stats, home_players, away_players)`

### Requirement: create_data_source Factory

The system MUST expose `create_data_source(config: Settings) -> DataSource` that returns `MockDataSource(_MOCK_DATA_DIR)` when `config.MOCK_MODE is True`, and constructs `APIFootballClient(config.API_FOOTBALL_KEY)` + `LiveDataSource(client, config.FIXTURE_ID)` when `config.MOCK_MODE is False`. In both branches the returned object MUST satisfy the `DataSource` Protocol.

#### Scenario: Factory returns MockDataSource in mock mode

- GIVEN `Settings(MOCK_MODE=True, ...)` and an existing `mock_data/` directory
- WHEN `create_data_source(config)` is called
- THEN the result is a `MockDataSource` instance

#### Scenario: Factory returns LiveDataSource in live mode

- GIVEN `Settings(MOCK_MODE=False, API_FOOTBALL_KEY="k", FIXTURE_ID=868019)`
- WHEN `create_data_source(config)` is called
- THEN the result is a `LiveDataSource` instance
- AND its internal `APIFootballClient.base_url == "https://v3.football.api-sports.io/"`
- AND its internal `fixture_id == 868019`

### Requirement: Mock vs Live Mode Behavior

The data source abstraction MUST make mock and live modes behaviorally identical at the type level: both implementations return the same Pydantic models with the same fields, parsed by the same `parse_*` functions. Downstream code (`MatchStateManager`, routers) MUST NOT branch on `MOCK_MODE` — it branches only on the shape of the returned models. The ONLY difference is the origin of the data: local JSON files (mock) vs API-Football HTTP responses (live).

#### Scenario: Same parser path for both modes

- GIVEN any `DataSource` instance (mock or live)
- WHEN `await source.get_fixture()` is called
- THEN the returned object is a `MatchState` produced by `parse_fixture`

### Requirement: Mock and Live Share the Parse Path (Structural Invariant)

`LiveDataSource` MUST call the SAME `parse_fixture` / `parse_events` / `parse_statistics` / `parse_players` functions as `MockDataSource`. There MUST be no other code path that turns a v3 envelope into a `MatchState` model. This is a structural invariant — verified by static inspection of `backend/data_source.py`, not by runtime test.

#### Scenario: Live mode output is parser-seam-symmetric to mock

- GIVEN any valid `/fixtures` response element for fixture 868019
- WHEN fed through `LiveDataSource.get_fixture()` (or piped manually through `parse_fixture()`)
- THEN the resulting `MatchState` has the same field shape as `MockDataSource(mock_dir).get_fixture()` for the same fixture
