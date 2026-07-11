# Tasks: Backend Services

## Review Workload Forecast

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

~1300-1800 LOC across 2 PRs. Delivery strategy: ask-always.

### Work Units

| Unit | Goal | PR | Notes |
|------|------|-----|-------|
| 1 | MatchStateManager + text + predictions | PR 1 → main | Pure logic, no I/O |
| 2 | API client + detector + live source + factory | PR 2 → main | httpx + respx |

## PR 1 — Pure Logic (stacked-to-main)

### Phase 1: Foundation (~490 LOC)
- [x] 1.1 Create `backend/services/__init__.py` (marker).
- [x] 1.2 TDD: uninit raises + `update_fixture` stores + `get_state` returns. Implement. Files: `services/match_state.py`, `tests/test_match_state.py`.
- [x] 1.3 TDD: `update_details` reconciliation (empty→0-0, 4-goal→2-2 override, idempotent). Implement recompute.
- [x] 1.4 TDD: `get_context_text` byte-pinned snapshot at min 67 (7 sections, header exact) + pre-kickoff variants. Implement `PERIOD_NAMES` + 7 builders + header.
- [x] 1.5 TDD: `save_prediction` + `get_predictions` (round-trip, order, out-of-range). Implement log.
- [x] 1.6 REFACTOR: extract `_abbr()`, `_rating_float()`, `_filter_standouts()`; ≥70% coverage.
- [x] 1.7 Add `match_state` + `populated_match_state` fixtures to `tests/conftest.py` (preserve existing).

### Phase 2: Spec Sync
- [x] 1.8 Verify `openspec/specs/context-text-format/spec.md` synced (no content change).

### PR 1 Verification
- [x] 1.9 `cd backend && pytest` green; ≥70% on `services/match_state.py`; change 1 tests pass.

## PR 2 — Orchestration (stacked-to-main, base = main after PR 1)

### Phase 1: APIFootballClient (~175 LOC)
- [x] 2.1 TDD: `__init__` (default base_url, timeout=10.0, `x-apisports-key` header). Implement. Files: `services/api_football.py`, `tests/test_api_football.py` (respx).
- [x] 2.2 TDD: 4 fetches (respx 200, unwrap). Implement.
- [x] 2.3 TDD: `request_count` + WARNING at 80/100 (caplog). Wire counter + guards.
- [x] 2.4 TDD: 4xx→`HTTPStatusError`; network→`RequestError`. Verify.
- [x] 2.5 TDD: `aclose` (safe fresh, idempotent). Implement.
- [x] 2.6 REFACTOR: dedupe fetches, ≥70% coverage.

### Phase 2: LiveDataSource + Factory (~85 LOC)
- [x] 2.7 TDD: `LiveDataSource(client, fixture_id)` + `get_fixture` (client→`parse_fixture`). Implement. Files: `data_source.py`, `tests/test_api_football.py`.
- [x] 2.8 TDD: `get_details(momento)` 3 fetches + 5-tuple order. Implement.
- [x] 2.9 TDD: `create_data_source` live branch (client+fixture). Update factory. Files: `data_source.py`, `tests/test_data_source.py`.
- [x] 2.10 REFACTOR: delete `TestLiveDataSourceStub` (NotImplementedError OBSOLETE per spec delta).

### Phase 3: MilestoneDetector (~225 LOC)
- [x] 2.11 TDD: `__init__` (`_fired={1..6:False}`, injected not closed). Implement. Files: `services/milestones.py`, `tests/test_milestones.py`.
- [x] 2.12 TDD: 6 triggers + guards (m1@16/1H fires, m1@16/2H blocked, m3@HT, m6@FT, multi-fire@82/2H = 1+2+4+5). Implement `TRIGGER_MATRIX` + loop.
- [x] 2.13 TDD: payload `{momento, context_text, match_state.model_dump("json")}` + URL `{n8n_url}/webhook/momento` + 5s timeout. Wire.
- [x] 2.14 TDD: empty `n8n_url` (no-op, info, `_fired[1]` False) + POST fail (error, mark fired, no retry) + fail doesn't block next. Wire `except Exception`.
- [x] 2.15 TDD: `aclose` (internal closed, injected untouched). Implement.
- [x] 2.16 REFACTOR: extract `_build_payload(state)`; ≥70% coverage.

### Phase 4: Final Verification
- [x] 2.17 `cd backend && pytest --cov` green; ≥70% on `backend/services/` + `data_source.py`; change 1 green.

## Out of Scope (change 3)
- `routers/partido.py`, `main.py` (FastAPI + lifespan + polling), prediction HTTP wiring, `/mock/avanzar`, `/stats/requests`, `/health`.
