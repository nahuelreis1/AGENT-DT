# Tasks: Backend API

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~800 |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes (2 PRs) |
| Suggested split | PR1 router+endpoints → PR2 main+lifespan+polling |
| Delivery strategy | ask-always |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: Medium

## Phase 1: PR1 Foundation — PR1
- [x] 1.1 Create `routers/__init__.py` empty + `routers/partido.py` `router=APIRouter()` stub
- [x] 1.2 RED `test_momento_statuses_all_six` (6 keys→FixtureStatus)
- [x] 1.3 GREEN add `MOMENTO_STATUSES: dict[int,FixtureStatus]` in `services/match_state.py`

## Phase 2: PR1 Health + Conftest — PR1
- [x] 2.1 RED `test_health_mock` + `test_health_live` (`/health` 200+mode)
- [x] 2.2 GREEN conftest: `mock_settings`/`live_settings`/`mock_ds`/`live_ds`(`_client.request_count=0`)/`mock_state`/`live_state`/`mock_app`/`live_app`/`mock_client`/`live_client`; `routers/partido.py`: `GET /health` + `Depends(get_settings)`

## Phase 3: PR1 Endpoints (estado+contexto+preds+mock+stats) — PR1
- [x] 3.1 RED `test_estado_ok` (200, `fixture_id=868019`) + `test_estado_uninit_500`
- [x] 3.2 GREEN `GET /partido/estado`→`state.model_dump("json")`; `RuntimeError`→500; `Depends(get_match_state)`
- [x] 3.3 RED `test_contexto_ok` (`text/plain; charset=utf-8`+7-section) + `test_contexto_uninit_500`
- [x] 3.4 GREEN `GET /partido/contexto`→`Response(text, media_type="text/plain; charset=utf-8")`
- [x] 3.5 RED `test_preds_get` (seed 2 preds→list of 2)
- [x] 3.6 GREEN `GET /partido/predicciones`→`[p.model_dump("json") for p in mgr.get_predictions()]`
- [x] 3.7 RED `test_pred_valid` (200, `{ok:true,momento:2}`) + `_momento_oor_422` + `_empty_422`; `PredictionCreate` `Field(ge=1,le=6)`+`min_length=1`
- [x] 3.8 GREEN `POST /partido/prediccion`→`manager.save_prediction(m,content)`; Pydantic 422
- [x] 3.9 RED `test_mock_avanzar_mock` (200, status=MS[3]) + `_oor_422` + `_live_404`; `MockAvanzarRequest` `Field(ge=1,le=6)`
- [x] 3.10 GREEN `POST /mock/avanzar` 404 if `not MOCK_MODE`; else `state.status=MS[m]`, `get_details(m)`→`update_details`→`check_and_push`
- [x] 3.11 RED `test_mock_set_minute_mock` (200, only `elapsed` changed) + `_live_404`; `MockSetMinuteRequest` `Field(ge=0,le=130)`
- [x] 3.12 GREEN `POST /mock/set-minute`→`state.status.elapsed=minute` (404 if live)
- [x] 3.13 RED `test_stats_mock_zero` + `test_stats_live_count` (mock `_client.request_count=5`)
- [x] 3.14 GREEN `GET /stats/requests`: `isinstance(LD)`→`{count:N}`, else `{count:0}`

## Phase 4: PR1 Integration — PR1
- [x] 4.1 `cd backend && pytest` — 200 + PR1 PASS; coverage ≥70% on new code

## Phase 5: PR2 Polling — PR2
- [x] 5.1 RED `test_poll_once_success_order` (asserts `get_fixture→update_fixture→check_and_push` with `AsyncMock`)
- [x] 5.2 GREEN `async def poll_once(data_source, match_state, detector)` in `main.py`
- [x] 5.3 RED `test_poll_once_get_fixture_logged` + `test_poll_once_check_push_logged` (caplog; logged+no raise)
- [x] 5.4 GREEN wrap each call in `try/except Exception: log.exception(...)`
- [x] 5.5 RED `test_polling_loop_cancellable` (spawn task, cancel, completes)
- [x] 5.6 GREEN `async def polling_loop(..., interval)` `while True: await poll_once(); await asyncio.sleep(interval)`

## Phase 6: PR2 Lifespan + Wiring — PR2
- [x] 6.1 RED `test_lifespan_live_starts_polling` (`AsyncClient(ASGITransport(app))`+`async with`; `app.state.{config,ds,ms,detector,task}` set+task running)
- [x] 6.2 GREEN `lifespan(app)`: Settings, `create_data_source`, `MatchStateManager` primed `get_fixture()→update_fixture()`, `MilestoneDetector(...)`; if `not MOCK_MODE`: `polling_task=asyncio.create_task(polling_loop(...))`; yield
- [x] 6.3 RED `test_lifespan_mock_no_polling_task` (`polling_task is None`; covered by 6.2)
- [x] 6.4 RED `test_shutdown_order_live` (`AsyncMock.await_args_list`: `cancel→await→detector.aclose→client.aclose`)
- [x] 6.5 GREEN after yield: `task.cancel(); suppress(CancelledError); await task; await detector.aclose(); if not MOCK_MODE: await client.aclose()`
- [x] 6.6 RED `test_app_imports_and_includes_router` (imports `app`; 8 routes present)
- [x] 6.7 GREEN `app = FastAPI(lifespan=lifespan); app.include_router(partido.router)`

## Phase 7: PR2 Integration — PR2
- [x] 7.1 `cd backend && pytest` — 200 + PR1 + PR2 PASS; coverage ≥70% new code
