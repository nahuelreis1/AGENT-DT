# Proposal: Backend API

## Intent

The backend has services (changes 1–2) but no HTTP surface. This change adds the FastAPI layer + live-mode polling loop — the final piece making the backend deployable so n8n can consume state/context/predictions via REST and live mode stays fresh automatically.

## Scope

### In Scope
- FastAPI app with lifespan (startup creates services + optional polling task; shutdown cancels + closes)
- 8 REST endpoints: health, estado, contexto, predicciones, prediccion, mock/avanzar, mock/set-minute, stats/requests
- Polling loop — live mode only, 90s, error-resilient
- Mode-gated routes (`/mock/*` return 404 in live mode)
- MOMENTO_STATUSES (momento→FixtureStatus for mock avanzar)
- Full test suite (endpoints, lifespan, polling)

### Out of Scope
- audio_player (step 7), n8n workflow + README (steps 8–9)
- CORS, auth, DB persistence (state is in-memory)

## Capabilities

### New Capabilities
- `http-api`: FastAPI app, lifespan, 8 endpoints, mode-gating, request count
- `polling-loop`: Live-mode background task — `poll_once()` + `polling_loop()`, refreshes state, fires milestones

### Modified Capabilities
- `match-state-manager`: Add MOMENTO_STATUSES (momento 1..6 → FixtureStatus) for mock status progression

## Approach

`app.state` + `Depends` for injection (testable). `poll_once()` is a free function so tests avoid `while True`. Lifespan starts polling only when `not MOCK_MODE`. No CORS. Mock routes 404 in live mode. A `PredictionCreate` model (no timestamp) handles the POST body.

## Affected Areas

- **New** `backend/main.py` — app, lifespan, poll_once(), polling_loop()
- **New** `backend/routers/partido.py` — 8 endpoints with Depends
- **New** `backend/routers/__init__.py` — package marker
- **Modified** `backend/services/match_state.py` — add MOMENTO_STATUSES
- **Modified** `backend/tests/conftest.py` — app/client/mock fixtures
- **New** `backend/tests/test_routers.py` — endpoint tests
- **New** `backend/tests/test_main.py` — lifespan + polling tests
- **Modified** `backend/tests/test_match_state.py` — MOMENTO_STATUSES test

## Risks

- Polling swallows errors, state stale (Med) — log at error; poll_once tested with mock failures
- Lifespan leaks httpx client (Low) — cancel task first, then aclose(); test shutdown
- Mock /avanzar wrong status (Med) — MOMENTO_STATUSES test covers all 6
- Milestones re-fire on startup (Low) — _fired set prevents re-fire; lifespan primes state

## Rollback Plan

> ⚠️ TOUCHES THE POLLING LOOP (creates it). Per `config.yaml`, rollback required.

`git revert` — no migration, no external systems. Services from changes 1–2 are untouched. New files are additive; MOMENTO_STATUSES is additive. Reverting removes new files and restores match_state.py.

## Dependencies

- fastapi, uvicorn (already in requirements.txt)
- Changes 1–2 complete (200/200 tests, 99.59%)

## Success Criteria

- [ ] 8 endpoints respond correctly in mock mode
- [ ] /mock/* routes 404 in live mode; polling runs only live
- [ ] Lifespan shutdown cancels task + closes clients
- [ ] MOMENTO_STATUSES maps all 6 momenti correctly
- [ ] ≥70% coverage on new code; existing 200 tests green
