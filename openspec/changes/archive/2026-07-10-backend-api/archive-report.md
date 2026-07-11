# Archive Report: backend-api (FINAL)

**Change**: `backend-api` (change 3 of 3 — FINAL)
**Status**: ARCHIVED
**Archived on**: 2026-07-10
**Project**: AI DT (`agent-dt`)
**Artifact store**: hybrid (OpenSpec filesystem + Engram)
**Verify verdict**: PASS — 231/231 tests, 99.92% coverage, 0 critical, 0 warnings, 2 suggestions (non-blocking)
**Delivery**: 2 stacked PRs to main (PR1: router+endpoints, PR2: main+lifespan+polling) + 1 verify-fix test batch

---

## Executive Summary

The `backend-api` change is the FINAL change of the AI DT backend. It wires the service layer from changes 1–2 into a deployable FastAPI app and adds the live-mode polling loop. Three capabilities shipped:

1. **`http-api`** (NEW) — FastAPI app with 8 REST endpoints: `/health`, `/partido/estado`, `/partido/contexto`, `/partido/predicciones` (GET), `/partido/prediccion` (POST), `/mock/avanzar` (mock-mode only), `/mock/set-minute` (mock-mode only), `/stats/requests`. Mode-gated: `/mock/*` returns 404 in live mode; all other endpoints work in both modes. Lifespan injects `Settings`/`DataSource`/`MatchStateManager`/`MilestoneDetector` into `app.state`; routes use `Depends(get_*)` for testable DI without globals.
2. **`polling-loop`** (NEW) — `poll_once(data_source, match_state, detector)` free function: `get_fixture` → `update_fixture` → `check_and_push` with per-step error containment. `polling_loop` runs every 90s in live mode only; cancellable via `asyncio.Task.cancel()`. Lifespan starts polling in live mode, never in mock mode.
3. **`match-state-manager`** (MODIFIED) — Added `MOMENTO_STATUSES: dict[int, FixtureStatus]` mapping momento keys 1..6 to fixture statuses (1=1H@15, 2=1H@30, 3=HT@45, 4=2H@60, 5=2H@75, 6=PEN@120). Consumed by `POST /mock/avanzar` to advance simulated match state.

The work was delivered as **2 stacked PRs to main** plus a verify-fix test batch, keeping each PR under the 400-line review budget per the `sdd-phase-common` review workload guard. PR1 = `routers/__init__.py` + `routers/partido.py` (8 endpoints) + `MOMENTO_STATUSES` + conftest expansion (~470 LOC). PR2 = `backend/main.py` (`poll_once` + `polling_loop` + lifespan + app wiring) + `tests/test_main.py` (~430 LOC).

---

## Test Results

| Metric | Target | Actual | Result |
|---|---|---|---|
| Tests collected | ≥228 | **231** | ✅ |
| Tests passed | 231 | 231 | ✅ |
| Tests failed | 0 | 0 | ✅ |
| Tests errored | 0 | 0 | ✅ |
| Warnings | 0 | 0 | ✅ |
| Coverage (overall) | ≥70% | **99.92%** | ✅ |
| Coverage (`main.py`) | ≥70% | **100%** (44/44 stmts) | ✅ |
| Coverage (`routers/partido.py`) | ≥70% | **100%** (66/66 stmts) | ✅ |
| Coverage (`services/match_state.py`) | ≥70% | 99% (143/144) | ✅ |
| Coverage (`tests/test_main.py`) | — | 100% (134/134) | ✅ |
| Strict TDD | required | RED→GREEN→VERIFY-FIX visible in commit log | ✅ |
| New third-party deps | 0 | 0 (fastapi/uvicorn already in requirements.txt) | ✅ |

**Test command**: `cd backend && pytest` (exit code 0, 25.69s).

**Test breakdown**:
- 200 pre-existing (from `backend-foundation` + `backend-services` archives)
- 19 PR1 (4 MOMENTO_STATUSES + 15 endpoint/dependency scenarios)
- 9 PR2 (3 poll_once + 2 polling_loop + 4 lifespan/shutdown)
- 3 verify-fix (additional triangulation tests added after PR2 review)

**Spec scenario coverage**:
- `http-api` (NEW) — 8 requirements, 14 scenarios: all directly covered
- `polling-loop` (NEW) — 3 requirements, 10 scenarios: 8/10 directly covered; 2 covered by composition (warnings noted in verify-report)
- `match-state-manager` (MODIFIED, this change's delta) — 1 new requirement, 2 scenarios: both directly covered

---

## Spec Sync Summary

| Domain | Action | Details |
|---|---|---|
| `http-api` | **Created** (new) | 8 requirements, 14 scenarios — full spec copied from `openspec/changes/backend-api/specs/http-api/spec.md` |
| `polling-loop` | **Created** (new) | 3 requirements, 10 scenarios — full spec copied from `openspec/changes/backend-api/specs/polling-loop/spec.md` |
| `match-state-manager` | **Merged** (additive) | 1 requirement ADDED (MOMENTO_STATUSES, 2 scenarios) — appended to existing canonical spec. All 6 prior requirements preserved unchanged. |

**Total**: 2 new specs, 1 merged spec (additive, non-destructive). Source of truth (`openspec/specs/`) now has 10 domains: `api-football-client`, `api-football-parsing`, `backend-config`, `context-text-format`, `data-source-strategy`, `http-api`, `match-data-models`, `match-state-manager`, `milestone-detector`, `polling-loop`.

### Additive-merge confirmation (per `openspec/config.yaml` `rules.archive`)

The `match-state-manager` delta is purely additive (1 new requirement appended after "Mode-Agnostic Behavior"). No existing requirements were REMOVED or MODIFIED. The 6 original requirements (Construction, Detail Update, Context Text, Prediction Log, Mode-Agnostic, plus their 5 from change 2 archives) are preserved byte-for-byte. The `predict-and-compare lineage` between momento 3 and momento 6 (per `rules.archive`) is unchanged — `MOMENTO_STATUSES` is a new constant used by mock-mode advancement, not by the prediction log.

---

## Artifacts Produced

### Source code (new)

| File | Purpose |
|---|---|
| `backend/main.py` | FastAPI app, `lifespan`, `poll_once()`, `polling_loop()` — 121 lines |
| `backend/routers/__init__.py` | Package marker |
| `backend/routers/partido.py` | 8 endpoints + 4 `Depends` functions + 3 Pydantic request models — 66 statements |
| `backend/tests/test_routers.py` | 15 endpoint tests (mock+live mode-gating, 422/500/404 paths) — PR1 |
| `backend/tests/test_main.py` | 9 lifespan + polling tests across 4 classes — 308 lines, 134 statements — PR2 |

### Source code (modified)

| File | Change | Description |
|---|---|---|
| `backend/services/match_state.py` | Additive | Added `MOMENTO_STATUSES: dict[int, FixtureStatus]` constant (1 line in constant block, additive) |
| `backend/tests/conftest.py` | Additive | Added `test_app`, `test_client`, `mock_settings`, `live_settings`, `mock_ds`, `live_ds`, `mock_state`, `live_state`, `mock_app`, `live_app` fixtures — ALL existing fixtures preserved |
| `backend/tests/test_match_state.py` | Additive | Added `test_momento_statuses_all_six` covering all 6 keys → FixtureStatus mapping |

### Specs (synced to source of truth)

| File | Action |
|---|---|
| `openspec/specs/http-api/spec.md` | **Created** (166 lines, 8 requirements, 14 scenarios) |
| `openspec/specs/polling-loop/spec.md` | **Created** (81 lines, 3 requirements, 10 scenarios) |
| `openspec/specs/match-state-manager/spec.md` | **Merged** (was 159 lines, now 184 lines; +1 requirement, +2 scenarios — purely additive) |

### SDD artifacts (this archive)

| File | Purpose |
|---|---|
| `openspec/changes/archive/2026-07-10-backend-api/proposal.md` | Intent, scope, approach, risks, rollback (rollback = `git revert` per `config.yaml`) |
| `openspec/changes/archive/2026-07-10-backend-api/design.md` | 12 architecture decisions, data flow, interfaces, 8 testing strategy rows |
| `openspec/changes/archive/2026-07-10-backend-api/specs/...` | 3 delta specs (2 new + 1 modified) |
| `openspec/changes/archive/2026-07-10-backend-api/tasks.md` | 34 tasks across 2 PRs (PR1: 19 tasks, PR2: 14 tasks, PR1 integration: 1 task), all marked `[x]` |
| `openspec/changes/archive/2026-07-10-backend-api/verify-report.md` | PASS — 228/228 at verify time, 99.92% coverage, 0 critical, 0 warnings, 2 suggestions |
| `openspec/changes/archive/2026-07-10-backend-api/archive-report.md` | This file |

### Engram observations (traceability)

| Observation ID | Title | Sync ID |
|---|---|---|
| #126 | AI DT — Project Context (sdd-init) | `obs-47066e4e14e3c942` |
| #155 | sdd/backend-api/proposal | `obs-66f665b578193fff` |
| #156 | sdd/backend-api/spec | `obs-471272d28750c020` |
| #157 | sdd/backend-api/design | `obs-98383c4f25af4e73` |
| #158 | sdd/backend-api/tasks | `obs-38a54f9d2e892df1` |
| #159 | sdd/backend-api/apply-progress (PR1+PR2+verify-fix) | `obs-ddebd80d735fd251` |
| #160 | sdd/backend-api/verify-report | `obs-236862bc7a331864` |
| (this) | sdd/backend-api/archive-report | (saved on archive) |

---

## Verify Suggestions (carried forward for future reference)

These are the 2 non-blocking suggestions from the verify report. Not required for this change to close; logged here for future work:

1. **`polling_loop(interval: float)` differs from design's `interval: int`** — benign (asyncio.sleep accepts both; Settings.POLLING_INTERVAL is int). Stylistic. *Owner: any future change that needs stricter typing.*
2. **`_StopLoop` could be `asyncio.CancelledError` directly** — same semantics, more explicit. Stylistic. *Owner: any future change that touches polling.*

Plus the 3 WARNING items from PR2 (now all 0 warnings after verify-fix batch):
- "Per-iteration exception does not stop the loop" — added direct test in verify-fix batch
- "Mock-mode shutdown closes detector only" — added direct test in verify-fix batch
- "`test_shutdown_order_live` only asserts the last 2 of 4 ordered steps" — strengthened in verify-fix batch

---

## Predict-and-Compare Lineage (per `openspec/config.yaml` `rules.archive`)

The "magic" of the system is the momento 3 → momento 6 prediction comparison. This change implements the **HTTP wiring half** of that lineage (change 2 owned the service-layer half).

| Momento | Service layer (change 2) | HTTP wiring (this change) |
|---|---|---|
| 3 (HT) | `MatchStateManager.save_prediction(3, "...")` appends to the in-memory log | `POST /partido/prediccion` calls `save_prediction` (validated by `PredictionCreate(momento: int = Field(ge=1, le=6), content: str = min_length=1)`) |
| 6 (FT) | `MatchStateManager.get_predictions()` returns the log in append order | `GET /partido/predicciones` calls `get_predictions` so n8n can compare m=3 prediction vs actual outcome |

**What ships in this change:** the `POST /partido/prediccion` and `GET /partido/predicciones` routes, the `PredictionCreate` Pydantic model with `Field(ge=1, le=6)` + `min_length=1` content, the 422/200 test coverage, the 7-scenario HTTP-level spec.

**Invariant preserved:** the `momento` validation is in two layers: Pydantic `PredictionCreate` (1..6, non-empty content) at the HTTP boundary AND Pydantic `Prediction` model (1..=6) at the service boundary. A bad value is rejected at the model boundary regardless of which layer catches it first.

**MOMENTO_STATUSES contribution:** the new constant is used by `POST /mock/avanzar` to advance the simulated state through the 6 milestone moments. The constant mirrors the milestone triggers in `services/milestones.py` — momento 3 maps to `HT@45`, momento 6 maps to `PEN@120`. Per `rules.proposal`, the milestone triggers (1=15', 2=30', 3=HT, 4=60', 5=75', 6=FT) MUST NOT change without re-flagging.

---

## Archive Move

`openspec/changes/backend-api/` → `openspec/changes/archive/2026-07-10-backend-api/`

The full change folder (proposal, design, 3 spec files, tasks, verify-report) moves to the archive as an audit trail. Per `sdd-archive` SKILL.md rule, archived changes are NEVER deleted or modified.

The active `openspec/changes/` directory now contains only the README; all 4 changes are archived:
- `2026-07-09-backend-foundation` (change 1)
- `2026-07-10-fix-api-football-v3-compatibility` (change 1.1 — compatibility fix)
- `2026-07-10-backend-services` (change 2)
- `2026-07-10-backend-api` (change 3, FINAL — just archived)

---

## SDD Cycle Complete

The `backend-api` change is fully planned, implemented, verified, and archived. The AI DT backend is now complete:

- **Change 1** (backend-foundation): Pydantic models, API-Football v3 parsers, config, context text format
- **Change 1.1** (fix-api-football-v3-compatibility): envelope shape correction
- **Change 2** (backend-services): `MatchStateManager`, `APIFootballClient`, `MilestoneDetector`, `LiveDataSource` filling
- **Change 3** (backend-api, FINAL): FastAPI HTTP surface, lifespan, polling loop, 8 endpoints, mock-mode progression

The backend is now deployable: n8n can consume `GET /partido/estado`, `GET /partido/contexto`, `GET /partido/predicciones`, `POST /partido/prediccion`, and live mode stays fresh via the 90s polling loop that fires milestone webhooks automatically.

**Ready for the next change** (e.g., step 7 audio_player, steps 8-9 n8n workflow + README, per the proposal's out-of-scope items).
