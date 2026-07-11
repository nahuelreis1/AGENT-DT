# Proposal: Backend Services

## Intent

The backend has no service layer. `LiveDataSource` raises `NotImplementedError`, there is no in-memory match state, no milestone orchestration, and the deferred `context-text-format` spec is unimplemented. This change introduces the service layer: `MatchStateManager` + `get_context_text()`, `APIFootballClient` (async httpx + request tracking), the filled-in `LiveDataSource`, and `MilestoneDetector` (6 triggers → n8n webhooks). Change 3 (HTTP API + polling loop) has no business logic to wire up without these.

## Scope

### In Scope
- `backend/services/__init__.py` — package marker.
- `backend/services/match_state.py` — `MatchStateManager`, `PERIOD_NAMES`, `get_context_text()`, score reconciliation, prediction store.
- `backend/services/api_football.py` — `APIFootballClient` (async httpx, 4 fetch methods, `request_count`, warning logs at 80/100).
- `backend/services/milestones.py` — `MilestoneDetector` (6 triggers, fetch details before push, log-and-continue on n8n failure).
- `backend/data_source.py` — `LiveDataSource.__init__(client, fixture_id)`, stubs filled, delegates to `parse_*` + `APIFootballClient`. `create_data_source()` updated for live mode.
- `backend/tests/test_match_state.py` — unit tests + `get_context_text` snapshot test.
- `backend/tests/test_api_football.py` — integration tests with `respx`.
- `backend/tests/test_milestones.py` — unit tests with `respx` for n8n webhook.
- `openspec/specs/context-text-format/spec.md` — synced from archive (deferred from change 1, now active).

### Out of Scope (change 3 — backend-api)
- `routers/partido.py` — REST endpoints.
- `main.py` — FastAPI app, lifespan, polling loop.
- HTTP wiring for `save_prediction` / `get_predictions`.
- `/mock/avanzar`, `/stats/requests`, `/health` endpoints.

## Capabilities

> CONTRACT for sdd-spec. Research of `openspec/specs/` complete (4 specs in place from change 1).

### New Capabilities
- `match-state-manager`: in-memory `MatchState` lifecycle, `get_context_text()` text format, score reconciliation from Goal events, prediction append/read.
- `api-football-client`: async httpx wrapper for API-Football v3, 4 fetch methods, request tracking, header injection.
- `milestone-detector`: 6-trigger matrix with status guards, details fetch before push, n8n webhook delivery with log-and-continue.

### Modified Capabilities
- `data-source-strategy`: `LiveDataSource` is no longer a stub — accepts `APIFootballClient` + `fixture_id`, delegates to `parse_*` functions. The "NotImplementedError" scenario in the existing spec is OBSOLETE; spec needs delta to remove it.
- `context-text-format`: synced from `openspec/changes/archive/2026-07-09-backend-foundation/specs/context-text-format/spec.md` (was deferred in change 1, now active). No content changes — same 7-section contract.

## Approach

**Score reconciliation (Option A, user-confirmed):** `MatchStateManager.update_details()` recomputes `home.goals` and `away.goals` by counting `Goal` events per team from the cumulative events list. This OVERRIDES whatever `update_fixture()` set from the API's `goals` field. Why: the API `goals` field is incremental (set by `/fixtures`), while the events list is the cumulative ground truth. This makes mock mode work correctly: min 15 (empty events) → 0-0, HT (1 Goal: Molina) → 1-0, FT (4 Goals: Molina + Messi pen + Weghorst×2) → 2-2.

**Layering — single parsing path preserved:** `APIFootballClient` returns raw dicts (NOT Pydantic). `LiveDataSource` calls the client and pipes dicts into the existing `parse_*` functions from change 1. The "mock and live share parsing" invariant is structural, not aspirational.

**Milestone trigger matrix (FLAGGED per `openspec/config.yaml` rule "Flag any change that alters the 6 milestone triggers" — this change IMPLEMENTS them; any future alteration MUST be re-flagged in that change's proposal):**

| Momento | Trigger condition | Status guard |
|---------|-------------------|--------------|
| 1 | `elapsed >= 15` | `short == "1H"` |
| 2 | `elapsed >= 30` | `short in ("1H", "HT", "2H")` |
| 3 | `short == "HT"` | — |
| 4 | `elapsed >= 60` | `short in ("HT", "2H", "FT")` |
| 5 | `elapsed >= 75` | `short in ("2H", "FT")` |
| 6 | `short == "FT"` | — |

Status guards ensure a polling tick at min 16 in the 2H (after a delayed poll) does NOT retroactively fire momento 1.

**Webhook payload (DOCUMENTED per `openspec/config.yaml` rule "Document the exact webhook payload pushed to n8n for each milestone" — payload shape is identical across momento 1-6; only `momento`, `context_text`, and `match_state` values change):**

```json
{
  "momento": 1,
  "context_text": "⚽ Argentina 0 - 0 Holanda | Minuto 15 | 1er Tiempo\n\n...",
  "match_state": { "...full Pydantic as JSON via model_dump(mode='json')..." }
}
```

POST to `{N8N_WEBHOOK_BASE_URL}/momento` (or `/webhook/momento` per the n8n README convention — design phase will pick one and document). Timeout: 5.0s.

**Log-and-continue on n8n failure:** if `n8n_url` is empty (mock mode) → no-op with `log.info(...)`. If POST fails or times out → `log.error(...)`, mark fired anyway (no retry queue). Protects the polling loop from a broken n8n and prevents the same milestone from re-firing every 90 seconds.

**`get_context_text()` period names (from archived spec, applied here):** `PERIOD_NAMES = {"1H": "1er Tiempo", "HT": "Entretiempo", "2H": "2do Tiempo", "FT": "Final"}`. Team abbreviation: first 3 letters uppercased (Argentina→ARG); fallback to full name uppercased if length < 3. Standout players: `rating >= 7.0`, top 3, sorted descending. Weak players: `0 < rating < 6.5`, top 2, sorted ascending. Rating parsed as `float(p.rating or 0)` — handles empty string. Penalty: `"Penalty" in event.detail` → format as `(pen {minute}')`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/services/__init__.py` | New | Package marker |
| `backend/services/match_state.py` | New | State + context text + reconciliation + prediction store |
| `backend/services/api_football.py` | New | httpx async client + request tracking |
| `backend/services/milestones.py` | New | 6-trigger matrix + n8n push |
| `backend/data_source.py` | Modified | `LiveDataSource` stubs filled; `create_data_source()` wires client for live mode |
| `backend/tests/test_match_state.py` | New | Unit + snapshot test |
| `backend/tests/test_api_football.py` | New | `respx` integration tests |
| `backend/tests/test_milestones.py` | New | `respx` + asyncio unit tests |
| `openspec/specs/context-text-format/spec.md` | Synced | Was deferred in change 1; active now (no content change) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Live API returns ALL events cumulative, not per-momento | Med | `LiveDataSource.get_details(momento)` returns the cumulative snapshot at that threshold (same contract as `MockDataSource` — design phase documents the semantic). Mock and live share the per-momento boundary. |
| `rating` field is a string; may be empty or `None` | Med | Parse as `float(p.rating or 0)`; guards empty string. Snapshot test covers 0-rating edge case. |
| Empty `n8n_url` in mock mode → silent skip of all pushes | Low | Explicit `log.info("milestone push skipped: N8N_WEBHOOK_BASE_URL is empty")`; test asserts no exception. |
| Score drift between API `goals` field and cumulative event count | Low (resolved) | `update_details()` recomputes from events (Option A). `update_fixture()` sets the API value as a placeholder until first `update_details()`. |
| `_fired` dict state lost on process restart (re-fires all 6) | Low | Single-process backend; documented as known limitation. Mitigation: clear on startup if `MATCH_RESTART=True` env var. Not blocking change 3. |
| Free-tier API quota exhaustion (100 req/day) | Med | `APIFootballClient` logs WARNING at 80 and 100 requests (per `implementation_plan.md` optimization). Polling interval defaults to 90s (~81 req/match). |

## Rollback Plan

This change adds 4 files, modifies 1, and syncs 1 spec. Rollback = `git revert` the merge commit.

1. **No new external dependencies introduced** — `httpx` and `respx` are already in `requirements-dev.txt` from change 1.
2. **No migration** — no DB or filesystem state to roll back.
3. **`LiveDataSource` reverts to stub** — after revert, `create_data_source(MOCK_MODE=False)` returns a stub that raises `NotImplementedError`. The factory still works in mock mode; live mode is non-functional until re-merged.
4. **`context-text-format` spec reverts to deferred state** — change 1's archived spec remains the source of truth.

**Downstream dependency on change 3:** `MatchStateManager`, `APIFootballClient`, and `MilestoneDetector` are NOT consumed by any HTTP route yet. Change 3 wires them into `routers/partido.py` and `main.py`. If change 3 ships with production blockers, the service layer from this change is still independently testable from REPL/CLI and the polling loop is not entangled with HTTP wiring.

**Chained PR strategy (2 PRs to `main`, within 400-line review budget per the sdd-phase-common review workload guard):**
- **PR 1 (~500 LOC):** `services/match_state.py` + `tests/test_match_state.py`. Pure logic, no I/O. Snapshot test pins the 7-section `get_context_text()` format. Land and review first.
- **PR 2 (~700 LOC):** `services/api_football.py` + `services/milestones.py` + `data_source.py` modification + `tests/test_api_football.py` + `tests/test_milestones.py`. Orchestration with httpx + respx. Targets the same base branch; rebase if PR 1 is not yet merged.

## Dependencies

**From change 1 (shipped):** `Settings` (config), `MatchState` / `MatchEvent` / `PlayerStats` / `TeamStats` / `Prediction` (models), `parse_fixture` / `parse_events` / `parse_statistics` / `parse_players` (parsers), `DataSource` Protocol, `MockDataSource`, `create_data_source` factory, `MOMENTO_FILE_KEYS` map.

**From external libs (already in `requirements.txt` / `requirements-dev.txt`):** `httpx` (async HTTP), `respx` (httpx mocking for tests).

**Enables change 3 (backend-api):**
- `routers/partido.py` will import `MatchStateManager.get_state()`, `.get_context_text()`, `.save_prediction()`, `.get_predictions()`.
- `main.py` will instantiate `APIFootballClient(Settings())` and `MilestoneDetector(data_source, match_state, n8n_url, http_client)`, and call `await detector.check_and_push()` from the polling loop.
- `create_data_source()` in live mode now wires `APIFootballClient` + `fixture_id` into `LiveDataSource` — change 3 just calls the factory with the existing `Settings`.

## Success Criteria

- [ ] `cd backend && pytest` passes; ≥70% coverage on new modules (`services/`, `data_source.py`); all change 1 tests still green.
- [ ] `get_context_text()` snapshot test is byte-identical to the archived spec example for the minute-67 scenario.
- [ ] `MatchStateManager.update_details()` produces `0-0` at min 15 (using `events_15.json`) and `2-2` at FT (using `events_ft.json`) — verified by unit test.
- [ ] `APIFootballClient` raises `httpx.HTTPStatusError` on 4xx/5xx and `httpx.RequestError` on network failure — verified by `respx` mocks.
- [ ] `MilestoneDetector.check_and_push()` fires each of the 6 momenti at most once across the full match timeline and survives n8n being unreachable — verified by `respx` + asyncio tests.
- [ ] `LiveDataSource.get_fixture()` and `get_details()` no longer raise `NotImplementedError`; both route through the same `parse_*` functions as `MockDataSource` (verified by inspecting a `respx`-mocked response feeding a live source returning a valid `MatchState`).
- [ ] `data-source-strategy` spec is updated: the "NotImplementedError" scenario is marked OBSOLETE.
- [ ] No new third-party dependencies added to `requirements.txt` or `requirements-dev.txt`.
