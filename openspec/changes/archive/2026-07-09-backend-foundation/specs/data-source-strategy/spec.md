# data-source-strategy Specification

## Purpose

Strategy pattern for match data sources. A `DataSource` Protocol defines the contract, `MockDataSource` returns data from local JSON files (replicating the API-Football v3 envelope), `LiveDataSource` is the interface marker for the change 2 implementation, and `create_data_source(config)` selects the right one based on `Settings.MOCK_MODE`.

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

### Requirement: LiveDataSource Interface Stub

The system MUST define a `LiveDataSource` class that conforms to the `DataSource` Protocol. Both `get_fixture` and `get_details` MUST raise `NotImplementedError` in this change. Full implementation lands in change 2.

#### Scenario: LiveDataSource methods are not yet implemented

- GIVEN a freshly constructed `LiveDataSource(...)`
- WHEN `await source.get_fixture()` is called
- THEN `NotImplementedError` is raised

### Requirement: create_data_source Factory

The system MUST expose `create_data_source(config: Settings) -> DataSource` that returns `MockDataSource` when `config.MOCK_MODE is True` and `LiveDataSource` otherwise.

#### Scenario: Factory returns MockDataSource in mock mode

- GIVEN `Settings(MOCK_MODE=True, ...)` and an existing `mock_data/` directory
- WHEN `create_data_source(config)` is called
- THEN the result is a `MockDataSource` instance

#### Scenario: Factory returns LiveDataSource in live mode

- GIVEN `Settings(MOCK_MODE=False, API_FOOTBALL_KEY="k", FIXTURE_ID=868019)`
- WHEN `create_data_source(config)` is called
- THEN the result is a `LiveDataSource` instance

### Requirement: Mock vs Live Mode Behavior

The data source abstraction MUST make mock and live modes behaviorally identical at the type level: both implementations return the same Pydantic models with the same fields, parsed by the same `parse_*` functions. Downstream code (`MatchStateManager`, routers) MUST NOT branch on `MOCK_MODE` — it branches only on the shape of the returned models. The ONLY difference is the origin of the data: local JSON files (mock) vs API-Football HTTP responses (live).

#### Scenario: Same parser path for both modes

- GIVEN any `DataSource` instance (mock or live)
- WHEN `await source.get_fixture()` is called
- THEN the returned object is a `MatchState` produced by `parse_fixture`
