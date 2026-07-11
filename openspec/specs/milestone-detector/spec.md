# milestone-detector Specification

## Purpose

Polling-tick orchestrator that fires the 6 n8n webhooks (`momento=1..6`) over the course of a match. Each moment fires AT MOST ONCE per process lifetime; before pushing, the detector fetches the full detail snapshot and updates `MatchStateManager`. The detector degrades gracefully — empty webhook URL is a no-op, n8n failures are logged and the moment is still marked fired (no retry queue).

## Requirements

### Requirement: Construction and Fired-Set Initialization

`MilestoneDetector(data_source: DataSource, match_state: MatchStateManager, n8n_url: str, http_client: httpx.AsyncClient | None = None)` MUST initialize `_fired: dict[int, bool]` with keys `1..6` all set to `False`. If `http_client is None`, the detector MUST create an internal `httpx.AsyncClient` to be closed by `aclose()`. If `http_client` is provided, the detector reuses it and MUST NOT close it on `aclose()`.

#### Scenario: All moments start unfired

- GIVEN a fresh `MilestoneDetector(mock_ds, mgr, n8n_url="")`
- WHEN `_fired` is inspected
- THEN `_fired == {1: False, 2: False, 3: False, 4: False, 5: False, 6: False}`

#### Scenario: Injected client is reused, not closed

- GIVEN `MilestoneDetector(..., http_client=external_client)`
- WHEN `await detector.aclose()` is called
- THEN `external_client.is_closed` is still `False`

### Requirement: Trigger Matrix with Status Guards

`async check_and_push() -> None` MUST iterate moments `1..6` in order. For each moment that is unfired AND whose trigger condition AND status guard are satisfied by `match_state.get_state().status`, the detector MUST (a) call `await data_source.get_details(momento)`, (b) call `match_state.update_details(...)`, (c) build the webhook payload from the updated state, (d) POST the payload, and (e) mark the moment fired regardless of POST success. The matrix is:

| M | Trigger | Status guard |
|---|---------|--------------|
| 1 | `elapsed >= 15` | `short == "1H"` |
| 2 | `elapsed >= 30` | `short in ("1H", "HT", "2H")` |
| 3 | `short == "HT"` | — |
| 4 | `elapsed >= 60` | `short in ("HT", "2H", "ET", "BT", "P", "AET", "PEN", "FT")` |
| 5 | `elapsed >= 75` | `short in ("2H", "ET", "BT", "P", "AET", "PEN", "FT")` |
| 6 | `short in ("FT", "AET", "PEN")` | — |

#### Scenario: Momento 1 fires at min 16 in 1H

- GIVEN `state.elapsed=16, state.short="1H"` and all moments unfired
- WHEN `await check_and_push()` runs
- THEN `data_source.get_details(1)` is awaited
- AND the webhook is posted once
- AND `_fired[1] is True`
- AND `_fired[2..6]` remain `False`

#### Scenario: Status guard blocks late minute-16 in 2H

- GIVEN `state.elapsed=16, state.short="2H"` and moment 1 unfired
- WHEN `await check_and_push()` runs
- THEN moment 1 does NOT fire (status guard `short == "1H"` fails)
- AND no `data_source.get_details(1)` is awaited
- AND `_fired[1] is False`

#### Scenario: Momento 6 fires exactly once at FT

- GIVEN `state.short="FT"` and all moments unfired
- WHEN `await check_and_push()` runs twice
- THEN `_fired[6] is True` after the first call
- AND the second call does not re-post (data_source.get_details(6) is awaited at most once across both calls)

#### Scenario: Multiple moments fire in the same tick when guards are satisfied

- GIVEN `state.elapsed=82, state.short="2H"` and all moments unfired
- WHEN `await check_and_push()` runs
- THEN moments 1, 2, 4, and 5 all fire (in that order)
- AND moment 3 (HT guard) and moment 6 (FT guard) do NOT fire

#### Scenario: Momento 6 fires on AET

- GIVEN `state.short="AET"`, `state.elapsed=120`, all moments unfired
- WHEN `await check_and_push()` runs
- THEN `data_source.get_details(6)` is awaited
- AND the webhook is posted once
- AND `_fired[6] is True`

#### Scenario: Momento 6 fires on PEN

- GIVEN `state.short="PEN"`, `state.elapsed=120`, all moments unfired
- WHEN `await check_and_push()` runs
- THEN `data_source.get_details(6)` is awaited
- AND the webhook is posted once
- AND `_fired[6] is True`

#### Scenario: Momento 4 fires during ET

- GIVEN `state.elapsed=95, state.short="ET"`, all moments unfired
- WHEN `await check_and_push()` runs
- THEN `data_source.get_details(4)` is awaited
- AND `_fired[4] is True`

#### Scenario: Momento 5 fires during ET

- GIVEN `state.elapsed=105, state.short="ET"`, all moments unfired
- WHEN `await check_and_push()` runs
- THEN `data_source.get_details(5)` is awaited
- AND `_fired[5] is True`

### Requirement: Webhook Payload Shape and Endpoint

The POST body MUST be `{"momento": N, "context_text": str, "match_state": dict}` where `context_text = match_state.get_context_text()` and `match_state = match_state.get_state().model_dump(mode="json")`. The URL MUST be `{n8n_url}/webhook/momento` (path suffix `/webhook/momento` is fixed). The request MUST use `timeout=5.0` seconds.

#### Scenario: Payload shape is momento + context_text + JSON-serialized state

- GIVEN a populated state and moment 3 about to fire
- WHEN the POST body is built
- THEN `body["momento"] == 3`
- AND `isinstance(body["context_text"], str)` and `len(body["context_text"]) > 0`
- AND `body["match_state"]` is a dict containing the keys `home`, `away`, `events`, `status`, `fixture_id`

#### Scenario: URL is {n8n_url}/webhook/momento

- GIVEN `n8n_url="https://n8n.example.com"`
- WHEN moment 1 fires
- THEN the POST URL is `https://n8n.example.com/webhook/momento`

### Requirement: Log-and-Continue on Failure

If `n8n_url` is the empty string, the detector MUST NOT post and MUST emit exactly one `log.info(...)` per `check_and_push()` call describing the skip. If the POST raises (timeout, 4xx/5xx, network error), the detector MUST emit `log.error(...)` with the error, mark the moment fired, and continue to the next moment. There is no retry queue and no exponential backoff.

#### Scenario: Empty n8n_url is a no-op with info log

- GIVEN `n8n_url=""` and moment 1's trigger satisfied
- WHEN `await check_and_push()` runs
- THEN zero HTTP requests are made
- AND one `log.info` line is emitted mentioning `N8N_WEBHOOK_BASE_URL` is empty
- AND `_fired[1] is False` (moment 1 was NEVER fired — the trigger was satisfied but the push was skipped, so a future tick with n8n configured COULD still fire it)

#### Scenario: POST failure marks fired without retry

- GIVEN `n8n_url="https://n8n.invalid"` and the post returns connection refused
- WHEN `await check_and_push()` runs
- THEN one `log.error` line is emitted referencing the failed POST
- AND `_fired[1] is True`
- AND a second call to `check_and_push()` does NOT re-attempt moment 1 (`_fired[1]` is still `True`)

#### Scenario: One moment's failure does not block the next

- GIVEN `n8n_url` returns 500 for moment 2 and 200 for moment 4, with all triggers satisfied for moments 1, 2, 4
- WHEN `await check_and_push()` runs
- THEN moments 1, 2, and 4 all mark fired by the end
- AND moment 2's 500 produced a `log.error` but did not halt iteration

### Requirement: Async Cleanup

`async aclose() -> None` MUST close the internal `httpx.AsyncClient` if one was created (i.e. when `http_client is None` at construction). When an `http_client` was injected, `aclose()` MUST be a no-op for the injected client (caller owns its lifecycle).

#### Scenario: aclose closes internal client

- GIVEN a detector constructed without an injected `http_client`
- WHEN `await detector.aclose()` is called
- THEN the detector's internal client is closed

#### Scenario: aclose is safe to call after a tick

- GIVEN a detector that has just completed `check_and_push()` with no failures
- WHEN `await detector.aclose()` is called
- THEN the call returns without exception
