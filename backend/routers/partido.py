"""HTTP router for the `partido` (match) surface.

Exposes the 8 endpoints defined in the `http-api` spec:
- GET  /health
- GET  /partido/estado
- GET  /partido/contexto
- GET  /partido/predicciones
- POST /partido/prediccion
- POST /mock/avanzar
- POST /mock/set-minute
- GET  /stats/requests

Dependency injection uses `request.app.state` + `Depends(get_*)` so
tests build a FastAPI app with a pre-populated `app.state` (no
lifespan needed). `/mock/*` routes return 404 when `MOCK_MODE=false`.

Spec: openspec/changes/backend-api/specs/http-api/spec.md
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from backend.config import Settings
from backend.data_source import DataSource, LiveDataSource
from backend.services.match_state import MOMENTO_STATUSES, MatchStateManager
from backend.services.milestones import MilestoneDetector

router = APIRouter()


# ---------------------------------------------------------------------------
# Request models (Pydantic v2) — Field constraints produce 422 on bad input.
# ---------------------------------------------------------------------------


class PredictionCreate(BaseModel):
    """POST /partido/prediccion body.

    `momento` is constrained to 1..6 (the 6 match snapshots); `content`
    is non-empty. The server stamps `now()` on save — the client cannot
    forge a timestamp.
    """

    momento: int = Field(ge=1, le=6)
    content: str = Field(min_length=1)


class MockAvanzarRequest(BaseModel):
    """POST /mock/avanzar body — the momento to advance to (0..6)."""

    momento: int = Field(ge=0, le=6)


class MockSetMinuteRequest(BaseModel):
    """POST /mock/set-minute body — the elapsed minutes (0..130)."""

    minute: int = Field(ge=0, le=130)


# ---------------------------------------------------------------------------
# Dependency injection — resolve services from `app.state` (no globals).
# ---------------------------------------------------------------------------


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_data_source(request: Request) -> DataSource:
    return request.app.state.data_source


def get_match_state(request: Request) -> MatchStateManager:
    return request.app.state.match_state


def get_milestone_detector(request: Request) -> MilestoneDetector:
    return request.app.state.milestone_detector


# ---------------------------------------------------------------------------
# GET /health — mode-aware health check
# ---------------------------------------------------------------------------


@router.get("/health")
async def health(settings: Settings = Depends(get_settings)):
    """Return `{"status": "ok", "mode": "<mock|live>"}`.

    The `mode` reflects `Settings.MOCK_MODE` at request time so an
    operator can tell which branch the process is running.
    """
    mode = "mock" if settings.MOCK_MODE else "live"
    return {"status": "ok", "mode": mode}


# ---------------------------------------------------------------------------
# GET /partido/estado — serialized match state (500 on uninit)
# ---------------------------------------------------------------------------


@router.get("/partido/estado")
async def estado(state: MatchStateManager = Depends(get_match_state)):
    """Return the current `MatchState` as JSON (`model_dump(mode="json")`).

    Returns HTTP 500 when the manager was never initialized (raises
    `RuntimeError` on `get_state`).
    """
    try:
        return state.get_state().model_dump(mode="json")
    except RuntimeError:
        raise HTTPException(status_code=500, detail="MatchState not initialized")


# ---------------------------------------------------------------------------
# GET /partido/contexto — 7-section context as text/plain (500 on uninit)
# ---------------------------------------------------------------------------


@router.get("/partido/contexto")
async def contexto(state: MatchStateManager = Depends(get_match_state)):
    """Return the 7-section context string as `text/plain; charset=utf-8`.

    The context is natural-language text (not JSON) — n8n consumes the
    raw body. Returns HTTP 500 when the manager is uninitialized.
    """
    try:
        text = state.get_context_text()
    except RuntimeError:
        raise HTTPException(status_code=500, detail="MatchState not initialized")
    return Response(content=text, media_type="text/plain; charset=utf-8")


# ---------------------------------------------------------------------------
# GET /partido/predicciones — saved predictions as a JSON list
# ---------------------------------------------------------------------------


@router.get("/partido/predicciones")
async def predicciones(state: MatchStateManager = Depends(get_match_state)):
    """Return the saved `Prediction` list as JSON.

    `get_predictions()` never raises on an uninitialized manager (it
    returns the empty list), so there is no 500 path here.
    """
    return [p.model_dump(mode="json") for p in state.get_predictions()]


# ---------------------------------------------------------------------------
# POST /partido/prediccion — save a prediction (422 on bad momento/content)
# ---------------------------------------------------------------------------


@router.post("/partido/prediccion")
async def prediccion(
    body: PredictionCreate,
    state: MatchStateManager = Depends(get_match_state),
):
    """Save a prediction and return `{"ok": true, "momento": N}`.

    Pydantic validates `momento` (1..6) and `content` (non-empty) before
    the handler runs — out-of-range or empty values produce HTTP 422.
    """
    state.save_prediction(body.momento, body.content)
    return {"ok": True, "momento": body.momento}


# ---------------------------------------------------------------------------
# POST /mock/avanzar — advance to a momento (404 in live mode, 422 on bad m)
# ---------------------------------------------------------------------------


@router.post("/mock/avanzar")
async def mock_avanzar(
    body: MockAvanzarRequest,
    settings: Settings = Depends(get_settings),
    data_source: DataSource = Depends(get_data_source),
    state: MatchStateManager = Depends(get_match_state),
    detector: MilestoneDetector = Depends(get_milestone_detector),
):
    """Advance the mock match to `momento` (1..6).

    Mock mode only — returns 404 when `MOCK_MODE=false`. Steps:
    set the state status from `MOMENTO_STATUSES`, fetch per-momento
    details and update the manager, then fire the milestone detector.
    """
    if not settings.MOCK_MODE:
        raise HTTPException(status_code=404, detail="Mock endpoints are not available in live mode")

    state.get_state().status = MOMENTO_STATUSES[body.momento]
    events, home_stats, away_stats, home_players, away_players = (
        await data_source.get_details(body.momento)
    )
    state.update_details(events, home_stats, away_stats, home_players, away_players)
    await detector.check_and_push()
    return {"momento": body.momento, "status": "advanced"}


# ---------------------------------------------------------------------------
# POST /mock/set-minute — set elapsed minutes (404 in live mode)
# ---------------------------------------------------------------------------


@router.post("/mock/set-minute")
async def mock_set_minute(
    body: MockSetMinuteRequest,
    settings: Settings = Depends(get_settings),
    state: MatchStateManager = Depends(get_match_state),
):
    """Update ONLY `status.elapsed` on the stored state.

    Mock mode only — returns 404 when `MOCK_MODE=false`. No details
    fetch, no milestone check: this is a fine-grained minute override
    that leaves every other state field untouched.
    """
    if not settings.MOCK_MODE:
        raise HTTPException(status_code=404, detail="Mock endpoints are not available in live mode")

    state.get_state().status.elapsed = body.minute
    return {"elapsed": body.minute}


# ---------------------------------------------------------------------------
# GET /stats/requests — request counter (mock 0, live N)
# ---------------------------------------------------------------------------


@router.get("/stats/requests")
async def stats_requests(data_source: DataSource = Depends(get_data_source)):
    """Return `{"count": N}`.

    Mock mode returns 0 (no live API calls). Live mode returns
    `APIFootballClient.request_count` via `LiveDataSource._client`.
    """
    if isinstance(data_source, LiveDataSource):
        return {"count": data_source._client.request_count}
    return {"count": 0}
