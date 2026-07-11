# Archive Report — backend-foundation

**Change**: `backend-foundation` (change 1 of 3)
**Archived**: 2026-07-09
**Mode**: hybrid (openspec + engram)
**Status**: APPROVED WITH WARNINGS
**Verdict source**: `verify-report.md` — 83/83 tests pass, 100% coverage, 0 critical issues, 1 pre-approved warning, 3 suggestions

---

## Summary

Established the **foundation layer** of the AI DT backend: typed configuration, Pydantic v2 match-state models, shared API-Football v3 parsers, and a `DataSource` strategy that lets mock and live modes share the same parsing code. This is the greenfield scaffold that change 2 (services) and change 3 (HTTP API) build on.

**Core invariant enforced structurally**: `parsers.py` is the single seam that knows the API-Football v3 envelope. Both `MockDataSource` and the (change 2) `LiveDataSource` call the same `parse_*` functions, so downstream code never branches on `MOCK_MODE` — it branches only on the shape of the returned Pydantic models.

---

## Test Results

| Metric | Value |
|--------|-------|
| Total tests | 83 |
| Passing | 83 |
| Failing | 0 |
| Skipped | 0 |
| Coverage | 100% (719 / 719 statements) |
| Required threshold | 70% — exceeded by 30 percentage points |
| Test runtime | 0.65s |
| TDD mode | strict (RED → GREEN → TRIANGULATE → REFACTOR) |
| Test runner | `cd backend && pytest` |

Coverage breakdown:

| Module | Stmts | Miss | Cover |
|--------|-------|------|-------|
| `backend/config.py` | 17 | 0 | 100% |
| `backend/data_source.py` | 44 | 0 | 100% |
| `backend/models.py` | 27 | 0 | 100% |
| `backend/parsers.py` | 62 | 0 | 100% |
| `tests/conftest.py` | 9 | 0 | 100% |
| `tests/test_config.py` | 94 | 0 | 100% |
| `tests/test_data_source.py` | 141 | 0 | 100% |
| `tests/test_models.py` | 116 | 0 | 100% |
| `tests/test_parsers.py` | 209 | 0 | 100% |
| **TOTAL** | **719** | **0** | **100%** |

---

## Spec Sync Summary

| Domain | Action | Reason | Scenarios |
|--------|--------|--------|-----------|
| `backend-config` | **Created** at `openspec/specs/backend-config/spec.md` | Greenfield — copied from delta | 8 |
| `match-data-models` | **Created** at `openspec/specs/match-data-models/spec.md` | Greenfield — copied from delta | 9 |
| `api-football-parsing` | **Created** at `openspec/specs/api-football-parsing/spec.md` | Greenfield — copied from delta | 13 |
| `data-source-strategy` | **Created** at `openspec/specs/data-source-strategy/spec.md` | Greenfield — copied from delta | 7 |
| `context-text-format` | **DEFERRED** — stays in `changes/backend-foundation/specs/` | Implementation (`get_context_text()`) lands in change 2 with a snapshot test pinning the format; per proposal: "context-text format decided here, snapshot test in change 2" | 5 (pinned, not yet exercised) |

**Total in-scope coverage**: 37 / 37 scenarios pass (100%). Greenfield merge — no destructive delta to existing main specs (`openspec/specs/` previously held only a `README.md` placeholder).

**Archive rule applied**: `archive: Warn before merging destructive deltas to main specs` — N/A, no main specs existed. Direct copy is non-destructive.

**Archive rule applied (deferred to change 2)**: `archive: Preserve the predict-and-compare lineage between momento 3 and momento 6` — the `context-text-format` spec is the file that pins this lineage (it defines the exact text format pushed at each `momento` push, including the momento 3 → 6 comparison that n8n's AI Agent consumes). The spec is captured here in the change folder; it will be merged to main specs in the change 2 archive, when the snapshot test pins the format end-to-end.

---

## Verdict

**APPROVED WITH WARNINGS** — `sdd-verify` verdict, no critical issues.

- 0 critical
- 1 warning (pre-approved): total diff size ~10,535 lines, far exceeding the 400-line review budget. **Pre-approved by user as `size:exception` for data files** (19 mock JSONs are ~9,400 lines; code-only diff is ~2,200 lines across 14 files, mostly mechanical Pydantic models and parser functions).
- 3 suggestions (cosmetic — see below)

**Why archive despite the warning**: the warning is pre-approved, all 83 tests pass, 100% coverage, and the change is greenfield with no external systems affected. Rolling back at this point would discard working tested code; archiving it freezes the contract for change 2.

---

## Artifacts Produced

### Change folder (archived as `openspec/changes/archive/2026-07-09-backend-foundation/`)

| Artifact | Status |
|----------|--------|
| `proposal.md` | ✅ |
| `design.md` | ✅ (140 lines) |
| `tasks.md` | ✅ (24 / 24 tasks complete) |
| `verify-report.md` | ✅ (296 lines) |
| `archive-report.md` | ✅ (this file) |
| `specs/backend-config/spec.md` | ✅ (delta) |
| `specs/match-data-models/spec.md` | ✅ (delta) |
| `specs/api-football-parsing/spec.md` | ✅ (delta) |
| `specs/data-source-strategy/spec.md` | ✅ (delta) |
| `specs/context-text-format/spec.md` | ✅ (delta, **deferred** — will sync with change 2) |

### Source code (committed, NOT in change folder)

**Backend source** (5 modules, ~150 LOC code):

| Path | Role |
|------|------|
| `backend/config.py` | `pydantic-settings` Settings with live-mode model_validator |
| `backend/models.py` | 7 Pydantic v2 models |
| `backend/parsers.py` | 4 pure-function parsers + `STAT_TYPE_MAP` |
| `backend/data_source.py` | Protocol, `MockDataSource`, `LiveDataSource` stub, `create_data_source` factory, `MOMENTO_FILE_KEYS` |
| `backend/__init__.py` | Package marker |

**Backend tests** (5 modules, ~560 LOC test code):

| Path | Tests |
|------|-------|
| `backend/tests/conftest.py` | module-relative `mock_dir` fixture |
| `backend/tests/test_config.py` | 14 tests |
| `backend/tests/test_models.py` | 17 tests |
| `backend/tests/test_parsers.py` | 24 tests |
| `backend/tests/test_data_source.py` | 19 tests |
| `backend/tests/__init__.py` | Package marker |

**Mock data** (19 API-Football v3 JSONs, fixture 868019 ARG vs NED Qatar 2022):

| Path | Role |
|------|------|
| `backend/mock_data/fixture.json` | Final state (2-2, FT) |
| `backend/mock_data/events_{15,30,ht,60,75,ft}.json` | 6 cumulative event snapshots |
| `backend/mock_data/statistics_{15,30,ht,60,75,ft}.json` | 6 per-team stat snapshots |
| `backend/mock_data/players_{15,30,ht,60,75,ft}.json` | 6 player-rating snapshots (2 teams × 11 players each) |

**Configuration** (4 files):

| Path | Role |
|------|------|
| `backend/pyproject.toml` | pytest config (`asyncio_mode=auto`, cov ≥70%) |
| `backend/requirements.txt` | pydantic, pydantic-settings, httpx, fastapi, uvicorn |
| `backend/requirements-dev.txt` | pytest, pytest-asyncio, pytest-cov, respx |
| `backend/.env.example` | 5 Settings vars with `your_api_key_here` placeholders |

**Total source files created**: 33 (5 src + 5 test + 19 mock JSON + 4 config).

---

## Source of Truth Updated

The following main specs now reflect the implemented behavior:

- `openspec/specs/backend-config/spec.md` (new)
- `openspec/specs/match-data-models/spec.md` (new)
- `openspec/specs/api-football-parsing/spec.md` (new)
- `openspec/specs/data-source-strategy/spec.md` (new)

The `context-text-format` delta spec **stays in the change folder** — see deferral note above.

---

## Verify Suggestions (preserved for future reference)

The `sdd-verify` report flagged 3 suggestions, all non-blocking:

### S-1: Proposal uses `get_fixture(<minute>)` notation — actual API is `get_details(momento)`

The proposal's success-criteria block describes `MockDataSource.get_fixture(15)`, `get_fixture(35)`, `get_fixture(ft)`. The actual implementation uses `MockDataSource.get_details(momento: int)` with the `MOMENTO_FILE_KEYS` map. The spec (`data-source-strategy/spec.md`) is correct and is the source of truth; the proposal is the only document with the older notation.

**Action**: Correct the proposal's success-criteria block next time these docs are touched. Not a merge blocker.

### S-2: `fixture.json` is the FINAL state, not pre-kickoff

`mock_data/fixture.json` represents the post-match state (status: "FT", elapsed: 120, goals: 2-2). `MockDataSource.get_fixture()` therefore returns the final state, not a pre-kickoff 0-0/1H snapshot. This matches the spec but could surprise a reader expecting `get_fixture()` to be the pre-kickoff identity. The pre-kickoff 0-0/1H state is `get_details(momento=1)`.

**Action**: No change. If a "pre-match" identity is later needed, add a `fixture_pre.json` and a `pre_match=False` parameter to `get_fixture()`.

### S-3: CoverageWarning about `backend` module re-import

Pytest emits a benign `CoverageWarning: Module backend was previously imported, but not measured` because `tests/test_config.py` and `conftest.py` import the same modules coverage is measuring. Coverage % is unaffected (still 100%).

**Action**: Add `--cov-branch` to `pyproject.toml` or use `import-mode=importlib` for a clean warning. Cosmetic only.

---

## What This Change Enables

- **Change 2 (`backend-services`)** can now implement:
  - `MatchStateManager` (consumes `MatchState` from this change's models; uses `last_updated: datetime` and nullable `home_stats/away_stats`).
  - `APIFootballClient` (fills in `LiveDataSource` interface; uses `parse_*` from this change's parsers).
  - `MilestoneDetector` (consumes `MatchState`; uses `create_data_source` in tests; pushes the **6 milestone triggers** (1=15', 2=30', 3=HT, 4=60', 5=75', 6=FT) per the config.yaml rule).
  - `get_context_text()` (consumes the `context-text-format` spec deferred from this change; adds a snapshot test pinning the format).
  - `PERIOD_NAMES` map and per-momento webhook payload documentation (per `config.yaml` `design:` rule: "Document the exact webhook payload pushed to n8n for each milestone").

- **Change 3 (`backend-api`)** can now implement:
  - `routers/partido.py` (serializes the Pydantic models from this change).
  - `main.py` (wires `create_data_source(Settings())` into `app.state`).
  - FastAPI polling loop.

---

## Risks Captured

These risks were in the proposal and are noted here for traceability:

| Risk | Likelihood | Status |
|------|------------|--------|
| Mock data drifts from real API-Football schema | Med | Mitigated: parsers are the single seam |
| Granular mock stats not Opta-precise | Low | Documented as illustrative; only 6-moment structure is factual |
| `LiveDataSource` interface may not match real httpx response shape | Med | Mitigated: Protocol returns Pydantic, not dicts; httpx detail stays in change 2 impl |
| MatchStateManager (ch.2) depends on these models | Low | Resolved: `MatchState` exposes `last_updated: datetime` and nullable `home_stats/away_stats` |
| Review budget overrun (>400 lines) | Med | Pre-approved as `size:exception` for data files; code-only diff is 5x cap, defensible |

---

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived. All 24 tasks are complete. All 37 in-scope spec scenarios are covered by passing tests. The 4 in-scope specs are now in main specs; the 5th (context-text-format) is captured in the change folder and will sync in change 2.

**Ready for change 2**: `backend-services` (services + `get_context_text()` + `LiveDataSource` impl + milestone detector).
