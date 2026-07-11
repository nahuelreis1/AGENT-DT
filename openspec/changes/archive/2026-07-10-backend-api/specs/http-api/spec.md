# http-api Specification

## Purpose

FastAPI application exposing match state, context text, predictions, mock progression controls, and request statistics over HTTP. Mode-gated: `/mock/*` endpoints return 404 in live mode; all other endpoints work in both mock and live modes.

## Requirements

### Requirement: Health Check Endpoint

`GET /health` MUST return HTTP 200 with JSON body `{"status": "ok", "mode": "<mode>"}`. The `mode` value MUST reflect `Settings.MOCK_MODE` at request time (`"mock"` when true, `"live"` when false). This endpoint MUST respond in both modes.

#### Scenario: Health check in mock mode

- GIVEN `MOCK_MODE=true`
- WHEN `GET /health` is called
- THEN the response status is 200
- AND the JSON body is `{"status": "ok", "mode": "mock"}`

#### Scenario: Health check in live mode

- GIVEN `MOCK_MODE=false`
- WHEN `GET /health` is called
- THEN the response status is 200
- AND the JSON body is `{"status": "ok", "mode": "live"}`

### Requirement: Match State Endpoint

`GET /partido/estado` MUST return the current `MatchState` serialized as JSON (via `model_dump(mode="json")`). If the `MatchStateManager` is not initialized (raises `RuntimeError`), the endpoint MUST return HTTP 500. This endpoint MUST work in both mock and live modes.

#### Scenario: Returns serialized match state

- GIVEN the manager holds state with `fixture_id=868019`
- WHEN `GET /partido/estado` is called
- THEN the response status is 200
- AND the JSON body contains `fixture_id == 868019`

#### Scenario: Uninitialized manager returns 500

- GIVEN the manager was never initialized and raises `RuntimeError` on `get_state`
- WHEN `GET /partido/estado` is called
- THEN the response status is 500

### Requirement: Context Text Endpoint

`GET /partido/contexto` MUST return the 7-section context string with `Content-Type: text/plain; charset=utf-8`. If the manager is not initialized, the endpoint MUST return HTTP 500. This endpoint MUST work in both modes.

#### Scenario: Returns context as plain text

- GIVEN the manager holds initialized state
- WHEN `GET /partido/contexto` is called
- THEN the response status is 200
- AND the `Content-Type` header is `text/plain; charset=utf-8`
- AND the body is the 7-section context string

#### Scenario: Uninitialized manager returns 500

- GIVEN the manager raises `RuntimeError` on `get_context_text`
- WHEN `GET /partido/contexto` is called
- THEN the response status is 500

### Requirement: Predictions Endpoints

`GET /partido/predicciones` MUST return the saved `Prediction` list as JSON. `POST /partido/prediccion` MUST accept `{"momento": 1..6, "content": str}`, save it, and return `{"ok": true, "momento": N}` with HTTP 200. The POST MUST return HTTP 422 when `momento` is outside `1..6` or when `content` is empty. Both endpoints MUST work in both modes.

#### Scenario: GET returns saved predictions

- GIVEN two predictions saved with momenti 1 and 3
- WHEN `GET /partido/predicciones` is called
- THEN the response status is 200
- AND the JSON body is a list of two predictions

#### Scenario: POST saves a valid prediction

- GIVEN the manager is initialized
- WHEN `POST /partido/prediccion` is called with `{"momento": 2, "content": "Gol inminente"}`
- THEN the response status is 200
- AND the JSON body is `{"ok": true, "momento": 2}`

#### Scenario: POST rejects momento out of range

- GIVEN the manager is initialized
- WHEN `POST /partido/prediccion` is called with `{"momento": 7, "content": "x"}`
- THEN the response status is 422

#### Scenario: POST rejects empty content

- GIVEN the manager is initialized
- WHEN `POST /partido/prediccion` is called with `{"momento": 3, "content": ""}`
- THEN the response status is 422

### Requirement: Mock Avanzar Endpoint

`POST /mock/avanzar` accepts `{"momento": 1..6}`. In mock mode it MUST: update status via `MOMENTO_STATUSES`, fetch fixture details, update the manager state, fire the milestone detector, and return `{"momento": N, "status": "advanced"}` with HTTP 200. It MUST return HTTP 422 when `momento` is outside `1..6`. It MUST return HTTP 404 when `MOCK_MODE=false`.

#### Scenario: Advance to a momento in mock mode

- GIVEN `MOCK_MODE=true` and the manager initialized
- WHEN `POST /mock/avanzar` is called with `{"momento": 3}`
- THEN the response status is 200
- AND the JSON body is `{"momento": 3, "status": "advanced"}`
- AND the manager state reflects `MOMENTO_STATUSES[3]`

#### Scenario: Momento out of range in mock mode

- GIVEN `MOCK_MODE=true`
- WHEN `POST /mock/avanzar` is called with `{"momento": 9}`
- THEN the response status is 422

#### Scenario: Avanzar in live mode returns 404

- GIVEN `MOCK_MODE=false`
- WHEN `POST /mock/avanzar` is called with `{"momento": 3}`
- THEN the response status is 404

### Requirement: Mock Set-Minute Endpoint

`POST /mock/set-minute` accepts `{"minute": 0..130}`. In mock mode it MUST update only `status.elapsed` on the stored state and return `{"elapsed": N}` with HTTP 200. It MUST return HTTP 404 when `MOCK_MODE=false`. Other state fields MUST remain unchanged.

#### Scenario: Set minute in mock mode

- GIVEN `MOCK_MODE=true` and the manager initialized with `elapsed=0`
- WHEN `POST /mock/set-minute` is called with `{"minute": 67}`
- THEN the response status is 200
- AND the JSON body is `{"elapsed": 67}`
- AND only `status.elapsed` changed (other fields unchanged)

#### Scenario: Set-minute in live mode returns 404

- GIVEN `MOCK_MODE=false`
- WHEN `POST /mock/set-minute` is called with `{"minute": 67}`
- THEN the response status is 404

### Requirement: Request Stats Endpoint

`GET /stats/requests` MUST return `{"count": N}`. In mock mode `N` MUST be 0. In live mode `N` MUST equal `APIFootballClient.request_count`. This endpoint MUST work in both modes.

#### Scenario: Stats in mock mode

- GIVEN `MOCK_MODE=true`
- WHEN `GET /stats/requests` is called
- THEN the response status is 200
- AND the JSON body is `{"count": 0}`

#### Scenario: Stats in live mode

- GIVEN `MOCK_MODE=false` and the API client made 5 requests
- WHEN `GET /stats/requests` is called
- THEN the response status is 200
- AND the JSON body is `{"count": 5}`

### Requirement: Mode-Gating of Mock Routes

All routes under `/mock/*` MUST return HTTP 404 when `MOCK_MODE=false`. All non-mock routes MUST function identically in both mock and live modes.

#### Scenario: Mock routes 404 in live mode

- GIVEN `MOCK_MODE=false`
- WHEN any `/mock/*` route is called
- THEN the response status is 404

#### Scenario: Non-mock routes work in both modes

- GIVEN either `MOCK_MODE=true` or `MOCK_MODE=false`
- WHEN `/health`, `/partido/*`, or `/stats/*` routes are called
- THEN they respond normally (not 404 due to mode)
