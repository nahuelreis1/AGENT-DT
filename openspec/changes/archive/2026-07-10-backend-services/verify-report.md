# Verify Report: backend-services

**Status:** PASS
**Verdict:** APPROVED
**Date:** 2026-07-09
**Strict TDD:** ACTIVE (hybrid mode, OpenSpec + Engram)

---

## Executive Summary

The `backend-services` change (change 2 of 3) is **complete and verified**. All 163 tests pass on the first run with 99.54% line coverage (target was 70%). The implementation matches the proposal, the design, the four delta specs, the synced `context-text-format` spec, and all 26 tasks in `tasks.md`.

The work split into two stacked PRs as planned:
- **PR 1 (pure logic, ~490 LOC):** `MatchStateManager` + `get_context_text()` + prediction log + snapshot test.
- **PR 2 (orchestration, ~700 LOC):** `APIFootballClient` + `LiveDataSource` filling + `MilestoneDetector` + factory + tests.

The TDD RED→GREEN→TRIANGULATE→REFACTOR cycle is visible in the commit log (e.g. `b31b0aa test…(RED)` → `92a4888 feat…(GREEN)` → `6693462 chore…(REFACTOR)`), and the verification surface — assertions, snapshot, caplog on quota warnings, respx on webhooks — is behaviorally rich, not a smoke test.

A previous revision removed the obsolete `TestLiveDataSourceStub` (2 tests) and replaced it with 4 delegation tests in `TestLiveDataSourceDelegation`. The NotImplementedError path is gone from the production code, the spec marks the scenario OBSOLETE, and the test that pinned the old contract is gone.

The only "miss" in coverage is the `emoji = "?"` defensive fallback for cards that have neither "Yellow" nor "Red" in `detail` (line 275 of `match_state.py`) — and the `FakeAPIFootballClient.aclose` no-op (line 76 of `test_data_source.py`). Both are genuinely defensive code with no realistic input path; not blocking.

---

## Test Results

| Metric | Expected | Actual | Result |
|---|---|---|---|
| Tests collected | 163 | 163 | ✅ |
| Tests passed | 163 | 163 | ✅ |
| Tests failed | 0 | 0 | ✅ |
| Tests errored | 0 | 0 | ✅ |
| Warnings | 0 | 0 | ✅ |
| Coverage (overall) | ≥ 70% | 99.54% | ✅ |
| Coverage (services/match_state.py) | ≥ 70% | 99% (129/130) | ✅ |
| Coverage (services/api_football.py) | ≥ 70% | 100% (30/30) | ✅ |
| Coverage (services/milestones.py) | ≥ 70% | 100% (40/40) | ✅ |
| Coverage (data_source.py) | ≥ 70% | 100% (53/53) | ✅ |
| Test command exit code | 0 | 0 | ✅ |

**Missing lines (1 each, both defensive):**
- `backend/services/match_state.py:275` — `else: emoji = "?"` in `_cards_section._fmt` for card events with neither Yellow nor Red in detail. Pydantic `MatchEvent.type` accepts `"Card"` but `detail` is free text; no spec scenario produces this branch.
- `backend/tests/test_data_source.py:76` — `async def aclose(self) -> None: pass` in the `FakeAPIFootballClient` test helper. Unused because the live source test never calls `aclose` on the fake.

**Command evidence:**
```
$ cd backend && python -m pytest -v --tb=short
============================= test session starts =============================
configfile: pyproject.toml
plugins: anyio-4.13.0, asyncio-1.4.0, cov-7.1.0, respx-0.23.1
asyncio: mode=Mode.AUTO
collecting ... collected 163 items
...
============================ 163 passed in 13.01s =============================
Required test coverage of 70% reached. Total coverage: 99.54%
```

---

## Proposal Success Criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | `cd backend && pytest` passes; ≥70% coverage on new modules; all change 1 tests still green | ✅ | 163/163 passed, 99.54% coverage; all 33 change 1 tests (test_config, test_models, test_parsers) green |
| 2 | `get_context_text()` snapshot test byte-identical to archived spec example for minute-67 | ✅ | `test_snapshot_at_minute_67_matches_pinned_format` asserts full byte-exact string with all 7 sections |
| 3 | `update_details()` produces 0-0 at min 15 and 2-2 at FT | ✅ | `test_update_details_with_empty_events_yields_0_0_even_if_fixture_set_2_2` + `test_update_details_with_four_goal_events_split_2_2_overrides_api_score` |
| 4 | `APIFootballClient` raises `HTTPStatusError` on 4xx/5xx and `RequestError` on network | ✅ | `test_4xx_response_raises_http_status_error` + `test_5xx_response_raises_http_status_error` + `test_network_error_raises_request_error` |
| 5 | `MilestoneDetector.check_and_push()` fires each of 6 momenti at most once and survives n8n unreachable | ✅ | `test_all_six_momenti_fire_across_full_match_timeline` (m=1..6 each fire once) + `test_post_exception_marks_fired_and_continues` (n8n raises ConnectError, _fired still True) |
| 6 | `LiveDataSource.get_fixture()` and `get_details()` no longer raise `NotImplementedError`; both route through same `parse_*` functions | ✅ | `grep NotImplementedError backend/` returns 0 matches; `data_source.py:152-171` calls `parse_fixture`/`parse_events`/`parse_statistics`/`parse_players` |
| 7 | `data-source-strategy` spec updated: `NotImplementedError` scenario marked OBSOLETE | ✅ | `openspec/changes/backend-services/specs/data-source-strategy/spec.md` has "REMOVED Requirements" section removing `LiveDataSource Interface Stub`; obsolete `TestLiveDataSourceStub` deleted in commit `3534fe6` |
| 8 | No new third-party dependencies added | ✅ | `requirements.txt` unchanged (5 lines: fastapi, uvicorn, httpx, pydantic, pydantic-settings); `requirements-dev.txt` unchanged (4 lines: pytest, pytest-asyncio, pytest-cov, respx) — both match change 1 state |

**All 8 success criteria met.**

---

## Design Compliance

| # | Decision | Status | Evidence |
|---|---|---|---|
| 1 | State holder = plain `MatchStateManager` (no singleton) | ✅ | `match_state.py:60-70` — no metaclass, no `__new__` override, no global; tests construct `MatchStateManager()` directly |
| 2 | Score source of truth = recompute from `Goal` events in `update_details` (Option A) | ✅ | `match_state.py:109-119` — counts `e.type == "Goal" and e.team == home_name` after copying events, overriding whatever `update_fixture` set |
| 3 | Live source DI = `LiveDataSource(client, fixture_id)` — injected, no client ownership | ✅ | `data_source.py:148-150` stores both; `aclose` only lives on `APIFootballClient` (owned by the factory or detector, not by `LiveDataSource`) |
| 4 | `request_count` increments BEFORE the HTTP call | ✅ | `api_football.py:77-83` — counter increments on line 77, `await self._client.get(...)` is on line 83; warnings fire on the incremented value before the request completes |
| 5 | `fetch_fixture` return = `dict` (response[0]); `{}` on empty | ✅ | `api_football.py:95-96` — `return resp[0] if resp else {}` |
| 6 | `MilestoneDetector` HTTP = owns client unless injected | ✅ | `milestones.py:92-94` — `self._http = http_client or httpx.AsyncClient(timeout=5.0)`; `self._owns_http = http_client is None` |
| 7 | Trigger matrix = `list[tuple[int, callable, callable]]` | ✅ | `milestones.py:52-71` — exactly 6 entries, each `(int, lambda, lambda)`; iterated in `check_and_push` |
| 8 | Fetch details BEFORE `update_details` | ✅ | `milestones.py:119-124` — `await self._data_source.get_details(momento)` returns 5-tuple, then `self._match_state.update_details(...)` |
| 9 | Mark fired on POST fail (no retry) | ✅ | `milestones.py:131-132` — `_push` is wrapped in try/except, but `_fired[momento] = True` runs unconditionally after the try |
| 10 | Empty `n8n_url` = no-op with `log.info`, leave unfired | ✅ | `milestones.py:110-112` — early return, `_fired[1]` remains False (test verifies) |
| 11 | POST exception scope = `except Exception` | ✅ | `milestones.py:143` — `except Exception as e:` (catches serialization errors too) |
| 12 | Snapshot test = byte-pinned at min 67 | ✅ | `test_match_state.py:856-990` — full byte-exact `assert text == expected` with 19 lines of pinned string |
| 13 | PR split (400-line budget) | ✅ | Two stacked PRs to main: PR1 = match_state only, PR2 = api_football + milestones + data_source |

**All 13 design decisions match.**

---

## Spec Coverage Matrix

### match-state-manager spec (10 scenarios)

| Scenario | Test | Status |
|---|---|---|
| Uninitialized state raises on `get_state` | `test_get_state_before_update_fixture_raises_runtime_error` | ✅ |
| Fixture update makes state readable | `test_update_fixture_makes_state_readable` | ✅ |
| Min 15 with empty events yields 0-0 | `test_update_details_with_empty_events_yields_0_0_even_if_fixture_set_2_2` | ✅ |
| 4 Goal events split 2-2 override API score | `test_update_details_with_four_goal_events_split_2_2_overrides_api_score` | ✅ |
| Reconciliation is idempotent | `test_update_details_reconciliation_is_idempotent` | ✅ |
| Snapshot at minute 67 matches the pinned format | `test_snapshot_at_minute_67_matches_pinned_format` | ✅ |
| Pre-kickoff uses every empty-section variant | `test_pre_kickoff_uses_every_empty_section_variant` | ✅ |
| Save then read round-trips | `test_save_prediction_round_trips` | ✅ |
| Predictions preserve append order | `test_predictions_preserve_append_order` | ✅ |
| Out-of-range momento is rejected | `test_save_prediction_momento_above_six_raises_value_error` | ✅ |

**10/10 covered.**

### api-football-client spec (12 scenarios)

| Scenario | Test | Status |
|---|---|---|
| Default base URL and timeout | `test_request_count_starts_at_zero` + all tests using `respx` matching `https://v3.football.api-sports.io/` | ✅ |
| `fetch_fixture` returns the first response element | `test_fetch_fixture_returns_first_element_of_response` | ✅ |
| `fetch_fixture` with empty response returns `{}` | `test_fetch_fixture_with_empty_response_returns_empty_dict` | ✅ |
| `fetch_events` returns the response list | `test_fetch_events_returns_full_response_list` | ✅ |
| `fetch_statistics` returns the response list | `test_fetch_statistics_returns_full_response_list` | ✅ |
| `fetch_players` returns the response list | `test_fetch_players_returns_full_response_list` | ✅ |
| 4xx response raises `HTTPStatusError` | `test_4xx_response_raises_http_status_error` | ✅ |
| 5xx response raises `HTTPStatusError` | `test_5xx_response_raises_http_status_error` | ✅ |
| Network failure raises `RequestError` | `test_network_error_raises_request_error` | ✅ |
| Counter increments per call | `test_request_count_increments_per_call` | ✅ |
| WARNING fires at 80 and 100 | `test_warning_logged_at_request_80_and_100` | ✅ |
| `aclose` is safe and closes client | `test_aclose_closes_client` | ✅ |

**12/12 covered.**

### milestone-detector spec (13 scenarios)

| Scenario | Test | Status |
|---|---|---|
| All moments start unfired | `test_empty_n8n_url_is_a_no_op` (asserts `{i: False for i in range(1, 7)}`) | ✅ |
| Injected client is reused, not closed | `test_injected_http_client_is_not_closed_by_aclose` | ✅ |
| Momento 1 fires at elapsed≥15, short==1H | `test_trigger_1_fires_at_minute_15_first_half` | ✅ |
| Status guard blocks late minute-16 in 2H | `test_trigger_1_does_not_fire_at_ft_despite_elapsed_above_15` | ✅ |
| Momento 6 fires exactly once at FT | `test_trigger_6_fires_at_ft` + `test_trigger_does_not_re_fire_on_second_check` | ✅ |
| Multiple moments fire in the same tick (m=1,2,4,5 at 82'/2H) | `test_all_six_momenti_fire_across_full_match_timeline` | ✅ |
| Payload shape = momento + context_text + match_state | `test_payload_has_momento_context_text_and_match_state` | ✅ |
| URL = `{n8n_url}/webhook/momento` | `test_payload_has_momento_context_text_and_match_state` (respx route pinned) | ✅ |
| Empty `n8n_url` = no-op + info log | `test_empty_n8n_url_is_a_no_op` | ✅ |
| POST failure marks fired without retry | `test_post_exception_marks_fired_and_continues` + `test_5xx_response_does_not_crash_or_retry` | ✅ |
| One moment's failure does not block the next | `test_post_exception_marks_fired_and_continues` (m=2 and m=4 both fire despite ConnectError) | ✅ |
| `aclose` closes internal client | `test_owned_http_client_is_closed_by_aclose` | ✅ |
| `aclose` is safe after a tick | `test_owned_http_client_is_closed_by_aclose` (after `check_and_push`) | ✅ |

**13/13 covered.**

### data-source-strategy spec (DELTA — 7 scenarios)

| Scenario | Test | Status |
|---|---|---|
| Constructor accepts client and fixture_id | `test_factory_returns_live_datasource_in_live_mode` (passes them via factory) + `test_structural_typing_accepts_live_datasource` | ✅ |
| Live mode returns a parsed MatchState | `test_get_fixture_calls_client_fetch_fixture_with_fixture_id` | ✅ |
| All three fetches are issued (events, statistics, players) | `test_get_details_calls_all_four_client_methods_with_fixture_id` | ✅ |
| Live mode output is parser-seam-symmetric to mock | `test_mock_get_fixture_returned_object_is_from_parse_fixture` (structural invariant verified by field-by-field comparison) | ✅ |
| Factory returns MockDataSource in mock mode | `test_factory_returns_mock_datasource_in_mock_mode` | ✅ |
| Factory returns LiveDataSource in live mode | `test_factory_returns_live_datasource_in_live_mode` | ✅ |
| `NotImplementedError` scenario is OBSOLETE | `grep NotImplementedError backend/` → 0 matches; `TestLiveDataSourceStub` deleted in commit `3534fe6`; spec has REMOVED Requirements section | ✅ |

**7/7 covered.**

### context-text-format spec (synced — 2 requirements)

| Requirement | Test | Status |
|---|---|---|
| File exists at `openspec/specs/context-text-format/spec.md` | `ls openspec/specs/context-text-format/spec.md` (file present, byte-identical to archived source) | ✅ |
| Snapshot test pins the format at minute 67 | `test_snapshot_at_minute_67_matches_pinned_format` (full byte-exact assert, 19 lines) | ✅ |

**2/2 covered.**

**Total: 44 spec scenarios, 44 covered. No UNTESTED, no FAILING.**

---

## Score Reconciliation Audit

The critical `update_details` invariant: events list is the ground truth, the API's `goals` field is incremental and overridden.

| Step | Input | Expected score | Test | Status |
|---|---|---|---|---|
| `update_fixture` with API score 2-2 | fixture set 2-2 | 2-2 (placeholder) | setup | ✅ |
| `update_details(events=[], ...)` | 0 events | 0-0 | `test_update_details_with_empty_events_yields_0_0_even_if_fixture_set_2_2` | ✅ |
| `update_details(events=[Molina 35' Goal], ...)` | 1 home goal | 1-0 | `test_update_details_with_one_home_goal_event_recomputes_to_1_0` | ✅ |
| `update_details(events=[Molina, Messi pen, Weghorst, Weghorst 101], ...)` | 4 goals split | 2-2 (overriding API's 1-1) | `test_update_details_with_four_goal_events_split_2_2_overrides_api_score` | ✅ |
| Idempotency: same input twice | score unchanged | unchanged | `test_update_details_reconciliation_is_idempotent` | ✅ |

**Score reconciliation works exactly as specified.**

---

## Trigger Matrix Audit

| M | Condition | Guard | Spec test | Status |
|---|---|---|---|---|
| 1 | `elapsed >= 15` | `short == "1H"` | `test_trigger_1_fires_at_minute_15_first_half` + `test_trigger_1_does_not_fire_at_ft_despite_elapsed_above_15` | ✅ |
| 2 | `elapsed >= 30` | `short in ("1H", "HT", "2H")` | `test_trigger_2_fires_at_minute_30_second_half` + `test_trigger_2_does_not_fire_at_ft` | ✅ |
| 3 | `short == "HT"` | (always) | `test_trigger_3_fires_at_ht` | ✅ |
| 4 | `elapsed >= 60` | `short in ("HT", "2H", "FT")` | `test_trigger_4_fires_at_minute_60` (asserts m=4 present, m=2 superset also present) | ✅ |
| 5 | `elapsed >= 75` | `short in ("2H", "FT")` | `test_trigger_5_fires_at_minute_75` | ✅ |
| 6 | `short == "FT"` | (always) | `test_trigger_6_fires_at_ft` + full-timeline test | ✅ |

**Full timeline simulation:** `test_all_six_momenti_fire_across_full_match_timeline` walks 15'→30'→45'→60'→75'→90' and asserts `[1, 2, 3, 4, 5, 6]` in the call list — exactly once per momento, in trigger-matrix order. **Status guards correctly prevent retroactive fires.**

---

## Webhook Payload Audit

`MilestoneDetector.check_and_push` (m=1, n8n_url="http://test-n8n.local"):
```json
{
  "momento": 1,
  "context_text": "⚽ Argentina 0 - 0 Netherlands | Minuto 15 | 1er Tiempo\n\nGOLES: Sin goles aún\n\n...",
  "match_state": {
    "fixture_id": 868019,
    "status": {"elapsed": 15, "short": "1H", "long": "test-state"},
    "home": {"id": 26, "name": "Argentina", "goals": 0},
    "away": {"id": 33, "name": "Netherlands", "goals": 0},
    ...
  }
}
```

- ✅ `momento` is `int`
- ✅ `context_text` is the 7-section `get_context_text()` output (verified by `assert "Minuto 15" in payload["context_text"]`)
- ✅ `match_state` is `model_dump(mode="json")` (verified by JSON-parseable dict with `fixture_id`, `status`, `home`, `away`, `events`)
- ✅ URL is `{n8n_url}/webhook/momento` (respx route is pinned at this path in the test)
- ✅ Timeout is 5.0s (`milestones.py:93` — `httpx.AsyncClient(timeout=5.0)`)

---

## Security Audit

| Check | Result |
|---|---|
| Hardcoded API keys in production code | ✅ None — `api_key` is always injected via constructor → `Settings.API_FOOTBALL_KEY` |
| Real secrets in test data | ✅ None — tests use `"test-key"` and `"bad-key"` placeholders |
| `.env.example` has placeholders only | ✅ `API_FOOTBALL_KEY=your_api_key_here` |
| httpx client uses headers for auth (not URL params) | ✅ `headers={"x-apisports-key": api_key}` (line 58 of `api_football.py`) |
| `is_closed` test on injected client (detector does not close it) | ✅ `test_injected_http_client_is_not_closed_by_aclose` |

**No security issues found.**

---

## Issues

### CRITICAL (block merge)
**None.**

### WARNING (should fix but not blocking)
**None.**

### SUGGESTION (nice to have)
1. **Defensive card fallback (`match_state.py:275`):** The `else: emoji = "?"` branch is unreachable in normal operation because the parsers only emit "Yellow Card" / "Red Card" detail strings. Consider logging a warning if a `Card` event with unknown detail ever appears, so future schema drift doesn't silently produce confusing output. Not blocking.
2. **`update_details` pre-condition error message:** The `RuntimeError` raised when `update_details` is called before `update_fixture` is the right gate, but a custom exception class (`MatchStateNotInitialized`) would let callers distinguish "not yet initialized" from other runtime errors. Not blocking — change 3 (the only caller) checks for `RuntimeError` generically.
3. **Snapshot test uses string concatenation:** The 19-line `expected` string in `test_snapshot_at_minute_67_matches_pinned_format` is hand-built inline. A future maintenance hazard if the format changes. Consider extracting the canonical snapshot to a `.txt` fixture file in `backend/tests/snapshots/` so the test reads + compares instead of embedding the expected string. Not blocking.
4. **`n8n_url.rstrip("/")` is one-way:** `milestones.py:92` strips a single trailing slash from the configured URL, which handles `https://n8n.example.com/`. If the operator provides `https://n8n.example.com/webhook` (already with the webhook path) it would produce `https://n8n.example.com/webhook/webhook/momento`. Document the contract: pass base URL only, no trailing path. Not blocking.

---

## Spec-Implementation Gaps

| Spec | Gap | Severity |
|---|---|---|
| match-state-manager | None | — |
| api-football-client | None | — |
| milestone-detector | None | — |
| data-source-strategy (delta) | None | — |
| context-text-format (synced) | None | — |

**No gaps found between spec and implementation.**

---

## Verdict

**APPROVED.**

- 163/163 tests pass.
- 99.54% coverage (target was 70%).
- All 8 proposal success criteria met.
- All 13 design decisions match.
- All 44 spec scenarios across 4 specs are covered by passing tests.
- No security issues, no gaps, no critical or warning issues.
- The two-PR stacked-to-main strategy was followed (PR 1: match_state; PR 2: api_football + milestones + data_source).
- The TDD cycle (RED→GREEN→TRIANGULATE→REFACTOR) is visible in the commit log.

**Next step:** ready for `sdd-archive` — sync the four delta specs from `openspec/changes/backend-services/specs/` into `openspec/specs/`. The `context-text-format` spec is already synced (no content change).
