# Tasks: Backend Foundation

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1400-1800 (9 src/config + 19 JSON + 5 test/conftest) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1 scaffold+models → PR2 config+parsers → PR3 mock_data+conftest → PR4 data_source |
| Delivery strategy | ask-always |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | PR | Base |
|------|------|----|------|
| 1 | Scaffold + Models | PR 1 | main |
| 2 | Config + Parsers | PR 2 | PR 1 |
| 3 | Mock data (19 JSONs) + conftest | PR 3 | PR 2 |
| 4 | DataSource strategy | PR 4 | PR 3 |

> 19 mock JSONs alone are ~600-900 lines. User MUST pick chain strategy (stacked-to-main / feature-branch-chain / size:exception) before sdd-apply.

## Phase 0: Dev Environment Scaffold

- [x] 0.1 Create `backend/pyproject.toml` (asyncio_mode=auto, testpaths, cov ≥70).
- [x] 0.2 Create `backend/requirements.txt` (pydantic, pydantic-settings, httpx, fastapi, uvicorn) and `requirements-dev.txt` (pytest, pytest-asyncio, pytest-cov, respx).
- [x] 0.3 Create `backend/.env.example` with placeholders for all 5 Settings fields.
- [x] 0.4 Create `backend/__init__.py` and `backend/tests/__init__.py`.

## Phase 1: Match Data Models (TDD)

- [x] 1.1 RED: write `backend/tests/test_models.py` covering all `match-data-models` scenarios.
- [x] 1.2 GREEN: implement `backend/models.py` with 7 Pydantic v2 models + Literal constraints.
- [x] 1.3 REFACTOR: extract shared types; verify `pytest backend/tests/test_models.py`.

## Phase 2: Backend Config (TDD)

- [x] 2.1 RED: write `backend/tests/test_config.py` (defaults, .env, int coercion, 3 live-mode rejects).
- [x] 2.2 GREEN: implement `backend/config.py` with pydantic-settings + `model_validator`.
- [x] 2.3 REFACTOR: clean up; verify `pytest backend/tests/test_config.py`.

## Phase 3: API-Football Parsers (TDD)

- [x] 3.1 RED: write `backend/tests/test_parsers.py` for all 4 parsers (hand-crafted dicts, no I/O).
- [x] 3.2 GREEN: implement `backend/parsers.py` with `STAT_TYPE_MAP` and unknown-event skipping.
- [x] 3.3 REFACTOR: hoist `STAT_TYPE_MAP`; verify `pytest backend/tests/test_parsers.py`.

## Phase 4: Mock Data (19 JSONs, API-Football v3 envelope)

- [x] 4.1 Create `backend/mock_data/fixture.json` (868019, ARG vs NED, 1H, 0-0).
- [x] 4.2 Create `events_{15,30,ht,60,75,ft}.json` (6 files, cumulative; `ft` has Weghorst 90+11').
- [x] 4.3 Create `statistics_{15,30,ht,60,75,ft}.json` (6 files, per-team stats).
- [x] 4.4 Create `players_{15,30,ht,60,75,ft}.json` (6 files, 11+11 players, evolving ratings).

## Phase 5: DataSource Strategy (TDD)

- [x] 5.1 RED: write `conftest.py` (module-relative `mock_dir`) and `test_data_source.py` (Protocol, all 6 moments, factory, NotImplementedError, missing-JSON).
- [x] 5.2 GREEN: implement `data_source.py` with Protocol, `MOMENTO_FILE_KEYS`, `MockDataSource` (with `_load_json`), `LiveDataSource` stub, `create_data_source`.
- [x] 5.3 REFACTOR: clean up; verify `pytest backend/tests/test_data_source.py`.

## Phase 6: Verification

- [x] 6.1 Run `cd backend && pytest --cov=. --cov-report=term-missing`; confirm ≥70% coverage.
- [x] 6.2 Verify proposal success criteria (m1→0-0/1H, m6→2-2 + Weghorst 90+11', factory branches, no real keys in repo).
