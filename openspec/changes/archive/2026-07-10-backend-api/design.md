# Design: Backend API

## Technical Approach

FastAPI app with an `asynccontextmanager` `lifespan` creates all services on `app.state` and starts an optional polling task. `app.state` + `Depends(get_*)` functions give testable dependency injection without globals. `poll_once()` is a free function (not a method) so tests call it directly without `while True`. The polling loop runs only in live mode (`not MOCK_MODE`); mock mode is driven entirely by HTTP. Change 2's services (`MatchStateManager`, `MilestoneDetector`, `DataSource`) are reused unchanged except for one additive constant (`MOMENTO_STATUSES`).

## Architecture Decisions

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | DI mechanism | `app.state` + `Depends(get_*)` reading `request.app.state` | Standard FastAPI; tests build a test app with pre-populated state, no lifespan needed. |
| 2 | `poll_once` error boundary | `try/except Exception` inside `poll_once`, log at error | Single responsibility — `polling_loop` stays a trivial while/sleep; one place to contain errors. |
| 3 | `polling_loop` no try/except | Relies on `poll_once` swallowing | If `poll_once` catches all, the loop never sees an exception; only `CancelledError` from `asyncio.sleep` escapes → the intended cancellation path. |
| 4 | Shutdown order | cancel task → `await task` (suppress `CancelledError`) → `detector.aclose()` → `client.aclose()` | Cancel first so no in-flight request hits a closed httpx connection. |
| 5 | Lifespan primes first fixture | `await get_fixture()` → `update_fixture()` before `yield` | Endpoints work on first request; no cold-start 500. |
| 6 | Mock mode: no polling task | `if not MOCK_MODE` gate | No live API to poll; mock is HTTP-driven via `/mock/avanzar`. |
| 7 | POST body model | `PredictionCreate(momento, content)` — no timestamp | Server stamps `now()`; client cannot forge it. `Field(ge=1, le=6)` → 422 for bad momento. |
| 8 | `/partido/contexto` return | `Response(text, media_type="text/plain; charset=utf-8")` | Context is natural-language text, not JSON; n8n consumes raw body. |
| 9 | `/mock/*` live response | HTTP 404 | Route is mode-specific; 404 = "does not exist here" is cleaner than 403 (forbidden) or 501. |
| 10 | `/stats/requests` path | `data_source._client.request_count` via `isinstance(LiveDataSource)` | `APIFootballClient` lives inside `LiveDataSource`, not on `app.state`; mock returns 0. |
| 11 | `MOMENTO_STATUSES` location | Module constant in `match_state.py` | Co-located with the manager that consumes it; `dict[int, FixtureStatus]` keyed 1..6. |
| 12 | Router file | `routers/partido.py` with `APIRouter()` | Follows `rules.apply: Follow existing backend/services and backend/routers layout`. |

## Data Flow

### Polling loop (live mode)
```
Startup → lifespan
  create_data_source(live) → LiveDataSource
  get_fixture() → update_fixture()              # prime state
  MilestoneDetector(live, n8n_url)
  polling_task = create_task(polling_loop)

Every 90s → poll_once:
  data_source.get_fixture() → match_state.update_fixture()
  milestone_detector.check_and_push()
    └─ for each unfired momento: get_details → update_details
       → get_context_text → POST {n8n_url}/webhook/momento
       → _fired[m] = True

Shutdown: cancel task → await → detector.aclose() → client.aclose()
```

### Webhook payload + 6-moment flow

Already documented in change 2 design (`openspec/changes/archive/2026-07-10-backend-services/design.md`): POST `{n8n_url}/webhook/momento` with `{"momento": int, "context_text": str, "match_state": <MatchState.model_dump("json")>}`. The momento 3 → 6 prediction lineage (HT prediction saved via `POST /partido/prediccion`, compared at FT via `GET /partido/predicciones`) is unchanged — this change only adds the HTTP surface the lineage depends on.

### Mock mode flow
```
POST /mock/avanzar {momento: 1}
  → MOMENTO_STATUSES[1] → state.status = FixtureStatus(15, "1H", ...)
  → data_source.get_details(1) → update_details()   # score recomputed
  → milestone_detector.check_and_push()             # n8n_url="" → no-op
  → {"momento": 1, "status": "advanced"}
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/main.py` | Create | FastAPI app, `lifespan`, `poll_once()`, `polling_loop()`. |
| `backend/routers/__init__.py` | Create | Package marker. |
| `backend/routers/partido.py` | Create | 8 endpoints + 4 `Depends` functions + 3 request models. |
| `backend/services/match_state.py` | Modify | Add `MOMENTO_STATUSES` constant (additive, no behavior change). |
| `backend/tests/conftest.py` | Modify | Add `test_app`, `test_client`, `mock_settings`; preserve ALL existing fixtures. |
| `backend/tests/test_routers.py` | Create | All 8 endpoints, mock/live mode-gating, 422/500/404 paths. |
| `backend/tests/test_main.py` | Create | `poll_once` success+error, `polling_loop` cancellation, lifespan startup/shutdown. |
| `backend/tests/test_match_state.py` | Modify | Add `MOMENTO_STATUSES` coverage (all 6 keys). |

## Interfaces / Contracts

```python
# main.py
async def poll_once(data_source, match_state, milestone_detector) -> None
async def polling_loop(data_source, match_state, milestone_detector, interval: int) -> None
@asynccontextmanager
async def lifespan(app: FastAPI) -> None  # sets app.state.{config,data_source,match_state,milestone_detector,[polling_task]}

# routers/partido.py — Depends functions
def get_data_source(request: Request) -> DataSource
def get_match_state(request: Request) -> MatchStateManager
def get_milestone_detector(request: Request) -> MilestoneDetector
def get_settings(request: Request) -> Settings

# Request models (Pydantic v2)
class PredictionCreate(BaseModel):   # momento: int = Field(ge=1, le=6); content: str
class MockAvanzarRequest(BaseModel): # momento: int = Field(ge=1, le=6)
class MockSetMinuteRequest(BaseModel): # minute: int = Field(ge=0, le=130)

# match_state.py — additive constant
MOMENTO_STATUSES: dict[int, FixtureStatus] = {
    1: FixtureStatus(elapsed=15,  short="1H",  long="First Half"),
    2: FixtureStatus(elapsed=30,  short="1H",  long="First Half"),
    3: FixtureStatus(elapsed=45,  short="HT",  long="Halftime"),
    4: FixtureStatus(elapsed=60,  short="2H",  long="Second Half"),
    5: FixtureStatus(elapsed=75,  short="2H",  long="Second Half"),
    6: FixtureStatus(elapsed=120, short="PEN", long="Match Finished After Penalty"),
}
```

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | `poll_once`: success order (get_fixture→update_fixture→check_and_push); get_fixture failure (logged, no crash); check_and_push failure (logged, no crash) | Mock services with call trackers; `caplog` for error assertions. |
| Unit | `polling_loop`: cancellable via `task.cancel()` | `asyncio.create_task` + `cancel` + `await` with `suppress(CancelledError)`. |
| Unit | Lifespan: startup creates services + primes fixture; mock mode no task; shutdown cancels then closes clients | `httpx.AsyncClient(transport=ASGITransport(app))` driving the lifespan via `async with`. |
| Unit | 8 endpoints: health (mock+live), estado (200+500), contexto (text/plain+500), predicciones (list), prediccion (200+422), mock/avanzar (mock 200 + 422 + live 404), mock/set-minute (mock 200 + live 404), stats/requests (mock 0 + live N) | `test_app` with pre-populated `app.state` (no lifespan); `httpx.AsyncClient` + `ASGITransport`. |
| Unit | `MOMENTO_STATUSES`: all 6 keys map to correct `FixtureStatus` | Direct dict access. |
| Coverage | ≥70% on new code; existing 200 tests green | `cd backend && pytest` (asyncio_mode=auto, strict) |

## Migration / Rollout

No migration. Rollback = `git revert` — new files are additive; `MOMENTO_STATUSES` is additive; changes 1–2 services untouched. Per `config.yaml`, rollback plan required (touches polling loop): documented in proposal — `git revert` removes new files and restores `match_state.py`.

## Open Questions

None.
