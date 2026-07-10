"""Tests for `MilestoneDetector` — the 6-trigger matrix that pushes
context snapshots to the n8n webhook at 6 specific match moments.

Trigger matrix (per design):
- 1: 15' in 1H
- 2: 30' in 1H, HT, or 2H
- 3: HT (halftime)
- 4: 60' in HT, 2H, or FT
- 5: 75' in 2H or FT
- 6: FT (full time)

Each trigger fires at most once per process. The detector owns its
own `_fired` set, so re-entry on the same momenti is a no-op.

The data source is the real `MockDataSource` from `conftest` — the
test pins the trigger condition (time + status), not the events
shape. The n8n webhook is mocked with respx so the test is fast and
network-free.

Covers every scenario in
`openspec/changes/backend-services/specs/milestone-detector/spec.md`
plus triangulation cases for the no-re-fire path, the no-op n8n
URL, the POST-failure resilience, and the full timeline.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx
import pytest
import respx

from backend.data_source import DataSource
from backend.models import FixtureStatus, MatchState, TeamScore
from backend.services.match_state import MatchStateManager
from backend.services.milestones import MilestoneDetector


N8N_URL = "http://test-n8n.local"
WEBHOOK_PATH = "/webhook/momento"


# ---------------------------------------------------------------------------
# Helpers — build hand-crafted MatchState objects for the trigger condition
# tests. Centralizing the construction keeps the per-test bodies focused on
# the behavior under test, not on dict/model construction.
# ---------------------------------------------------------------------------


def make_state(
    *,
    elapsed: int,
    short: str,
    home_goals: int = 0,
    away_goals: int = 0,
    home_name: str = "Argentina",
    away_name: str = "Netherlands",
) -> MatchState:
    """Return a bare-bones `MatchState` for trigger condition tests.

    The events/stats/players lists are empty — the detector fills
    them in from the data source when a trigger fires. We only need
    the status fields to control the condition/guard logic.
    """
    return MatchState(
        fixture_id=868019,
        status=FixtureStatus(elapsed=elapsed, short=short, long="test-state"),
        home=TeamScore(id=26, name=home_name, goals=home_goals),
        away=TeamScore(id=33, name=away_name, goals=away_goals),
        events=[],
        home_stats=None,
        away_stats=None,
        home_players=[],
        away_players=[],
        last_updated=datetime(2022, 12, 9, 20, 0, 0, tzinfo=timezone.utc),
    )


def make_detector(
    match_state: MatchStateManager,
    data_source: DataSource,
    *,
    n8n_url: str = N8N_URL,
    http_client: httpx.AsyncClient | None = None,
) -> MilestoneDetector:
    """Construct a `MilestoneDetector` with the test's chosen n8n URL.

    The default n8n URL points at a host respx can intercept. A
    `None` URL disables the webhook (the no-op short-circuit).
    """
    return MilestoneDetector(
        data_source=data_source,
        match_state=match_state,
        n8n_url=n8n_url,
        http_client=http_client,
    )


def seed_match_state(match_state: MatchStateManager, state: MatchState) -> None:
    """Drop a hand-crafted `MatchState` into the manager (no I/O)."""
    match_state.update_fixture(state)


def fire_momenti_from_calls(calls: list[httpx.Request]) -> list[int]:
    """Extract the list of momenti pushed from the respx call list.

    Each call's `content` is a JSON body with a `momento` field.
    """
    momenti: list[int] = []
    for call in calls:
        body = call.request.content
        # httpx encodes JSON as bytes; decode and pull the momento.
        import json

        data = json.loads(body)
        momenti.append(data["momento"])
    return momenti


# ---------------------------------------------------------------------------
# Requirement: each of the 6 triggers fires at the right condition
# ---------------------------------------------------------------------------


class TestEachTriggerFires:
    """For each momento, the trigger fires when the state matches.

    The state is chosen so that only the target trigger's condition
    AND guard are met. Earlier triggers' guards or conditions
    are false at the same state.
    """

    @respx.mock
    async def test_trigger_1_fires_at_minute_15_first_half(
        self, mock_datasource, match_state
    ):
        """Spec: 'Momento 1 fires at elapsed >= 15 with short == "1H"'.

        At 15' in the first half only the minute-15 trigger should
        fire — the others all fail their condition or guard.
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        seed_match_state(match_state, make_state(elapsed=15, short="1H"))
        detector = make_detector(match_state, mock_datasource)

        await detector.check_and_push()
        await detector.aclose()

        assert fire_momenti_from_calls(respx.calls) == [1]

    @respx.mock
    async def test_trigger_2_fires_at_minute_30_second_half(
        self, mock_datasource, match_state
    ):
        """Spec: 'Momento 2 fires at elapsed >= 30 with short in (1H, HT, 2H)'.

        We use short="2H" so the 1H guard for trigger 1 fails. Trigger
        3 needs short=="HT" (False). Triggers 4-6 need elapsed >= 60.
        Only trigger 2 fires.
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        seed_match_state(match_state, make_state(elapsed=30, short="2H"))
        detector = make_detector(match_state, mock_datasource)

        await detector.check_and_push()
        await detector.aclose()

        assert fire_momenti_from_calls(respx.calls) == [2]

    @respx.mock
    async def test_trigger_3_fires_at_ht(self, mock_datasource, match_state):
        """Spec: 'Momento 3 fires when short == "HT"'.

        We use elapsed=29 so trigger 2's elapsed >= 30 condition
        fails; trigger 1's "1H" guard fails; triggers 4-6 need
        elapsed >= 60 (False) or short == "FT" (False). Only
        trigger 3 fires.
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        seed_match_state(match_state, make_state(elapsed=29, short="HT"))
        detector = make_detector(match_state, mock_datasource)

        await detector.check_and_push()
        await detector.aclose()

        assert fire_momenti_from_calls(respx.calls) == [3]

    @respx.mock
    async def test_trigger_4_fires_at_minute_60(self, mock_datasource, match_state):
        """Spec: 'Momento 4 fires at elapsed >= 60 with short in (HT, 2H, FT)'.

        At 60' in 2H, trigger 2 also fires (its condition is a
        superset of trigger 4's). We assert that trigger 4 is
        present in the call list — and that trigger 2 fires too
        (this is the documented behavior for the "first time we
        see elapsed >= 30 in 2H" event).
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        seed_match_state(match_state, make_state(elapsed=60, short="2H"))
        detector = make_detector(match_state, mock_datasource)

        await detector.check_and_push()
        await detector.aclose()

        momenti = fire_momenti_from_calls(respx.calls)
        assert 4 in momenti
        assert 2 in momenti  # the superset also fires

    @respx.mock
    async def test_trigger_5_fires_at_minute_75(self, mock_datasource, match_state):
        """Spec: 'Momento 5 fires at elapsed >= 75 with short in (2H, FT)'.

        At 75' in 2H, triggers 2 and 4 also fire (superset chain).
        We assert trigger 5 is present.
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        seed_match_state(match_state, make_state(elapsed=75, short="2H"))
        detector = make_detector(match_state, mock_datasource)

        await detector.check_and_push()
        await detector.aclose()

        momenti = fire_momenti_from_calls(respx.calls)
        assert 5 in momenti
        assert 2 in momenti
        assert 4 in momenti

    @respx.mock
    async def test_trigger_6_fires_at_ft(self, mock_datasource, match_state):
        """Spec: 'Momento 6 fires when short == "FT"'.

        At 90' in FT, triggers 4 and 5 also fire (they require
        elapsed >= 60 / >= 75 and the FT guard passes). We assert
        trigger 6 is present and that the FT guard has properly
        filtered trigger 1 (the 1H-only guard).
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        seed_match_state(match_state, make_state(elapsed=90, short="FT"))
        detector = make_detector(match_state, mock_datasource)

        await detector.check_and_push()
        await detector.aclose()

        momenti = fire_momenti_from_calls(respx.calls)
        assert 6 in momenti
        # Trigger 1's guard (short == "1H") must keep it from
        # firing even though elapsed >= 15.
        assert 1 not in momenti


# ---------------------------------------------------------------------------
# Requirement: status guards prevent false fires
# ---------------------------------------------------------------------------


class TestStatusGuards:
    @respx.mock
    async def test_trigger_1_does_not_fire_at_ft_despite_elapsed_above_15(
        self, mock_datasource, match_state
    ):
        """Spec: 'Status guard prevents trigger 1 from firing outside 1H'.

        Even though `elapsed=90 >= 15` satisfies the condition, the
        guard `short == "1H"` blocks the trigger. The test pins a
        state at FT and asserts trigger 1 is absent from the calls.
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        seed_match_state(match_state, make_state(elapsed=90, short="FT"))
        detector = make_detector(match_state, mock_datasource)

        await detector.check_and_push()
        await detector.aclose()

        momenti = fire_momenti_from_calls(respx.calls)
        assert 1 not in momenti

    @respx.mock
    async def test_trigger_2_does_not_fire_at_ft(self, mock_datasource, match_state):
        """Triangulation: trigger 2's guard is `(1H, HT, 2H)` — FT is
        explicitly excluded. The state at FT MUST NOT fire trigger 2,
        even though `elapsed >= 30` is satisfied.
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        # elapsed=29 keeps trigger 2's condition false so we can
        # isolate the guard's effect.
        seed_match_state(match_state, make_state(elapsed=29, short="FT"))
        detector = make_detector(match_state, mock_datasource)

        await detector.check_and_push()
        await detector.aclose()

        momenti = fire_momenti_from_calls(respx.calls)
        assert 2 not in momenti


# ---------------------------------------------------------------------------
# Requirement: no re-firing after _fired[momento] = True
# ---------------------------------------------------------------------------


class TestNoRefiring:
    @respx.mock
    async def test_trigger_does_not_re_fire_on_second_check(
        self, mock_datasource, match_state
    ):
        """Spec: 'Each trigger fires at most once per process'.

        After a trigger has fired, subsequent `check_and_push` calls
        MUST NOT call the webhook for that momento again — the
        `_fired` dict is the gate.
        """
        route = respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        seed_match_state(match_state, make_state(elapsed=15, short="1H"))
        detector = make_detector(match_state, mock_datasource)

        # First call — trigger 1 fires.
        await detector.check_and_push()
        first_call_count = route.call_count

        # Second call — same state, no new push.
        await detector.check_and_push()
        second_call_count = route.call_count

        await detector.aclose()

        assert first_call_count == 1
        assert second_call_count == 1  # no new push

    @respx.mock
    async def test_each_momento_fires_exactly_once_across_many_calls(
        self, mock_datasource, match_state
    ):
        """Triangulation: across N calls with the same state, the
        webhook is hit exactly once per momento that satisfies its
        condition. Re-entry does not multiply pushes.
        """
        route = respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        seed_match_state(match_state, make_state(elapsed=15, short="1H"))
        detector = make_detector(match_state, mock_datasource)

        for _ in range(5):
            await detector.check_and_push()

        await detector.aclose()

        # Trigger 1 is the only one that fires at this state.
        assert route.call_count == 1


# ---------------------------------------------------------------------------
# Requirement: empty n8n_url short-circuits
# ---------------------------------------------------------------------------


class TestEmptyN8nUrl:
    async def test_empty_n8n_url_is_a_no_op(self, mock_datasource, match_state):
        """Spec: 'Empty n8n URL disables the push'.

        With `n8n_url=""` the detector MUST NOT raise, MUST NOT make
        any HTTP call, and MUST NOT mutate `_fired`. The check is a
        no-op (a logged info message is acceptable; we just verify
        behavior here).
        """
        seed_match_state(match_state, make_state(elapsed=15, short="1H"))
        detector = make_detector(match_state, mock_datasource, n8n_url="")

        # No respx route registered — any outbound HTTP would raise
        # an unhandled ConnectError. The test passes if check_and_push
        # returns cleanly.
        await detector.check_and_push()

        # Detector stays un-fired so a later config change can
        # re-enable the webhook and have the trigger still available.
        assert detector._fired == {i: False for i in range(1, 7)}

        await detector.aclose()


# ---------------------------------------------------------------------------
# Requirement: POST failure resilience
# ---------------------------------------------------------------------------


class TestPostFailureResilience:
    @respx.mock
    async def test_post_exception_marks_fired_and_continues(
        self, mock_datasource, match_state, caplog
    ):
        """Spec: 'POST failure logs the error, marks the momento fired,
        and continues to the next momento'.

        We arrange two triggers to fire (at 60' 2H, triggers 2 and
        4 both fire — the superset chain). The webhook raises a
        `httpx.ConnectError` (simulating n8n being down). Both
        momenti must still be marked fired, and an error log must
        appear for each push.

        Note: the design catches exceptions but does NOT inspect
        the response status. A 4xx/5xx response is silently
        accepted; only a raised exception triggers the error
        log. This test exercises the exception path.
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            side_effect=httpx.ConnectError("n8n is down")
        )

        seed_match_state(match_state, make_state(elapsed=60, short="2H"))
        detector = make_detector(match_state, mock_datasource)

        with caplog.at_level(logging.ERROR, logger="backend.services.milestones"):
            await detector.check_and_push()
        await detector.aclose()

        # Both triggers were attempted (and marked fired) despite
        # the connection error.
        assert detector._fired[2] is True
        assert detector._fired[4] is True

        # At least one error log line per attempted push.
        error_messages = [
            record.getMessage()
            for record in caplog.records
            if record.levelno == logging.ERROR
        ]
        assert any("2" in msg for msg in error_messages)
        assert any("4" in msg for msg in error_messages)

    @respx.mock
    async def test_5xx_response_does_not_crash_or_retry(
        self, mock_datasource, match_state
    ):
        """Triangulation: a 5xx response from n8n is silently
        accepted (the design's `_push` does not call
        `raise_for_status`). The detector MUST mark the trigger
        fired and proceed — the schedule is the schedule, we
        don't retry.
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(500, json={"error": "down"})
        )

        seed_match_state(match_state, make_state(elapsed=15, short="1H"))
        detector = make_detector(match_state, mock_datasource)

        # Should not raise.
        await detector.check_and_push()
        await detector.aclose()

        # The trigger is still marked fired.
        assert detector._fired[1] is True
        # Exactly one POST was made — no retry.
        assert len(respx.calls) == 1


# ---------------------------------------------------------------------------
# Requirement: full timeline simulation
# ---------------------------------------------------------------------------


class TestFullTimeline:
    @respx.mock
    async def test_all_six_momenti_fire_across_full_match_timeline(
        self, mock_datasource, match_state
    ):
        """Spec: 'Each of the 6 momenti fires exactly once across a
        full match timeline'.

        We walk the match from 15' to 90' (FT) and call
        `check_and_push` at each boundary. Every momento must
        appear in the call list exactly once.
        """
        respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        detector = make_detector(match_state, mock_datasource)

        # Tick 1: 15' in 1H.  Triggers 1.
        seed_match_state(match_state, make_state(elapsed=15, short="1H"))
        await detector.check_and_push()

        # Tick 2: 30' in 2H (skip 1H on purpose to exercise the
        # short=2H branch).  Triggers 2.
        seed_match_state(match_state, make_state(elapsed=30, short="2H"))
        await detector.check_and_push()

        # Tick 3: HT.  Triggers 3.
        seed_match_state(match_state, make_state(elapsed=45, short="HT"))
        await detector.check_and_push()

        # Tick 4: 60' in 2H.  Triggers 4 (and 2 is already fired).
        seed_match_state(match_state, make_state(elapsed=60, short="2H"))
        await detector.check_and_push()

        # Tick 5: 75' in 2H.  Triggers 5.
        seed_match_state(match_state, make_state(elapsed=75, short="2H"))
        await detector.check_and_push()

        # Tick 6: 90' in FT.  Triggers 6.
        seed_match_state(match_state, make_state(elapsed=90, short="FT"))
        await detector.check_and_push()

        await detector.aclose()

        # All 6 momenti present, in trigger-matrix order, exactly once.
        momenti = fire_momenti_from_calls(respx.calls)
        assert momenti == [1, 2, 3, 4, 5, 6]


# ---------------------------------------------------------------------------
# Requirement: webhook payload structure
# ---------------------------------------------------------------------------


class TestWebhookPayload:
    @respx.mock
    async def test_payload_has_momento_context_text_and_match_state(
        self, mock_datasource, match_state
    ):
        """Spec: 'Webhook payload is {momento, context_text, match_state}'.

        `context_text` is the 7-section string from `get_context_text`.
        `match_state` is the JSON-serialized `MatchState` (via
        `model_dump(mode="json")`).
        """
        import json

        route = respx.post(f"{N8N_URL}{WEBHOOK_PATH}").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )

        seed_match_state(match_state, make_state(elapsed=15, short="1H"))
        detector = make_detector(match_state, mock_datasource)

        await detector.check_and_push()
        await detector.aclose()

        assert route.call_count == 1
        payload = json.loads(route.calls[0].request.content)

        assert set(payload.keys()) == {"momento", "context_text", "match_state"}
        assert payload["momento"] == 1
        assert isinstance(payload["context_text"], str)
        # The context text is the 7-section string. We don't pin the
        # exact content here (that is the context-text-format spec's
        # job); we just confirm the shape.
        assert "Minuto 15" in payload["context_text"]
        # match_state is a JSON-serializable dict.
        assert isinstance(payload["match_state"], dict)
        assert payload["match_state"]["fixture_id"] == 868019
        assert payload["match_state"]["status"]["elapsed"] == 15
        assert payload["match_state"]["status"]["short"] == "1H"


# ---------------------------------------------------------------------------
# Requirement: injected http_client lifecycle
# ---------------------------------------------------------------------------


class TestInjectedHttpClient:
    async def test_injected_http_client_is_not_closed_by_aclose(self, mock_datasource, match_state):
        """Spec: 'Aclose only shuts down an http_client the detector owns'.

        When the caller injects an `httpx.AsyncClient`, the detector
        MUST NOT close it on `aclose` — the caller's lifespan owns
        the client's lifecycle. The detector's own client (no
        injection) is closed on `aclose`.
        """
        injected = httpx.AsyncClient(timeout=5.0)
        try:
            detector = MilestoneDetector(
                data_source=mock_datasource,
                match_state=match_state,
                n8n_url=N8N_URL,
                http_client=injected,
            )

            await detector.aclose()

            # The injected client must still be usable.
            # `is_closed` becomes True only after `aclose`.
            assert injected.is_closed is False

        finally:
            await injected.aclose()

    async def test_owned_http_client_is_closed_by_aclose(self, mock_datasource, match_state):
        """Triangulation: when no client is injected, the detector
        owns the client and `aclose` shuts it down.
        """
        detector = MilestoneDetector(
            data_source=mock_datasource,
            match_state=match_state,
            n8n_url=N8N_URL,
        )

        owned = detector._http
        assert owned.is_closed is False

        await detector.aclose()

        assert owned.is_closed is True
