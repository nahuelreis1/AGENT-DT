# Delta for data-source-strategy

## REMOVED Requirements

### Requirement: LiveDataSource Interface Stub

(Reason: The stub is fully implemented in this change. The `LiveDataSource` class now constructs with an `APIFootballClient` and a `fixture_id`, calls the client on `get_fixture()` / `get_details(momento)`, and routes responses through the shared `parse_*` parsers. The "NotImplementedError" scenario is no longer accurate. See the ADDED requirements for the new behavior and the MODIFIED `create_data_source` factory wiring.)

## ADDED Requirements

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

### Requirement: Mock and Live Share the Parse Path (Structural Invariant)

`LiveDataSource` MUST call the SAME `parse_fixture` / `parse_events` / `parse_statistics` / `parse_players` functions as `MockDataSource`. There MUST be no other code path that turns a v3 envelope into a `MatchState` model. This is a structural invariant — verified by static inspection of `backend/data_source.py`, not by runtime test.

#### Scenario: Live mode output is parser-seam-symmetric to mock

- GIVEN any valid `/fixtures` response element for fixture 868019
- WHEN fed through `LiveDataSource.get_fixture()` (or piped manually through `parse_fixture()`)
- THEN the resulting `MatchState` has the same field shape as `MockDataSource(mock_dir).get_fixture()` for the same fixture

## MODIFIED Requirements

### Requirement: create_data_source Factory

The system MUST expose `create_data_source(config: Settings) -> DataSource` that returns `MockDataSource(_MOCK_DATA_DIR)` when `config.MOCK_MODE is True`, and constructs `APIFootballClient(config.API_FOOTBALL_KEY)` + `LiveDataSource(client, config.FIXTURE_ID)` when `config.MOCK_MODE is False`. In both branches the returned object MUST satisfy the `DataSource` Protocol.
(Previously: live mode returned an unconfigured `LiveDataSource()` stub — the factory now wires the client and fixture id.)

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
