# Proposal: Backend Foundation

## Intent

Establish the **foundation layer** of the AI DT backend so change 2 (services) and change 3 (HTTP API) build on stable contracts. Enforces the plan's "mock and live share parsing logic" invariant by introducing the strategy pattern + shared parsers now — not later.

## Scope

### In Scope
- `backend/config.py` — pydantic-settings `Settings` (API_FOOTBALL_KEY, FIXTURE_ID, N8N_WEBHOOK_BASE_URL, MOCK_MODE, POLLING_INTERVAL)
- `backend/models.py` — 7 Pydantic models: `FixtureStatus`, `TeamScore`, `MatchEvent`, `PlayerStats`, `TeamStats`, `MatchState`, `Prediction`
- `backend/parsers.py` — `parse_fixture`, `parse_events`, `parse_statistics`, `parse_players` (pure dict → Pydantic)
- `backend/data_source.py` — `DataSource` Protocol, `MockDataSource` (13 JSONs by minute), `create_data_source(config)` factory; `LiveDataSource` = interface only
- `backend/mock_data/*.json` — 13 API-Football v3 envelope replicas (fixture 868019, Argentina 2-2 Netherlands)
- `backend/.env.example`, `requirements.txt`, `requirements-dev.txt`, `pyproject.toml` (pytest `asyncio_mode=auto`, cov ≥70%)
- `backend/tests/` — `conftest.py` + 4 test modules (config, models, parsers, data_source)

### Out of Scope
- `services/match_state.py`, `services/api_football.py`, `services/milestones.py` → change 2
- `routers/partido.py`, `main.py`, FastAPI app, polling loop → change 3
- `LiveDataSource` full impl → change 2
- `get_context_text()` full impl → change 2 (text **format** pinned here, snapshot test in change 2)
- `audio_player/`, n8n flows, README → later changes

## Capabilities

> Contract with sdd-spec. `openspec/specs/` is empty, so all capabilities here are new.

### New Capabilities
- `backend-config`: env-driven pydantic-settings loader (incl. `MOCK_MODE` flag, `POLLING_INTERVAL` default 90s)
- `match-data-models`: Pydantic v2 models for fixture status, team score, events, player/team stats, full match state, and IA predictions
- `api-football-parsing`: shared pure-function parsers normalizing API-Football v3 responses (`/fixtures`, `/fixtures/events`, `/fixtures/statistics`, `/fixtures/players`) into Pydantic
- `data-source-strategy`: `DataSource` Protocol + `MockDataSource` (loads 13 JSONs by minute-key) + `LiveDataSource` interface + `create_data_source(config)` factory

### Modified Capabilities
- None

## Approach

**Strategy pattern, shared parsers.** `MockDataSource` and `LiveDataSource` (change 2) both call the SAME `parse_*` functions. Parsers are the single seam knowing the API-Football v3 envelope; downstream speaks Pydantic. Invariant is structural, not policy.

**Hermetic tests.** `backend/mock_data/` is the single source of truth for test fixtures. Tests use `tmp_path`; no env vars, no network. Strict TDD per `openspec/config.yaml`.

**Context-text format** decided here (header, goals, possession/shots/xG, standout players, weak players, substitutions, cards); `get_context_text()` body lands in change 2 with a snapshot test pinning the format.

**Mock data**: 6-moment structure (goals, score, minute markers, cards) for fixture 868019 is factually correct. Granular stats (player ratings, pass counts) are illustrative, not Opta-precise.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/` | New | Greenfield directory |
| `backend/config.py` | New | pydantic-settings |
| `backend/models.py` | New | 7 Pydantic models |
| `backend/parsers.py` | New | 4 parser functions |
| `backend/data_source.py` | New | Protocol + Mock + factory |
| `backend/mock_data/*.json` | New | 13 API-Football v3 replicas |
| `backend/tests/` | New | conftest + 4 test modules |
| `backend/pyproject.toml` | New | pytest config (asyncio_mode, cov ≥70%) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Mock data drifts from real API-Football schema | Med | `parsers.py` is the single seam; any schema change updates parsers + mock together; tests use the same dicts as live |
| Granular mock stats not Opta-precise | Low | Documented as illustrative; only the 6-moment structure is treated as factual |
| `LiveDataSource` interface may not match real httpx response shape | Med | Protocol returns Pydantic models, not dicts; httpx detail stays in `LiveDataSource` impl in change 2 |
| MatchStateManager (change 2) depends on these models | Low | `MatchState` exposes `last_updated: datetime` and nullable `home_stats/away_stats`; design locked here |
| Review budget overrun (>400 lines) | Med | Tasks in change 2 batched; each file small and testable; tests live next to code |

## Rollback Plan

Greenfield: rollback = `rm -rf backend/`. **Downstream blockers**: change 2 cannot implement `MatchStateManager` / `APIFootballClient` / `MilestoneDetector` (all import from `backend/models.py`, `parsers.py`, `data_source.py`). Change 3 cannot exist. No external systems affected (nothing deployed yet). **Partial rollback** (e.g. parser shape wrong): redo affected `parsers.py` + tests + JSON files in one commit — no migration needed since this is pre-merge.

## Dependencies

- **External**: Python 3.11+, `pydantic`, `pydantic-settings`, `httpx`, `fastapi`, `uvicorn` (runtime); `pytest`, `pytest-asyncio`, `pytest-cov`, `respx` (dev)
- **Enables change 2 (backend-services)**: `MatchStateManager` consumes `MatchState` + parsers; `APIFootballClient` implements `LiveDataSource`; `MilestoneDetector` consumes `MatchState` and uses `create_data_source` in tests
- **Enables change 3 (backend-api)**: `routers/partido.py` serializes the models; `main.py` wires `create_data_source` into `app.state`

## Success Criteria

- [ ] `cd backend && pytest` passes with ≥70% coverage
- [ ] `MockDataSource.get_fixture(15)` returns `MatchState(elapsed=15, score=0-0, status="1H")`
- [ ] `MockDataSource.get_fixture(35)` includes Molina's goal in `events`
- [ ] `MockDataSource.get_fixture(ft)` returns score 2-2 with Weghorst's 90+11 equalizer
- [ ] All 4 parsers pass tests with API-Football-shaped dicts
- [ ] `create_data_source(Settings(MOCK_MODE=true))` returns `MockDataSource`
- [ ] No real API keys in repo (`.env.example` placeholders only)
- [ ] Total diff ≤ 400 lines (review budget per `openspec/config.yaml`)
