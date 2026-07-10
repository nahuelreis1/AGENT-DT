"""6-trigger milestone detector that pushes context snapshots to n8n.

`MilestoneDetector` is the "when do we wake up and call n8n?" seam.
It owns a `_fired` set so each of the 6 momenti (15', 30', HT, 60',
75', FT) fires at most once per process. On every fire it:

1. Asks the `DataSource` for the per-momento details.
2. Updates the in-memory `MatchStateManager` with those details.
3. Builds the 7-section context text.
4. POSTs the payload to `{N8N_WEBHOOK_BASE_URL}/webhook/momento`.

The trigger matrix is a module-level list of `(momento, condition,
guard)` tuples — the condition checks the time/state, the guard
narrows the trigger to the correct game phase (1H, HT, 2H, FT).
This is the same shape as the design's `TRIGGER_MATRIX` and is the
single source of truth for the firing rules.

Resilience:
- An empty `n8n_url` makes the detector a no-op (logged at info).
- A POST failure is logged at error and the momento is still marked
  fired — we do NOT retry, but we also do not throw away the
  schedule.
- Injected `http_client` is preserved (caller owns the lifecycle);
  the default `httpx.AsyncClient` is closed on `aclose`.

Spec: openspec/changes/backend-services/specs/milestone-detector/spec.md
"""
from __future__ import annotations

import logging
from typing import Callable

import httpx

from backend.data_source import DataSource
from backend.services.match_state import MatchStateManager

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Trigger matrix — single source of truth for "when does each momento fire?".
#
# Each entry is (momento, condition(state), guard(state)). The condition is
# the time-based check (e.g. elapsed >= 15) and the guard narrows the
# trigger to the correct game phase (e.g. only 1H). The list is iterated in
# order, so momenti are checked in ascending order. The first time both
# condition AND guard are True, the momento fires (and never again).
# ---------------------------------------------------------------------------


TRIGGER_MATRIX: list[tuple[int, Callable, Callable]] = [
    (1, lambda s: s.status.elapsed >= 15, lambda s: s.status.short == "1H"),
    (
        2,
        lambda s: s.status.elapsed >= 30,
        lambda s: s.status.short in ("1H", "HT", "2H"),
    ),
    (3, lambda s: s.status.short == "HT", lambda s: True),
    (
        4,
        lambda s: s.status.elapsed >= 60,
        # Guard widened: extra-time statuses (ET, BT, P, AET, PEN)
        # are also valid for the 60-minute snapshot. Without this,
        # a match that goes to ET would skip momento 4.
        lambda s: s.status.short in ("HT", "2H", "ET", "BT", "P", "AET", "PEN", "FT"),
    ),
    (
        5,
        lambda s: s.status.elapsed >= 75,
        # Guard widened: same set of extra-time statuses as momento 4
        # so the 75-minute snapshot still fires in extra time.
        lambda s: s.status.short in ("2H", "ET", "BT", "P", "AET", "PEN", "FT"),
    ),
    # Momento 6 trigger widened: AET (After Extra Time) and PEN
    # (Penalty Shootout end) also count as "match finished" so the
    # final webhook fires on those matches too.
    (6, lambda s: s.status.short in ("FT", "AET", "PEN"), lambda s: True),
]


class MilestoneDetector:
    """Trigger matrix runner. Fires each momento at most once.

    Constructor takes the data source, the match state manager (the
    payload source), the n8n base URL, and an optional injected
    `httpx.AsyncClient`. When `http_client` is `None` the detector
    creates and owns its own client (closed on `aclose`).
    """

    def __init__(
        self,
        data_source: DataSource,
        match_state: MatchStateManager,
        n8n_url: str,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._data_source = data_source
        self._match_state = match_state
        self._n8n_url = n8n_url.rstrip("/")
        self._http = http_client or httpx.AsyncClient(timeout=5.0)
        self._owns_http = http_client is None
        # 1..=6 → fired/pending. We never mutate the dict after init
        # except to flip values to True, so a plain dict is enough.
        self._fired: dict[int, bool] = {i: False for i in range(1, 7)}

    async def check_and_push(self) -> None:
        """Walk the trigger matrix once. Fire each un-fired momento
        whose condition AND guard are met.

        The state is captured ONCE at the top so the matrix operates
        on a consistent snapshot. Each fire updates the match state
        (via `get_details` → `update_details`) and POSTs the new
        context text to the webhook. A POST failure is logged but
        does NOT prevent subsequent fires — the schedule is the
        schedule.
        """
        if not self._n8n_url:
            log.info("milestone push skipped: N8N_WEBHOOK_BASE_URL is empty")
            return
        state = self._match_state.get_state()
        for momento, condition, guard in TRIGGER_MATRIX:
            if self._fired[momento]:
                continue
            if not condition(state) or not guard(state):
                continue
            events, home_stats, away_stats, home_players, away_players = (
                await self._data_source.get_details(momento)
            )
            self._match_state.update_details(
                events, home_stats, away_stats, home_players, away_players
            )
            context_text = self._match_state.get_context_text()
            payload = {
                "momento": momento,
                "context_text": context_text,
                "match_state": self._match_state.get_state().model_dump(mode="json"),
            }
            await self._push(momento, payload)
            self._fired[momento] = True

    async def _push(self, momento: int, payload: dict) -> None:
        """POST `payload` to the n8n webhook. Errors are logged, not raised.

        The trigger is marked fired by the caller (in
        `check_and_push`), so even a failure here does not retake
        the slot — the schedule is the schedule.
        """
        try:
            await self._http.post(f"{self._n8n_url}/webhook/momento", json=payload)
        except Exception as e:
            log.error("n8n push failed for momento %d: %s", momento, e)

    async def aclose(self) -> None:
        """Close the detector's owned `httpx.AsyncClient`, if any.

        When the caller injected a client, the detector leaves it
        alone — the caller's lifespan is responsible for the
        lifecycle. When the detector created the client, the
        detector closes it.
        """
        if self._owns_http:
            await self._http.aclose()
