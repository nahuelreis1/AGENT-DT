# Delta for api-football-client

## MODIFIED Requirements

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
