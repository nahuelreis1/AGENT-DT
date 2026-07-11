"""Tests for the `partido` router — the 8 HTTP endpoints defined in
the `http-api` spec.

Dependency injection uses `request.app.state` + `Depends(get_*)`, so
every test drives a FastAPI app whose `app.state` is pre-populated by
the `mock_app`/`live_app` fixtures in `conftest.py` — no lifespan runs.

Covers every scenario in
`openspec/changes/backend-api/specs/http-api/spec.md` plus
triangulation cases for the 422/500/404 paths and the mock/live
mode-gating.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# GET /health — mode-aware health check
# ---------------------------------------------------------------------------


class TestHealth:
    async def test_health_mock(self, mock_client):
        """Spec: GIVEN MOCK_MODE=true, GET /health returns 200 with
        `{"status": "ok", "mode": "mock"}`.
        """
        resp = await mock_client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok", "mode": "mock"}

    async def test_health_live(self, live_client):
        """Spec: GIVEN MOCK_MODE=false, GET /health returns 200 with
        `{"status": "ok", "mode": "live"}`.
        """
        resp = await live_client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok", "mode": "live"}


# ---------------------------------------------------------------------------
# GET /partido/estado — serialized match state (200 + 500 on uninit)
# ---------------------------------------------------------------------------


class TestEstado:
    async def test_estado_ok(self, mock_client):
        """Spec: GIVEN the manager holds state with fixture_id=868019,
        GET /partido/estado returns 200 and the JSON body contains
        `fixture_id == 868019`.
        """
        resp = await mock_client.get("/partido/estado")
        assert resp.status_code == 200
        body = resp.json()
        assert body["fixture_id"] == 868019

    async def test_estado_uninit_500(self, uninit_client):
        """Spec: GIVEN the manager was never initialized and raises
        `RuntimeError` on `get_state`, GET /partido/estado returns 500.
        """
        resp = await uninit_client.get("/partido/estado")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# GET /partido/contexto — 7-section context as text/plain (200 + 500)
# ---------------------------------------------------------------------------


class TestContexto:
    async def test_contexto_ok(self, mock_client):
        """Spec: GIVEN the manager holds initialized state, GET
        /partido/contexto returns 200 with `Content-Type:
        text/plain; charset=utf-8` and the 9-section context body.
        """
        resp = await mock_client.get("/partido/contexto")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/plain; charset=utf-8"
        text = resp.text
        # All 9 section markers present (Header, Formaciones, Goals, Stats,
        # Standout, Weak, All Players, Substitutions, Cards).
        assert "⚽" in text
        assert "FORMACIONES:" in text
        assert "GOLES:" in text
        assert "ESTADÍSTICAS:" in text
        assert "JUGADORES DESTACADOS" in text
        assert "JUGADORES FLOJOS" in text
        assert "TODOS LOS JUGADORES" in text
        assert "CAMBIOS REALIZADOS:" in text
        assert "TARJETAS:" in text
        # 9 sections separated by 8 blank lines, one trailing newline.
        assert text.count("\n\n") == 8
        assert text.endswith("\n")

    async def test_contexto_uninit_500(self, uninit_client):
        """Spec: GIVEN the manager raises `RuntimeError` on
        `get_context_text`, GET /partido/contexto returns 500.
        """
        resp = await uninit_client.get("/partido/contexto")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# GET /partido/predicciones — saved predictions as a JSON list
# ---------------------------------------------------------------------------


class TestPrediccionesGet:
    async def test_preds_get(self, mock_client, mock_state):
        """Spec: GIVEN two predictions saved with momenti 1 and 3,
        GET /partido/predicciones returns 200 and a list of two
        predictions (in append order).
        """
        mock_state.save_prediction(1, "Gol inminente")
        mock_state.save_prediction(3, "Cambio de momento")
        resp = await mock_client.get("/partido/predicciones")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) == 2
        assert body[0]["momento"] == 1
        assert body[0]["content"] == "Gol inminente"
        assert body[1]["momento"] == 3
        assert body[1]["content"] == "Cambio de momento"


# ---------------------------------------------------------------------------
# POST /partido/prediccion — save a prediction (200 + 422 on bad input)
# ---------------------------------------------------------------------------


class TestPrediccionPost:
    async def test_pred_valid(self, mock_client, mock_state):
        """Spec: GIVEN the manager is initialized, POST
        /partido/prediccion with `{"momento": 2, "content": "Gol inminente"}`
        returns 200 and `{"ok": true, "momento": 2}`, and the prediction
        is actually saved in the manager.
        """
        resp = await mock_client.post(
            "/partido/prediccion",
            json={"momento": 2, "content": "Gol inminente"},
        )
        assert resp.status_code == 200
        assert resp.json() == {"ok": True, "momento": 2}
        # Triangulation: the prediction reached the manager's log.
        preds = mock_state.get_predictions()
        assert len(preds) == 1
        assert preds[0].momento == 2
        assert preds[0].content == "Gol inminente"

    async def test_pred_momento_oor_422(self, mock_client):
        """Spec: POST /partido/prediccion with momento 7 (>6) returns 422."""
        resp = await mock_client.post(
            "/partido/prediccion",
            json={"momento": 7, "content": "x"},
        )
        assert resp.status_code == 422

    async def test_pred_empty_422(self, mock_client):
        """Spec: POST /partido/prediccion with empty content returns 422."""
        resp = await mock_client.post(
            "/partido/prediccion",
            json={"momento": 3, "content": ""},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /mock/avanzar — advance to a momento (mock 200 + 422 + live 404)
# ---------------------------------------------------------------------------


class TestMockAvanzar:
    async def test_mock_avanzar_mock(self, mock_client, mock_state):
        """Spec: GIVEN MOCK_MODE=true and the manager initialized, POST
        /mock/avanzar with `{"momento": 3}` returns 200 with
        `{"momento": 3, "status": "advanced"}` and the manager state
        reflects `MOMENTO_STATUSES[3]` (elapsed=45, short="HT").
        """
        resp = await mock_client.post("/mock/avanzar", json={"momento": 3})
        assert resp.status_code == 200
        assert resp.json() == {"momento": 3, "status": "advanced"}
        # Triangulation: the stored state reflects MOMENTO_STATUSES[3].
        status = mock_state.get_state().status
        assert status.elapsed == 45
        assert status.short == "HT"

    async def test_mock_avanzar_oor_422(self, mock_client):
        """Spec: POST /mock/avanzar with momento 9 (>6) returns 422."""
        resp = await mock_client.post("/mock/avanzar", json={"momento": 9})
        assert resp.status_code == 422

    async def test_mock_avanzar_live_404(self, live_client):
        """Spec: GIVEN MOCK_MODE=false, POST /mock/avanzar returns 404."""
        resp = await live_client.post("/mock/avanzar", json={"momento": 3})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /mock/set-minute — set elapsed minutes (mock 200 + live 404)
# ---------------------------------------------------------------------------


class TestMockSetMinute:
    async def test_mock_set_minute_mock(self, mock_client, mock_state):
        """Spec: GIVEN MOCK_MODE=true and the manager initialized with
        elapsed=0, POST /mock/set-minute with `{"minute": 67}` returns
        200 with `{"elapsed": 67}` and ONLY `status.elapsed` changes
        (every other state field stays identical).
        """
        before = mock_state.get_state().model_dump(mode="json")
        resp = await mock_client.post("/mock/set-minute", json={"minute": 67})
        assert resp.status_code == 200
        assert resp.json() == {"elapsed": 67}
        after = mock_state.get_state().model_dump(mode="json")
        assert after["status"]["elapsed"] == 67
        # Triangulation: the entire state dict except status.elapsed is
        # byte-for-byte identical to the pre-request snapshot.
        expected_after = {**before, "status": {**before["status"], "elapsed": 67}}
        assert after == expected_after

    async def test_mock_set_minute_live_404(self, live_client):
        """Spec: GIVEN MOCK_MODE=false, POST /mock/set-minute returns 404."""
        resp = await live_client.post("/mock/set-minute", json={"minute": 67})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /stats/requests — request counter (mock 0 + live N)
# ---------------------------------------------------------------------------


class TestStatsRequests:
    async def test_stats_mock_zero(self, mock_client):
        """Spec: GIVEN MOCK_MODE=true, GET /stats/requests returns 200
        with `{"count": 0}` (mock mode never hits the live API).
        """
        resp = await mock_client.get("/stats/requests")
        assert resp.status_code == 200
        assert resp.json() == {"count": 0}

    async def test_stats_live_count(self, live_client):
        """Spec: GIVEN MOCK_MODE=false and the API client made 5
        requests, GET /stats/requests returns 200 with `{"count": 5}`.
        """
        resp = await live_client.get("/stats/requests")
        assert resp.status_code == 200
        assert resp.json() == {"count": 5}
