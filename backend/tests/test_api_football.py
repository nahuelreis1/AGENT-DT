"""Tests for `APIFootballClient` — the httpx wrapper that talks to
API-Football v3 and tracks per-process request count for the
free-tier budget guard.

Uses `respx` to intercept httpx calls so we exercise the real
`_get` → `raise_for_status` → `resp.json` → `response` envelope path
without touching the network. The base URL is `https://v3.football.api-sports.io/`
per the API-Football v3 docs.

The client's responsibilities, per the design:
- Single `httpx.AsyncClient` instance created in `__init__`.
- `_get` increments `request_count` and warns at 80 and 100.
- `fetch_*` helpers each return the `response` array (or `{}` for
  empty `fetch_fixture`).
- `aclose` shuts the client down.

Covers every scenario in
`openspec/changes/backend-services/specs/api-football-client/spec.md`
plus triangulation cases for the empty-response path and the
`aclose` lifecycle.
"""
from __future__ import annotations

import logging

import httpx
import pytest
import respx

from backend.services.api_football import APIFootballClient


BASE_URL = "https://v3.football.api-sports.io/"


# ---------------------------------------------------------------------------
# Helpers — build v3 envelopes and respx routes for the test body.
# ---------------------------------------------------------------------------


def v3_envelope(response: list | dict) -> dict:
    """Wrap a v3 response payload in the standard API-Football envelope.

    The client only reads the `response` key, but the full envelope is
    closer to the real API shape and easier to assert against in the
    tests.
    """
    return {
        "get": "fixtures",
        "parameters": {},
        "errors": [],
        "results": len(response) if isinstance(response, list) else 1,
        "paging": {"current": 1, "total": 1},
        "response": response,
    }


def fake_fixture_response() -> list[dict]:
    """Return a minimal /fixtures response array (one element)."""
    return [
        {
            "fixture": {
                "id": 868019,
                "status": {"elapsed": 15, "short": "1H", "long": "First Half"},
            },
            "teams": {
                "home": {"id": 26, "name": "Argentina"},
                "away": {"id": 33, "name": "Netherlands"},
            },
            "goals": {"home": 0, "away": 0},
        }
    ]


# ---------------------------------------------------------------------------
# Requirement: fetch_fixture returns response[0]
# ---------------------------------------------------------------------------


class TestFetchFixture:
    @respx.mock
    async def test_fetch_fixture_returns_first_element_of_response(self):
        """Spec: 'fetch_fixture returns the first element of `response`'.

        When the API envelope's `response` is a non-empty list, the
        helper MUST return `response[0]`. We pin the value with a
        specific dict (one fixture) and assert identity.
        """
        payload = fake_fixture_response()
        respx.get(f"{BASE_URL}fixtures").mock(
            return_value=httpx.Response(200, json=v3_envelope(payload))
        )

        client = APIFootballClient(api_key="test-key")
        try:
            result = await client.fetch_fixture(868019)

        finally:
            await client.aclose()

        assert result == payload[0]

    @respx.mock
    async def test_fetch_fixture_with_empty_response_returns_empty_dict(self):
        """Spec: 'fetch_fixture with empty response returns {}'.

        When the API returns no fixtures, the client MUST NOT crash
        with an `IndexError` — it returns an empty dict so the
        downstream parser can short-circuit cleanly.
        """
        respx.get(f"{BASE_URL}fixtures").mock(
            return_value=httpx.Response(200, json=v3_envelope([]))
        )

        client = APIFootballClient(api_key="test-key")
        try:
            result = await client.fetch_fixture(0)

        finally:
            await client.aclose()

        assert result == {}


# ---------------------------------------------------------------------------
# Requirement: fetch_events / fetch_statistics / fetch_players
# ---------------------------------------------------------------------------


class TestFetchCollectionEndpoints:
    @respx.mock
    async def test_fetch_events_returns_full_response_list(self):
        """Spec: 'fetch_events returns the `response` list'.

        Events are returned as-is. The fixture pins two events so we
        can verify the list is passed through untouched.
        """
        events = [
            {"time": {"elapsed": 35}, "team": {"name": "Argentina"}, "type": "Goal", "detail": "Normal Goal", "player": {"name": "N. Molina"}, "assist": {"name": "L. Messi"}},
            {"time": {"elapsed": 73}, "team": {"name": "Netherlands"}, "type": "Goal", "detail": "Normal Goal", "player": {"name": "W. Weghorst"}, "assist": None},
        ]
        respx.get(f"{BASE_URL}fixtures/events").mock(
            return_value=httpx.Response(200, json=v3_envelope(events))
        )

        client = APIFootballClient(api_key="test-key")
        try:
            result = await client.fetch_events(868019)

        finally:
            await client.aclose()

        assert result == events

    @respx.mock
    async def test_fetch_statistics_returns_full_response_list(self):
        """Spec: 'fetch_statistics returns the `response` list`.

        Two team blocks, one for each side.
        """
        stats = [
            {"team": {"name": "Argentina"}, "statistics": [{"type": "Ball Possession", "value": "55%"}]},
            {"team": {"name": "Netherlands"}, "statistics": [{"type": "Ball Possession", "value": "45%"}]},
        ]
        respx.get(f"{BASE_URL}fixtures/statistics").mock(
            return_value=httpx.Response(200, json=v3_envelope(stats))
        )

        client = APIFootballClient(api_key="test-key")
        try:
            result = await client.fetch_statistics(868019)

        finally:
            await client.aclose()

        assert result == stats

    @respx.mock
    async def test_fetch_players_returns_full_response_list(self):
        """Spec: 'fetch_players returns the `response` list`.

        Two team blocks; we don't expand the player shape here — the
        client only ships the list through, parsing is downstream.
        """
        players = [
            {"team": {"name": "Argentina"}, "players": []},
            {"team": {"name": "Netherlands"}, "players": []},
        ]
        respx.get(f"{BASE_URL}fixtures/players").mock(
            return_value=httpx.Response(200, json=v3_envelope(players))
        )

        client = APIFootballClient(api_key="test-key")
        try:
            result = await client.fetch_players(868019)

        finally:
            await client.aclose()

        assert result == players


# ---------------------------------------------------------------------------
# Requirement: request_count tracking + free-tier budget warnings
# ---------------------------------------------------------------------------


class TestRequestCount:
    async def test_request_count_starts_at_zero(self):
        """Spec: 'request_count starts at 0'.

        A freshly-constructed client has not made any calls yet.
        """
        client = APIFootballClient(api_key="test-key")
        await client.aclose()

        assert client.request_count == 0

    @respx.mock
    async def test_request_count_increments_per_call(self):
        """Spec: 'request_count increments on every call`.

        The design says `_get` increments the counter once per call,
        so a sequence of 3 endpoints should land on 3. We hit
        `fetch_fixture` 3 times to keep the test focused.
        """
        respx.get(f"{BASE_URL}fixtures").mock(
            return_value=httpx.Response(200, json=v3_envelope(fake_fixture_response()))
        )

        client = APIFootballClient(api_key="test-key")
        try:
            await client.fetch_fixture(868019)
            assert client.request_count == 1
            await client.fetch_fixture(868019)
            assert client.request_count == 2
            await client.fetch_fixture(868019)
            assert client.request_count == 3

        finally:
            await client.aclose()

    @respx.mock
    async def test_warning_logged_at_request_80_and_100(self, caplog):
        """Spec: 'WARNING logged at request count 80 and 100'.

        The free-tier budget is 100/day. The client warns the operator
        when crossing 80 (early heads-up) and again at 100 (at-the-
        limit). 79 and 99 must NOT warn.
        """
        # Stub any 200 response — the warnings fire on the counter, not
        # on the response shape.
        respx.get(f"{BASE_URL}fixtures").mock(
            return_value=httpx.Response(200, json=v3_envelope(fake_fixture_response()))
        )

        client = APIFootballClient(api_key="test-key")
        try:
            with caplog.at_level(logging.WARNING, logger="backend.services.api_football"):
                # Drive 100 calls; the 80th and 100th are the warning
                # points.
                for _ in range(100):
                    await client.fetch_fixture(868019)

        finally:
            await client.aclose()

        # Exactly two warnings: 80 and 100. No warning at 79 or 99.
        warning_messages = [
            record.message
            for record in caplog.records
            if record.levelno == logging.WARNING
        ]
        assert len(warning_messages) == 2, f"expected 2 warnings, got {warning_messages}"
        assert "80" in warning_messages[0]
        assert "100" in warning_messages[1]


# ---------------------------------------------------------------------------
# Requirement: HTTP error handling
# ---------------------------------------------------------------------------


class TestHttpErrorHandling:
    @respx.mock
    async def test_4xx_response_raises_http_status_error(self):
        """Spec: 'Non-2xx response raises httpx.HTTPStatusError'.

        A 401 (invalid key) MUST propagate as `HTTPStatusError`, NOT
        be swallowed and returned as `[]`. Downstream code needs the
        failure to be loud.
        """
        respx.get(f"{BASE_URL}fixtures").mock(
            return_value=httpx.Response(401, json={"errors": ["invalid key"]})
        )

        client = APIFootballClient(api_key="bad-key")
        try:
            with pytest.raises(httpx.HTTPStatusError):
                await client.fetch_fixture(868019)

        finally:
            await client.aclose()

    @respx.mock
    async def test_5xx_response_raises_http_status_error(self):
        """Spec: 'Server error raises httpx.HTTPStatusError'.

        A 500 from API-Football surfaces as `HTTPStatusError` so the
        polling loop can decide to back off.
        """
        respx.get(f"{BASE_URL}fixtures").mock(
            return_value=httpx.Response(500, json={"errors": ["server error"]})
        )

        client = APIFootballClient(api_key="test-key")
        try:
            with pytest.raises(httpx.HTTPStatusError):
                await client.fetch_fixture(868019)

        finally:
            await client.aclose()

    @respx.mock
    async def test_network_error_raises_request_error(self):
        """Spec: 'Connection failure raises httpx.RequestError'.

        respx simulates a network-level failure via `side_effect=...`.
        The client does NOT retry — it propagates so the caller can
        decide.
        """
        respx.get(f"{BASE_URL}fixtures").mock(
            side_effect=httpx.ConnectError("simulated connection refused")
        )

        client = APIFootballClient(api_key="test-key")
        try:
            with pytest.raises(httpx.RequestError):
                await client.fetch_fixture(868019)

        finally:
            await client.aclose()


# ---------------------------------------------------------------------------
# Requirement: aclose lifecycle
# ---------------------------------------------------------------------------


class TestAclose:
    async def test_aclose_closes_client(self):
        """Spec: 'aclose shuts down the underlying httpx client'.

        After `aclose`, a subsequent request through the same client
        raises `RuntimeError` from httpx (the client is closed).
        We don't pin the exact exception type — just that the client
        is no longer usable.
        """
        client = APIFootballClient(api_key="test-key")

        await client.aclose()

        with pytest.raises(RuntimeError):
            await client._client.get(f"{BASE_URL}fixtures")


# ---------------------------------------------------------------------------
# Requirement: fetch_lineups (fifth fetch method + 204 handling)
# ---------------------------------------------------------------------------


class TestFetchLineups:
    @respx.mock
    async def test_fetch_lineups_200_returns_response_list_and_increments_count(self):
        """Spec: 'fetch_lineups returns the response list' + request_count++."""
        lineups = [
            {"team": {"name": "Argentina"}, "formation": "4-3-3", "startXI": [], "substitutes": []},
            {"team": {"name": "Netherlands"}, "formation": "3-4-1-2", "startXI": [], "substitutes": []},
        ]
        respx.get(f"{BASE_URL}fixtures/lineups").mock(
            return_value=httpx.Response(200, json=v3_envelope(lineups))
        )

        client = APIFootballClient(api_key="test-key")
        try:
            result = await client.fetch_lineups(868019)
            assert result == lineups
            assert client.request_count == 1
        finally:
            await client.aclose()

    @respx.mock
    async def test_fetch_lineups_204_returns_empty_list_without_raising(self):
        """Spec: 'fetch_lineups 204 returns empty list without raising'.

        A 204 (no content) means lineups are not yet published. The
        method MUST return [] (NOT raise HTTPStatusError) so the
        caller can treat it as (None, None) after parsing.
        """
        respx.get(f"{BASE_URL}fixtures/lineups").mock(
            return_value=httpx.Response(204)
        )

        client = APIFootballClient(api_key="test-key")
        try:
            result = await client.fetch_lineups(868019)
            assert result == []
            assert client.request_count == 1
        finally:
            await client.aclose()

    @respx.mock
    async def test_fetch_lineups_4xx_raises_http_status_error(self):
        """Spec: 4xx response raises HTTPStatusError (shared with other endpoints)."""
        respx.get(f"{BASE_URL}fixtures/lineups").mock(
            return_value=httpx.Response(401, json={"errors": ["invalid key"]})
        )

        client = APIFootballClient(api_key="bad-key")
        try:
            with pytest.raises(httpx.HTTPStatusError):
                await client.fetch_lineups(868019)
        finally:
            await client.aclose()
