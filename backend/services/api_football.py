"""HTTP client for the API-Football v3 endpoint.

`APIFootballClient` is the only module in the backend that talks to
the upstream API. It owns a single `httpx.AsyncClient`, tracks the
number of requests made since construction, and exposes four `fetch_*`
helpers (one per endpoint the live data source needs).

Free-tier safety:
- API-Football's free plan caps at 100 requests/day. The client
  warns at 80 (early heads-up) and at 100 (at-the-limit) via the
  `backend.services.api_football` logger. The warnings are
  operational signals, not rate-limit enforcers — the caller is
  responsible for backing off.

Envelope:
- Every response is wrapped in a v3 envelope:
  `{"get", "parameters", "errors", "results", "paging", "response"}`.
  This client only reads `response`. The parsers in
  `backend.parsers` handle the inner shape.

Lifecycle:
- `aclose` shuts the underlying `httpx.AsyncClient`. Callers MUST
  invoke it on shutdown (FastAPI lifespan in change 3).

Spec: openspec/changes/backend-services/specs/api-football-client/spec.md
"""
from __future__ import annotations

import logging

import httpx

log = logging.getLogger(__name__)


class APIFootballClient:
    """Async HTTP client for API-Football v3, with request tracking.

    Construction is cheap (no network I/O). The first call to a
    `fetch_*` method triggers the underlying `httpx.AsyncClient` to
    resolve the base URL and establish a connection pool lazily.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://v3.football.api-sports.io/",
        timeout: float = 10.0,
    ) -> None:
        """Store the API key and create the internal `httpx.AsyncClient`.

        `api_key` is sent as the `x-apisports-key` header on every
        request. `base_url` is configurable for tests; production
        callers accept the default.
        """
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"x-apisports-key": api_key},
            timeout=timeout,
        )
        self._request_count = 0

    @property
    def request_count(self) -> int:
        """Return the number of HTTP requests made since construction."""
        return self._request_count

    async def _get(self, endpoint: str, params: dict) -> dict | list:
        """GET one endpoint, increment the counter, return the v3 `response`.

        Free-tier budget warnings fire at 80 and 100 requests. Non-2xx
        responses raise `httpx.HTTPStatusError` (via
        `raise_for_status`); network failures raise
        `httpx.RequestError`. Neither is caught here — the polling
        loop decides what to do with them.
        """
        self._request_count += 1
        if self._request_count in (80, 100):
            log.warning(
                "API-Football request count: %d (free-tier budget = 100)",
                self._request_count,
            )
        resp = await self._client.get(endpoint, params=params)
        resp.raise_for_status()
        # 204 No Content — the /fixtures/lineups endpoint returns 204
        # when lineups are not yet published (pre-kickoff). Return an
        # empty list so the caller can treat it as (None, None) after
        # parsing. This is harmless to other endpoints (they never
        # return 204 with a successful body).
        if resp.status_code == 204:
            return []
        data = resp.json()
        return data.get("response", [])

    async def fetch_fixture(self, fixture_id: int) -> dict:
        """Return the single fixture object for `fixture_id`.

        The /fixtures endpoint returns a list (zero or one element
        for an exact id query). Empty list → empty dict so the
        downstream `parse_fixture` is never called with no input.
        """
        resp = await self._get("/fixtures", {"id": fixture_id})
        return resp[0] if resp else {}

    async def fetch_events(self, fixture_id: int) -> list[dict]:
        """Return the events list for `fixture_id` (parsed downstream)."""
        return await self._get("/fixtures/events", {"fixture": fixture_id})

    async def fetch_statistics(self, fixture_id: int) -> list[dict]:
        """Return the per-team statistics list for `fixture_id`."""
        return await self._get("/fixtures/statistics", {"fixture": fixture_id})

    async def fetch_players(self, fixture_id: int) -> list[dict]:
        """Return the per-team players list for `fixture_id`."""
        return await self._get("/fixtures/players", {"fixture": fixture_id})

    async def fetch_lineups(self, fixture_id: int) -> list[dict]:
        """Return the per-team lineups list for `fixture_id`.

        The /fixtures/lineups endpoint returns 204 (no content) when
        lineups are not yet published. The shared ``_get`` handles this
        by returning ``[]`` so the caller can pipe it through
        ``parse_lineups`` → ``(None, None)``.
        """
        return await self._get("/fixtures/lineups", {"fixture": fixture_id})

    async def aclose(self) -> None:
        """Close the underlying `httpx.AsyncClient`. Idempotent."""
        await self._client.aclose()
