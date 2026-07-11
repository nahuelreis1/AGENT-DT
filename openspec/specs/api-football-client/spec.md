# api-football-client Specification

## Purpose

Async `httpx` wrapper for the five API-Football v3 endpoints consumed by `LiveDataSource` (`/fixtures`, `/fixtures/events`, `/fixtures/statistics`, `/fixtures/players`, `/fixtures/lineups`). Returns raw response dicts — schema translation lives in the `api-football-parsing` parsers, not here. This class is LIVE-MODE-ONLY: the mock path does not construct it.

## Requirements

### Requirement: Client Construction

`APIFootballClient(api_key: str, base_url: str = "https://v3.football.api-sports.io/", timeout: float = 10.0)` MUST create an `httpx.AsyncClient` with header `x-apisports-key: {api_key}` injected on every request. The default base URL and timeout apply when the caller omits them.

#### Scenario: Default base URL and timeout

- GIVEN a fresh `APIFootballClient("k")`
- WHEN its internals are inspected
- THEN `base_url == "https://v3.football.api-sports.io/"`
- AND `timeout == 10.0`
- AND the `x-apisports-key` request header equals `k`

### Requirement: Fetch Methods Return Unwrapped Response Arrays

The client MUST expose five async methods. Each MUST `await self._client.get(endpoint)` with the fixture id as query string, raise on 4xx/5xx (`httpx.HTTPStatusError`) and on transport failures (`httpx.RequestError`), then return the unwrapped `response` payload from the JSON body:

| Method | Endpoint | Return |
|--------|----------|--------|
| `fetch_fixture(fixture_id)` | `/fixtures?id={id}` | `dict` (the first element of the response array) |
| `fetch_events(fixture_id)` | `/fixtures/events?fixture={id}` | `list[dict]` |
| `fetch_statistics(fixture_id)` | `/fixtures/statistics?fixture={id}` | `list[dict]` |
| `fetch_players(fixture_id)` | `/fixtures/players?fixture={id}` | `list[dict]` |
| `fetch_lineups(fixture_id)` | `/fixtures/lineups?fixture={id}` | `list[dict]` |

Every fetch method MUST increment `request_count` (including `fetch_lineups`). A 204 response (lineups not yet available) MUST be handled gracefully: the method MUST return an empty list `[]` (NOT raise) so the caller can treat it as `(None, None)` after parsing.
(Previously: four async methods; now adds fetch_lineups as the fifth)

#### Scenario: fetch_fixture returns the first response element

- GIVEN an HTTP 200 with body `{"response": [{...}, {...}], "errors": []}`
- WHEN `await client.fetch_fixture(868019)` is called
- THEN it returns the first element of the response array
- AND `request_count` has incremented by 1

#### Scenario: fetch_events returns the response list

- GIVEN an HTTP 200 with body `{"response": [event1, event2], "errors": []}`
- WHEN `await client.fetch_events(868019)` is called
- THEN it returns the list `[event1, event2]`

#### Scenario: fetch_lineups returns the response list

- GIVEN an HTTP 200 with body `{"response": [homeLineup, awayLineup], "errors": []}`
- WHEN `await client.fetch_lineups(868019)` is called
- THEN it returns the list `[homeLineup, awayLineup]`
- AND `request_count` has incremented by 1

#### Scenario: fetch_lineups 204 returns empty list without raising

- GIVEN an HTTP 204 (no content) from `/fixtures/lineups` (lineups not yet published)
- WHEN `await client.fetch_lineups(868019)` is called
- THEN it returns `[]` (no `HTTPStatusError` raised)
- AND `request_count` has incremented by 1

#### Scenario: 4xx response raises HTTPStatusError

- GIVEN an HTTP 401 from `/fixtures`
- WHEN `await client.fetch_fixture(868019)` is called
- THEN `httpx.HTTPStatusError` propagates to the caller

#### Scenario: Network failure raises RequestError

- GIVEN a connection refused on the API host
- WHEN `await client.fetch_events(868019)` is called
- THEN `httpx.RequestError` (or subclass) propagates to the caller

### Requirement: Request Counter and Quota Warnings

`request_count: int` MUST be a public read-only property reflecting the total number of HTTP calls this client instance has made (including failed ones, since the counter increments before the response is read). The client MUST emit a WARNING log line the first time `request_count` reaches 80 and another at 100. No warning is emitted below 80 or above 100.

#### Scenario: Counter increments per call

- GIVEN `request_count == 0`
- WHEN `fetch_fixture(1)` and `fetch_events(1)` complete successfully
- THEN `request_count == 2`

#### Scenario: WARNING fires exactly once at 80

- GIVEN a client that has just completed its 79th successful call
- WHEN the 80th call completes successfully
- THEN exactly one WARNING log line is emitted referencing the 80-request threshold

#### Scenario: WARNING fires at 100

- GIVEN `request_count == 99`
- WHEN the 100th call completes
- THEN a second WARNING log line is emitted referencing the 100-request threshold

### Requirement: Async Cleanup

`async aclose() -> None` MUST close the underlying `httpx.AsyncClient` and release its connection pool. The method MUST be safe to call when no requests were made.

#### Scenario: aclose on a fresh client

- GIVEN a freshly constructed `APIFootballClient("k")` with no calls made
- WHEN `await client.aclose()` is called
- THEN the call returns without exception

#### Scenario: aclose closes the underlying client

- GIVEN a client that has completed at least one request
- WHEN `await client.aclose()` is called
- THEN subsequent calls to `aclose()` do not raise
- AND no further requests can be made (the underlying transport is closed)

### Requirement: Live-Mode-Only Service

`APIFootballClient` MUST only be constructed when `Settings.MOCK_MODE is False`. The mock-mode data source path (`MockDataSource`) MUST NOT instantiate this class. Live-mode instantiation MUST succeed only when `API_FOOTBALL_KEY` is non-empty (guaranteed by `Settings` validation in change 1).
