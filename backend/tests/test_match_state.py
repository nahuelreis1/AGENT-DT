"""Tests for MatchStateManager — in-memory holder of MatchState and the
Prediction log, plus the 7-section context text per the
`context-text-format` spec.

Covers every scenario in
`openspec/changes/backend-services/specs/match-state-manager/spec.md`
plus triangulation cases that exercise the real code paths
(score reconciliation idempotency, pluralization, snapshot at min 67,
pre-kickoff empty variants).

These tests reference `backend.services.match_state`. A missing or broken
match_state module will fail at the import line — this keeps the
RED→GREEN cycle honest.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.models import (
    FixtureStatus,
    LineupPlayer,
    LineupTeam,
    MatchEvent,
    MatchState,
    PlayerStats,
    TeamScore,
    TeamStats,
)


# ---------------------------------------------------------------------------
# Helpers — build hand-crafted MatchState objects for individual tests.
# Centralizing the construction keeps the per-test bodies focused on
# the behavior under test, not on dict/model construction.
# ---------------------------------------------------------------------------


def make_status(elapsed: int = 0, short: str = "1H", long: str = "First Half") -> FixtureStatus:
    return FixtureStatus(elapsed=elapsed, short=short, long=long)


def make_team_score(name: str, goals: int = 0) -> TeamScore:
    return TeamScore(id=1, name=name, goals=goals)


def make_match_state(
    *,
    elapsed: int = 0,
    short: str = "1H",
    home_name: str = "Argentina",
    away_name: str = "Holanda",
    home_goals: int = 0,
    away_goals: int = 0,
    events: list[MatchEvent] | None = None,
    home_stats: TeamStats | None = None,
    away_stats: TeamStats | None = None,
    home_players: list[PlayerStats] | None = None,
    away_players: list[PlayerStats] | None = None,
) -> MatchState:
    return MatchState(
        fixture_id=868019,
        status=make_status(elapsed=elapsed, short=short),
        home=make_team_score(home_name, home_goals),
        away=make_team_score(away_name, away_goals),
        events=list(events) if events else [],
        home_stats=home_stats,
        away_stats=away_stats,
        home_players=list(home_players) if home_players else [],
        away_players=list(away_players) if away_players else [],
        last_updated=datetime(2022, 12, 9, 20, 0, 0, tzinfo=timezone.utc),
    )


def make_player(
    name: str,
    rating: str = "7.0",
    *,
    goals: int = 0,
    assists: int = 0,
    key_passes: int = 0,
    dribbles_success: int = 0,
    dribbles_attempts: int = 0,
) -> PlayerStats:
    return PlayerStats(
        name=name,
        position="M",
        rating=rating,
        minutes=67,
        goals=goals,
        assists=assists,
        shots_total=1,
        shots_on=1,
        passes_total=30,
        key_passes=key_passes,
        pass_accuracy="85%",
        duels_won=3,
        duels_total=5,
        dribbles_success=dribbles_success,
        dribbles_attempts=dribbles_attempts,
        fouls_committed=1,
        fouls_drawn=2,
        yellow_cards=0,
        red_cards=0,
    )


def make_lineup_player(
    name: str = "L. Messi",
    pos: str = "FW",
    number: int = 10,
    grid: str | None = "4:3",
) -> LineupPlayer:
    return LineupPlayer(
        player_id=1,
        name=name,
        number=number,
        pos=pos,
        grid=grid,
    )


def make_lineup_team(
    team_name: str = "Argentina",
    formation: str = "4-3-3",
    starters: list[LineupPlayer] | None = None,
    coach_name: str | None = "L. Scaloni",
) -> LineupTeam:
    if starters is None:
        starters = [make_lineup_player() for _ in range(11)]
    return LineupTeam(
        team_id=26,
        team_name=team_name,
        formation=formation,
        startXI=starters,
        substitutes=[],
        coach_name=coach_name,
    )


# ---------------------------------------------------------------------------
# Construction & initialization
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_get_state_before_update_fixture_raises_runtime_error(self):
        """Spec: 'Uninitialized state raises on get_state'.

        A freshly-constructed MatchStateManager() has no fixture, so
        `get_state()` MUST raise RuntimeError rather than returning
        `None` (which would force every caller to null-check).
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()

        with pytest.raises(RuntimeError):
            ms.get_state()

    def test_update_fixture_makes_state_readable(self):
        """Spec: 'Fixture update makes state readable'.

        After `update_fixture(state)`, `get_state()` MUST return the
        same object — same fixture_id, same status, same teams.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        state = make_match_state(elapsed=15, short="1H", home_goals=0, away_goals=0)

        ms.update_fixture(state)

        assert ms.get_state().fixture_id == 868019
        assert ms.get_state().status.short == "1H"
        assert ms.get_state().home.name == "Argentina"
        assert ms.get_state().away.name == "Holanda"

    def test_update_fixture_overwrites_prior_state(self):
        """Triangulation: a second `update_fixture` call replaces the
        prior state — update_fixture is a snapshot, not a merge.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        first = make_match_state(elapsed=15, short="1H", home_goals=0, away_goals=0)
        second = make_match_state(elapsed=67, short="2H", home_goals=2, away_goals=1)

        ms.update_fixture(first)
        ms.update_fixture(second)

        assert ms.get_state().status.elapsed == 67
        assert ms.get_state().status.short == "2H"
        assert ms.get_state().home.goals == 2


# ---------------------------------------------------------------------------
# Score reconciliation via update_details
# ---------------------------------------------------------------------------


class TestUpdateDetails:
    def test_update_details_before_update_fixture_raises_runtime_error(self):
        """Spec: detail update requires fixture to be initialized first.

        Calling `update_details` before `update_fixture` is a
        programmer error — the manager has no home/away team to
        attribute goals to, so we raise loudly.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()

        with pytest.raises(RuntimeError):
            ms.update_details([], None, None, [], [])

    def test_update_details_with_one_home_goal_event_recomputes_to_1_0(self):
        """Spec triangulation: a single home Goal event recomputes
        home.goals=1, away.goals=0, OVERRIDING the prior fixture score.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(home_goals=0, away_goals=0))
        events = [
            MatchEvent(minute=35, team="Argentina", player="Molina", type="Goal", detail="Normal Goal"),
        ]

        ms.update_details(events, None, None, [], [])

        assert ms.get_state().home.goals == 1
        assert ms.get_state().away.goals == 0

    def test_update_details_with_empty_events_yields_0_0_even_if_fixture_set_2_2(self):
        """Spec: 'Min 15 with empty events yields 0-0'.

        The API's `goals` field is incremental and stale by design;
        `update_details` with no Goal events MUST recompute 0-0 even
        when `update_fixture` previously set 2-2. The events list is
        the ground truth.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(home_goals=2, away_goals=2))

        ms.update_details([], None, None, [], [])

        assert ms.get_state().home.goals == 0
        assert ms.get_state().away.goals == 0

    def test_update_details_with_four_goal_events_split_2_2_overrides_api_score(self):
        """Spec: '4 Goal events split 2-2 override API score'.

        Two Argentina goals (Molina 35', Messi pen 73') and two
        Holanda goals (Weghorst 83', Weghorst 101') MUST recompute to
        2-2 even when `update_fixture` had set 1-1.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(home_goals=1, away_goals=1))
        events = [
            MatchEvent(minute=35, team="Argentina", player="Molina", type="Goal", detail="Normal Goal"),
            MatchEvent(minute=73, team="Argentina", player="Messi", type="Goal", detail="Penalty"),
            MatchEvent(minute=83, team="Holanda", player="Weghorst", type="Goal", detail="Normal Goal"),
            MatchEvent(minute=101, team="Holanda", player="Weghorst", type="Goal", detail="Normal Goal"),
        ]

        ms.update_details(events, None, None, [], [])

        assert ms.get_state().home.goals == 2
        assert ms.get_state().away.goals == 2

    def test_update_details_reconciliation_is_idempotent(self):
        """Spec: 'Reconciliation is idempotent'.

        Calling `update_details` twice with the same events MUST
        leave the score unchanged. The recompute must be deterministic
        given the same input.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(home_goals=0, away_goals=0))
        events = [
            MatchEvent(minute=35, team="Argentina", player="Molina", type="Goal", detail="Normal Goal"),
            MatchEvent(minute=43, team="Argentina", player="Messi", type="Goal", detail="Penalty"),
            MatchEvent(minute=73, team="Holanda", player="Weghorst", type="Goal", detail="Normal Goal"),
        ]

        ms.update_details(events, None, None, [], [])
        first_home, first_away = ms.get_state().home.goals, ms.get_state().away.goals
        ms.update_details(events, None, None, [], [])
        second_home, second_away = ms.get_state().home.goals, ms.get_state().away.goals

        assert first_home == second_home == 2
        assert first_away == second_away == 1

    def test_update_details_replaces_stored_events_and_players(self):
        """Spec: 'update_details replaces events, stats, players'.

        The new events list MUST replace the one passed to
        `update_fixture` (or any previous `update_details` call).
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state())
        new_event = MatchEvent(minute=10, team="Argentina", player="Di Maria", type="Goal", detail="Normal Goal")
        new_player = make_player("Di Maria", rating="7.0")

        ms.update_details([new_event], None, None, [new_player], [])

        state = ms.get_state()
        assert state.events == [new_event]
        assert state.home_players == [new_player]

    def test_missed_penalty_does_not_increment_score(self):
        """Spec fix: a 'Missed Penalty' Goal event must NOT be counted
        in the score. The API emits a separate event with detail
        containing 'Missed' when a penalty is missed — the score
        reconciliation must skip it.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(home_goals=0, away_goals=0))
        events = [
            MatchEvent(
                minute=80,
                team="Argentina",
                player="L. Messi",
                type="Goal",
                detail="Missed Penalty",
            ),
        ]

        ms.update_details(events, None, None, [], [])

        assert ms.get_state().home.goals == 0
        assert ms.get_state().away.goals == 0

    def test_own_goal_counts_for_opponent(self):
        """Spec fix: an Own Goal by Argentina counts as a goal for
        Netherlands (the opponent). Score reconciliation must flip
        the team attribution.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(home_goals=0, away_goals=0))
        events = [
            MatchEvent(
                minute=50,
                team="Argentina",  # Argentine player scored own goal
                player="R. De Paul",
                type="Goal",
                detail="Own Goal",
            ),
        ]

        ms.update_details(events, None, None, [], [])

        # Netherlands (away) gets +1 because of the own goal
        assert ms.get_state().home.goals == 0
        assert ms.get_state().away.goals == 1


# ---------------------------------------------------------------------------
# Lineup update
# ---------------------------------------------------------------------------


class TestUpdateLineups:
    def test_update_lineups_stores_and_is_readable(self):
        """Spec: 'Lineups stored and readable'."""
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state())
        home = make_lineup_team("Argentina", "4-3-3")
        away = make_lineup_team("Netherlands", "3-4-1-2")

        ms.update_lineups(home, away)

        assert ms.get_state().home_lineup is home
        assert ms.get_state().away_lineup is away
        assert ms.get_state().home_lineup.formation == "4-3-3"
        assert ms.get_state().away_lineup.formation == "3-4-1-2"

    def test_update_lineups_none_none_accepted_without_raising(self):
        """Spec: 'None lineups accepted without raising'."""
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state())

        ms.update_lineups(None, None)

        assert ms.get_state().home_lineup is None
        assert ms.get_state().away_lineup is None

    def test_update_lineups_before_fixture_raises_runtime_error(self):
        """Spec: 'Lineup update before fixture raises RuntimeError'."""
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()

        with pytest.raises(RuntimeError):
            ms.update_lineups(None, None)


# ---------------------------------------------------------------------------
# Context text — formaciones section (NEW)
# ---------------------------------------------------------------------------


class TestContextTextFormaciones:
    def test_both_lineups_loaded_renders_single_line(self):
        """Spec: 'Both lineups loaded' — FORMACIONES: {home} {f1} - {away} {f2}."""
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(home_name="Argentina", away_name="Holanda"))
        ms.update_lineups(
            make_lineup_team("Argentina", "4-3-3"),
            make_lineup_team("Holanda", "3-4-1-2"),
        )

        text = ms.get_context_text()

        assert "FORMACIONES: Argentina 4-3-3 - Holanda 3-4-1-2" in text

    def test_lineups_not_loaded_collapses_to_fallback(self):
        """Spec: 'Lineups not loaded collapses to fallback'."""
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state())

        text = ms.get_context_text()

        assert "FORMACIONES: No disponibles aún" in text

    def test_one_lineup_missing_collapses_to_fallback(self):
        """Spec: 'One lineup missing collapses to fallback'."""
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(home_name="Argentina", away_name="Holanda"))
        ms.update_lineups(make_lineup_team("Argentina", "4-3-3"), None)

        text = ms.get_context_text()

        assert "FORMACIONES: No disponibles aún" in text


# ---------------------------------------------------------------------------
# Context text — all players section (NEW)
# ---------------------------------------------------------------------------


class TestContextTextAllPlayers:
    def test_all_22_starters_listed_grouped_by_team(self):
        """Spec: 'All 22 starters listed grouped by team'."""
        from backend.services.match_state import MatchStateManager

        home_starters = [
            make_lineup_player(f"H{i}", pos="DF") for i in range(11)
        ]
        away_starters = [
            make_lineup_player(f"A{i}", pos="MF") for i in range(11)
        ]
        ms = MatchStateManager()
        ms.update_fixture(make_match_state())
        ms.update_lineups(
            make_lineup_team("Argentina", "4-3-3", starters=home_starters),
            make_lineup_team("Netherlands", "3-4-1-2", starters=away_starters),
        )

        text = ms.get_context_text()

        assert "TODOS LOS JUGADORES:" in text
        assert "Argentina (4-3-3):" in text
        assert "Netherlands (3-4-1-2):" in text
        # Home starters appear before away starters
        home_idx = text.find("Argentina (4-3-3):")
        away_idx = text.find("Netherlands (3-4-1-2):")
        assert 0 < home_idx < away_idx

    def test_no_lineups_loaded_collapses_to_fallback(self):
        """Spec: 'No lineups loaded collapses to fallback'."""
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state())

        text = ms.get_context_text()

        assert "TODOS LOS JUGADORES: Sin datos suficientes" in text

    def test_one_team_only_shows_that_team(self):
        """Spec: when only one lineup is present, show that team's players."""
        from backend.services.match_state import MatchStateManager

        home_starters = [make_lineup_player(f"H{i}", pos="DF") for i in range(11)]
        ms = MatchStateManager()
        ms.update_fixture(make_match_state())
        ms.update_lineups(
            make_lineup_team("Argentina", "4-3-3", starters=home_starters),
            None,
        )

        text = ms.get_context_text()

        assert "Argentina (4-3-3):" in text
        assert "Netherlands" not in text.split("TODOS LOS JUGADORES:")[1].split("\n\n")[0]

    def test_position_abbreviation_mapping(self):
        """Spec: pos[0] → G=ARQ, D=DEF, M=MED, F=ATK."""
        from backend.services.match_state import MatchStateManager

        starters = [
            make_lineup_player("GK1", pos="GK"),
            make_lineup_player("DF1", pos="DF"),
            make_lineup_player("MF1", pos="MF"),
            make_lineup_player("FW1", pos="FW"),
        ]
        ms = MatchStateManager()
        ms.update_fixture(make_match_state())
        ms.update_lineups(make_lineup_team(starters=starters), None)

        text = ms.get_context_text()

        all_players_section = text.split("TODOS LOS JUGADORES:")[1].split("\n\n")[0]
        assert "ARQ" in all_players_section
        assert "DEF" in all_players_section
        assert "MED" in all_players_section
        assert "ATK" in all_players_section


# ---------------------------------------------------------------------------
# Context text — header
# ---------------------------------------------------------------------------


class TestContextTextHeader:
    def test_header_at_minute_67_2H(self):
        """Spec: 'Snapshot at minute 67 with all data' (header sub-assertion).

        Argentina 2-1 Holanda, elapsed=67, short=2H MUST render as:
        `⚽ Argentina 2 - 1 Holanda | Minuto 67 | 2do Tiempo`.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=67, short="2H", home_goals=2, away_goals=1))

        text = ms.get_context_text()

        assert text.startswith("⚽ Argentina 2 - 1 Holanda | Minuto 67 | 2do Tiempo\n\n")

    def test_header_at_minute_101_FT(self):
        """Spec: 'Extra time minute 101 renders as Final period'.

        The polling tick at minute 101 with status FT MUST render
        as `Final` (not `2do Tiempo`) because the period_name comes
        from `status.short`, not from the minute.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=101, short="FT", home_goals=2, away_goals=2))

        text = ms.get_context_text()

        assert text.startswith("⚽ Argentina 2 - 2 Holanda | Minuto 101 | Final\n\n")

    def test_header_uses_period_name_for_HT(self):
        """Triangulation: HT maps to 'Entretiempo'.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=45, short="HT", home_goals=2, away_goals=0))

        text = ms.get_context_text()

        assert text.startswith("⚽ Argentina 2 - 0 Holanda | Minuto 45 | Entretiempo\n\n")

    def test_header_uses_period_name_for_1H(self):
        """Triangulation: 1H maps to '1er Tiempo'.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=15, short="1H", home_goals=0, away_goals=0))

        text = ms.get_context_text()

        assert text.startswith("⚽ Argentina 0 - 0 Holanda | Minuto 15 | 1er Tiempo\n\n")

    def test_header_status_AET_renders_Final_tiempo_extra(self):
        """Spec: 'AET' status renders as 'Final (tiempo extra)'.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(
            make_match_state(elapsed=120, short="AET", home_goals=2, away_goals=2)
        )

        text = ms.get_context_text()

        assert text.startswith("⚽ Argentina 2 - 2 Holanda | Minuto 120 | Final (tiempo extra)\n\n")

    def test_header_status_PEN_renders_Final_penales(self):
        """Spec: 'PEN' status renders as 'Final (penales)'.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(
            make_match_state(elapsed=120, short="PEN", home_goals=2, away_goals=2)
        )

        text = ms.get_context_text()

        assert text.startswith("⚽ Argentina 2 - 2 Holanda | Minuto 120 | Final (penales)\n\n")

    def test_header_status_NS_renders_No_iniciado(self):
        """Spec: 'NS' status (Not Started) renders as 'No iniciado'.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=0, short="NS", home_goals=0, away_goals=0))

        text = ms.get_context_text()

        assert "No iniciado" in text

    def test_header_unknown_status_falls_back_to_raw_short(self):
        """Spec: any unknown status falls back to the raw `short`
        value (existing behavior — no exception, no missing key).
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(
            make_match_state(elapsed=15, short="XYZ", home_goals=0, away_goals=0)
        )

        text = ms.get_context_text()

        # Raw short value used as fallback
        assert " | XYZ" in text


# ---------------------------------------------------------------------------
# Context text — goals section
# ---------------------------------------------------------------------------


class TestContextTextGoals:
    def test_goals_with_no_events_renders_sin_goles(self):
        """Spec: 'Match with no goals'.

        When no Goal events exist, the section is exactly:
        `GOLES: Sin goles aún`.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=15, short="1H"))

        text = ms.get_context_text()

        assert "GOLES: Sin goles aún" in text

    def test_goals_with_two_home_goals_and_one_away_goal(self):
        """Spec triangulation: each goal as `{player} ({minute}')`,
        penalty as `{player} (pen {minute}')`, joined with `, `.
        Argentina: Molina (35'), Messi (pen 43'); Holanda: Weghorst (83').
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=85, short="2H", home_goals=2, away_goals=1))
        events = [
            MatchEvent(minute=35, team="Argentina", player="Molina", type="Goal", detail="Normal Goal"),
            MatchEvent(minute=43, team="Argentina", player="Messi", type="Goal", detail="Penalty"),
            MatchEvent(minute=83, team="Holanda", player="Weghorst", type="Goal", detail="Normal Goal"),
        ]
        ms.update_details(events, None, None, [], [])

        text = ms.get_context_text()

        assert "GOLES: Molina (35'), Messi (pen 43') - Weghorst (83')" in text

    def test_goals_with_only_away_goals_leaves_home_side_empty(self):
        """Triangulation: when one team has no goals, its side is an
        empty string between `GOLES: ` and the dash.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=85, short="2H", home_goals=0, away_goals=1))
        events = [
            MatchEvent(minute=83, team="Holanda", player="Weghorst", type="Goal", detail="Normal Goal"),
        ]
        ms.update_details(events, None, None, [], [])

        text = ms.get_context_text()

        assert "GOLES:  - Weghorst (83')" in text

    def test_goals_with_only_home_goals_leaves_away_side_empty(self):
        """Triangulation: symmetric case for away.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=43, short="2H", home_goals=2, away_goals=0))
        events = [
            MatchEvent(minute=35, team="Argentina", player="Molina", type="Goal", detail="Normal Goal"),
            MatchEvent(minute=43, team="Argentina", player="Messi", type="Goal", detail="Penalty"),
        ]
        ms.update_details(events, None, None, [], [])

        text = ms.get_context_text()

        assert "GOLES: Molina (35'), Messi (pen 43') - " in text

    def test_goals_section_own_goal_appears_under_benefited_team(self):
        """Spec fix: when Argentina scores an own goal, the goal
        text appears under the OPPONENT's (Netherlands/Holanda)
        goals section with the `(og X')` prefix.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=55, short="2H", home_goals=0, away_goals=1))
        events = [
            MatchEvent(
                minute=50,
                team="Argentina",
                player="R. De Paul",
                type="Goal",
                detail="Own Goal",
            ),
        ]
        ms.update_details(events, None, None, [], [])

        text = ms.get_context_text()

        # Argentina's own goal must appear under Holanda's goals,
        # formatted with the (og) prefix — NOT under Argentina.
        assert "GOLES:  - R. De Paul (og 50')" in text

    def test_goals_section_missed_penalty_excluded(self):
        """Spec fix: a 'Missed Penalty' event must NOT appear in
        the GOLES section at all — missed penalties are not goals.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=85, short="2H", home_goals=1, away_goals=0))
        events = [
            MatchEvent(minute=35, team="Argentina", player="Molina", type="Goal", detail="Normal Goal"),
            MatchEvent(
                minute=80,
                team="Argentina",
                player="L. Messi",
                type="Goal",
                detail="Missed Penalty",
            ),
        ]
        ms.update_details(events, None, None, [], [])

        text = ms.get_context_text()

        # Only the made goal appears, missed penalty is excluded
        assert "GOLES: Molina (35') - " in text
        assert "Messi" not in text  # missed penalty player must not appear
        assert "Missed Penalty" not in text

    def test_scored_penalty_formatted_missed_penalty_not(self):
        """Spec fix: only SCORED penalties get the `(pen X')` prefix.
        A 'Missed Penalty' event must NEVER be rendered as `(pen X')`.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=90, short="2H", home_goals=1, away_goals=0))
        events = [
            MatchEvent(minute=43, team="Argentina", player="Messi", type="Goal", detail="Penalty"),
            MatchEvent(
                minute=80,
                team="Argentina",
                player="L. Messi",
                type="Goal",
                detail="Missed Penalty",
            ),
        ]
        ms.update_details(events, None, None, [], [])

        text = ms.get_context_text()

        # Scored penalty uses (pen) — must appear
        assert "Messi (pen 43')" in text
        # Missed penalty MUST NOT use (pen) — that would falsely
        # credit the goal. And it must not appear at all.
        assert "Messi (pen 80')" not in text
        assert "Missed Penalty" not in text


# ---------------------------------------------------------------------------
# Context text — stats section
# ---------------------------------------------------------------------------


class TestContextTextStats:
    def test_stats_with_none_collapses_to_single_line(self):
        """Spec: 'Stats not yet loaded collapses to single line'.

        When `home_stats is None` OR `away_stats is None`, the section
        is exactly `ESTADÍSTICAS: No disponibles aún` and no per-line
        POSESIÓN/TIROS/xG lines are emitted.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=15, short="1H"))

        text = ms.get_context_text()

        assert "ESTADÍSTICAS: No disponibles aún" in text
        # No per-line output when stats are missing.
        assert "POSESIÓN" not in text
        assert "TIROS AL ARCO" not in text
        assert "xG:" not in text

    def test_stats_with_data_emits_ten_lines_in_spec_order(self):
        """Spec: all 10 stat lines in the documented order:
        POSESIÓN, TIROS AL ARCO, xG, TIROS TOTALES, CÓRNERES, FOULTAS,
        OFFSIDE, PASES ACERTADOS, TARJETAS AMARILLAS, TARJETAS ROJAS.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        home_stats = TeamStats(
            name="Argentina",
            possession="55%",
            shots_on_goal=3,
            total_shots=7,
            corners=3,
            fouls=9,
            offsides=1,
            yellow_cards=1,
            red_cards=0,
            pass_accuracy="87%",
            expected_goals="1.90",
        )
        away_stats = TeamStats(
            name="Holanda",
            possession="45%",
            shots_on_goal=2,
            total_shots=5,
            corners=2,
            fouls=10,
            offsides=2,
            yellow_cards=0,
            red_cards=0,
            pass_accuracy="85%",
            expected_goals="1.20",
        )
        ms.update_fixture(
            make_match_state(
                elapsed=67,
                short="2H",
                home_goals=2,
                away_goals=1,
                home_stats=home_stats,
                away_stats=away_stats,
            )
        )

        text = ms.get_context_text()

        # Extract the stats section (between FORMACIONES fallback and standout)
        # All 10 lines must appear in order.
        assert "POSESIÓN: ARG 55% - HOL 45%" in text
        assert "TIROS AL ARCO: ARG 3 - HOL 2" in text
        assert "xG: ARG 1.90 - HOL 1.20" in text
        assert "TIROS TOTALES: ARG 7 - HOL 5" in text
        assert "CÓRNERES: ARG 3 - HOL 2" in text
        assert "FOULTAS: ARG 9 - HOL 10" in text
        assert "OFFSIDE: ARG 1 - HOL 2" in text
        assert "PASES ACERTADOS: ARG 87% - HOL 85%" in text
        assert "TARJETAS AMARILLAS: ARG 1 - HOL 0" in text
        assert "TARJETAS ROJAS: ARG 0 - HOL 0" in text

    def test_stats_lines_appear_in_documented_order(self):
        """Triangulation: verify the 10 stat lines appear in the correct
        sequence within the stats section."""
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        home_stats = TeamStats(
            name="Argentina", possession="55%", expected_goals="1.90",
        )
        away_stats = TeamStats(
            name="Holanda", possession="45%", expected_goals="1.20",
        )
        ms.update_fixture(
            make_match_state(
                elapsed=67, short="2H",
                home_stats=home_stats, away_stats=away_stats,
            )
        )

        text = ms.get_context_text()

        # Extract just the stats section
        stats_section = text.split("\n\n")
        # Find the section that starts with POSESIÓN
        stats_lines = None
        for section in stats_section:
            if section.startswith("POSESIÓN"):
                stats_lines = section.split("\n")
                break

        assert stats_lines is not None
        assert len(stats_lines) == 10
        # Verify order by checking the label of each line
        labels = [line.split(":")[0] for line in stats_lines]
        assert labels == [
            "POSESIÓN", "TIROS AL ARCO", "xG", "TIROS TOTALES",
            "CÓRNERES", "FOULTAS", "OFFSIDE", "PASES ACERTADOS",
            "TARJETAS AMARILLAS", "TARJETAS ROJAS",
        ]

    def test_team_abbr_for_short_name_uses_full_uppercased(self):
        """Spec edge case: team name < 3 chars uses the full name
        uppercased as the abbr (no slicing to 0 chars).
        """
        from backend.services.match_state import _team_abbr

        assert _team_abbr("PSG") == "PSG"
        assert _team_abbr("Barça") == "BAR"
        # Edge: exactly 2 chars → full name.
        assert _team_abbr("FC") == "FC"
        # Edge: 1 char → full name.
        assert _team_abbr("A") == "A"


# ---------------------------------------------------------------------------
# Context text — standout players
# ---------------------------------------------------------------------------


class TestContextTextStandouts:
    def test_standout_section_header_includes_rating_label(self):
        """Spec: header is `JUGADORES DESTACADOS (por rating):`.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(
            make_match_state(
                elapsed=67,
                short="2H",
                home_players=[make_player("L. Messi", rating="8.5")],
            )
        )

        text = ms.get_context_text()

        assert "JUGADORES DESTACADOS (por rating):" in text

    def test_standout_players_sorted_by_rating_descending(self):
        """Spec triangulation: players with rating >= 7.0 are listed
        in descending rating order. Cap at 3.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        home_players = [
            make_player("De Paul", rating="7.2"),
            make_player("L. Messi", rating="8.5"),
            make_player("N. Molina", rating="7.8"),
        ]
        ms.update_fixture(
            make_match_state(
                elapsed=67,
                short="2H",
                home_players=home_players,
            )
        )

        text = ms.get_context_text()

        # Lines must appear in rating-descending order.
        messi_idx = text.find("- L. Messi (8.5)")
        molina_idx = text.find("- N. Molina (7.8)")
        depaul_idx = text.find("- De Paul (7.2)")
        assert messi_idx > 0 and molina_idx > 0 and depaul_idx > 0
        assert messi_idx < molina_idx < depaul_idx

    def test_standout_capped_at_three_players(self):
        """Triangulation: even with 4 standouts, only 3 are listed.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        home_players = [
            make_player("A", rating="9.0"),
            make_player("B", rating="8.0"),
            make_player("C", rating="7.5"),
            make_player("D", rating="7.1"),
        ]
        ms.update_fixture(
            make_match_state(elapsed=67, short="2H", home_players=home_players)
        )

        text = ms.get_context_text()

        assert "- A (9.0)" in text
        assert "- B (8.0)" in text
        assert "- C (7.5)" in text
        # D (7.1) is the 4th — MUST NOT appear in standouts.
        assert "- D (7.1)" not in text

    def test_standout_with_all_below_threshold_renders_sin_datos(self):
        """Spec: when no player has rating >= 7.0, the section is
        `JUGADORES DESTACADOS: Sin datos suficientes` (note: the
        `(por rating):` header is REPLACED by `Sin datos suficientes`).
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        home_players = [
            make_player("C. Romero", rating="6.9"),
            make_player("N. Otamendi", rating="6.7"),
        ]
        ms.update_fixture(
            make_match_state(elapsed=67, short="2H", home_players=home_players)
        )

        text = ms.get_context_text()

        assert "JUGADORES DESTACADOS: Sin datos suficientes" in text
        # Make sure the header-with-colon variant is NOT used here.
        assert "JUGADORES DESTACADOS (por rating):" not in text


# ---------------------------------------------------------------------------
# Context text — weak players
# ---------------------------------------------------------------------------


class TestContextTextWeak:
    def test_weak_players_listed_sorted_ascending(self):
        """Spec: 0 < rating < 6.5, sorted ascending (worst first). Cap at 2.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        home_players = [
            make_player("L. Martínez", rating="6.1"),
            make_player("M. Acuña", rating="6.3"),
        ]
        ms.update_fixture(
            make_match_state(elapsed=67, short="2H", home_players=home_players)
        )

        text = ms.get_context_text()

        # Worst (6.1) MUST appear before better (6.3).
        worst_idx = text.find("- L. Martínez (6.1)")
        better_idx = text.find("- M. Acuña (6.3)")
        assert worst_idx > 0 and better_idx > 0
        assert worst_idx < better_idx

    def test_weak_players_capped_at_two(self):
        """Triangulation: only 2 weak players are listed even if more qualify.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        home_players = [
            make_player("P1", rating="5.5"),
            make_player("P2", rating="5.8"),
            make_player("P3", rating="6.0"),
        ]
        ms.update_fixture(
            make_match_state(elapsed=67, short="2H", home_players=home_players)
        )

        text = ms.get_context_text()

        assert "- P1 (5.5)" in text
        assert "- P2 (5.8)" in text
        assert "- P3 (6.0)" not in text

    def test_weak_with_all_above_or_equal_6_5_renders_sin_datos(self):
        """Spec: rating 6.5 or higher (or 0) is NOT weak.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        home_players = [
            make_player("E. Martínez", rating="6.5"),  # boundary, NOT weak
            make_player("R. De Paul", rating="6.7"),
        ]
        ms.update_fixture(
            make_match_state(elapsed=67, short="2H", home_players=home_players)
        )

        text = ms.get_context_text()

        assert "JUGADORES FLOJOS: Sin datos suficientes" in text

    def test_weak_excludes_zero_rating(self):
        """Triangulation: rating 0 (unrated, parsed from empty string)
        MUST NOT be flagged as weak — the rule is `0 < rating < 6.5`.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        home_players = [
            make_player("Bench", rating="0"),  # would otherwise be the worst
        ]
        ms.update_fixture(
            make_match_state(elapsed=67, short="2H", home_players=home_players)
        )

        text = ms.get_context_text()

        assert "JUGADORES FLOJOS: Sin datos suficientes" in text


# ---------------------------------------------------------------------------
# Context text — substitutions
# ---------------------------------------------------------------------------


class TestContextTextSubstitutions:
    def test_substitution_with_event_renders_out_in_minute(self):
        """Spec: subst events → `{out} → {in} ({minute}')`.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=85, short="2H"))
        events = [
            MatchEvent(
                minute=82,
                team="Argentina",
                player="L. Martínez",
                type="subst",
                detail="Substitution 1",
                assist="L. Paredes",
            ),
        ]
        ms.update_details(events, None, None, [], [])

        text = ms.get_context_text()

        assert "CAMBIOS REALIZADOS: L. Martínez → L. Paredes (82')" in text

    def test_no_substitutions_renders_ninguno(self):
        """Spec: empty subst events → `CAMBIOS REALIZADOS: Ninguno`.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=15, short="1H"))

        text = ms.get_context_text()

        assert "CAMBIOS REALIZADOS: Ninguno" in text


# ---------------------------------------------------------------------------
# Context text — cards
# ---------------------------------------------------------------------------


class TestContextTextCards:
    def test_yellow_card_renders_with_yellow_emoji(self):
        """Spec: 'Yellow Card' detail → 🟨.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=80, short="2H"))
        events = [
            MatchEvent(
                minute=78,
                team="Argentina",
                player="N. Montiel",
                type="Card",
                detail="Yellow Card",
            ),
        ]
        ms.update_details(events, None, None, [], [])

        text = ms.get_context_text()

        assert "TARJETAS: N. Montiel 🟨 (78')" in text

    def test_red_card_renders_with_red_emoji(self):
        """Spec: detail containing 'Red' → 🟥.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=80, short="2H"))
        events = [
            MatchEvent(
                minute=60,
                team="Argentina",
                player="Some Player",
                type="Card",
                detail="Red Card",
            ),
        ]
        ms.update_details(events, None, None, [], [])

        text = ms.get_context_text()

        assert "TARJETAS: Some Player 🟥 (60')" in text

    def test_no_cards_renders_ninguna(self):
        """Spec: empty cards → `TARJETAS: Ninguna`.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=15, short="1H"))

        text = ms.get_context_text()

        assert "TARJETAS: Ninguna" in text


# ---------------------------------------------------------------------------
# Pre-kickoff snapshot — every empty variant
# ---------------------------------------------------------------------------


class TestPreKickoffSnapshot:
    def test_pre_kickoff_uses_every_empty_section_variant(self):
        """Spec: 'Pre-kickoff uses every empty-section variant'.

        When events=[], stats=None, players=[], elapsed=0, every
        section that has an empty variant must use it.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=0, short="1H", home_goals=0, away_goals=0))

        text = ms.get_context_text()

        assert "FORMACIONES: No disponibles aún" in text
        assert "GOLES: Sin goles aún" in text
        assert "ESTADÍSTICAS: No disponibles aún" in text
        assert "JUGADORES DESTACADOS: Sin datos suficientes" in text
        assert "JUGADORES FLOJOS: Sin datos suficientes" in text
        assert "TODOS LOS JUGADORES: Sin datos suficientes" in text
        assert "CAMBIOS REALIZADOS: Ninguno" in text
        assert "TARJETAS: Ninguna" in text

    def test_pre_kickoff_output_has_nine_sections_separated_by_blank_lines(self):
        """Spec: 9 sections in fixed order, `\\n\\n` separator, single trailing `\\n`.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.update_fixture(make_match_state(elapsed=0, short="1H"))

        text = ms.get_context_text()

        # Split on `\n\n` to count sections.
        sections = text.split("\n\n")
        # 9 sections + 1 (the trailing \n leaves a trailing empty after the last split).
        assert len(sections) == 9
        # Trailing newline: text MUST end with exactly one '\n'.
        assert text.endswith("\n")
        assert not text.endswith("\n\n")


# ---------------------------------------------------------------------------
# FULL SNAPSHOT — minute 67, all data populated, byte-pinned
# ---------------------------------------------------------------------------


class TestFullSnapshotMinute67:
    def test_snapshot_at_minute_67_matches_pinned_format(self):
        """Spec: 'Snapshot at minute 67 matches the pinned format'.

        This is THE canonical snapshot. Build a hand-crafted state
        at minute 67 with Argentina 2-1 Holanda, the 5 events listed
        in the spec, populated stats, and standouts (no weak).
        Assert the EXACT full output string with all 9 sections,
        `\\n\\n` separators, and trailing `\\n`.
        """
        from backend.services.match_state import MatchStateManager

        home_stats = TeamStats(
            name="Argentina",
            possession="50%",
            shots_on_goal=3,
            total_shots=7,
            corners=3,
            fouls=9,
            offsides=1,
            yellow_cards=1,
            red_cards=0,
            pass_accuracy="87%",
            expected_goals="1.90",
        )
        away_stats = TeamStats(
            name="Holanda",
            possession="50%",
            shots_on_goal=2,
            total_shots=5,
            corners=2,
            fouls=10,
            offsides=2,
            yellow_cards=0,
            red_cards=0,
            pass_accuracy="85%",
            expected_goals="1.20",
        )
        home_players = [
            make_player("E. Martínez", rating="6.7", dribbles_success=1, dribbles_attempts=2),
            make_player(
                "L. Messi",
                rating="8.5",
                goals=1,
                assists=1,
                key_passes=3,
                dribbles_success=4,
                dribbles_attempts=6,
            ),
            make_player(
                "N. Molina",
                rating="7.8",
                goals=1,
                key_passes=2,
                dribbles_success=1,
                dribbles_attempts=3,
            ),
            make_player("N. Otamendi", rating="6.7", dribbles_success=1, dribbles_attempts=2),
        ]
        events = [
            MatchEvent(
                minute=35,
                team="Argentina",
                player="N. Molina",
                type="Goal",
                detail="Normal Goal",
                assist="L. Messi",
            ),
            MatchEvent(
                minute=73,
                team="Argentina",
                player="L. Messi",
                type="Goal",
                detail="Penalty",
            ),
            MatchEvent(
                minute=83,
                team="Holanda",
                player="W. Weghorst",
                type="Goal",
                detail="Normal Goal",
                assist="D. Blind",
            ),
            MatchEvent(
                minute=78,
                team="Argentina",
                player="N. Montiel",
                type="Card",
                detail="Yellow Card",
            ),
            MatchEvent(
                minute=82,
                team="Argentina",
                player="L. Martínez",
                type="subst",
                detail="Substitution 1",
                assist="L. Paredes",
            ),
        ]
        ms = MatchStateManager()
        ms.update_fixture(
            make_match_state(
                elapsed=67,
                short="2H",
                home_goals=2,
                away_goals=1,
                home_stats=home_stats,
                away_stats=away_stats,
                home_players=home_players,
            )
        )
        ms.update_details(events, home_stats, away_stats, home_players, [])

        text = ms.get_context_text()

        # make_player gives: minutes=67, shots_total=1, shots_on=1,
        # passes_total=30, pass_accuracy="85%", duels_won=3, duels_total=5,
        # fouls_committed=1, fouls_drawn=2, yellow_cards=0, red_cards=0
        #
        # Messi enriched: 67', 1 gol, 1 asistencia, 1/1 al arco,
        #   30 pases (85%), 3 pases clave, 4/6 regates, 3/5 duelos,
        #   1 falta, 2 faltas recibidas
        #
        # Molina enriched: 67', 1 gol, 1/1 al arco,
        #   30 pases (85%), 2 pases clave, 1/3 regates, 3/5 duelos,
        #   1 falta, 2 faltas recibidas
        expected = (
            "⚽ Argentina 2 - 1 Holanda | Minuto 67 | 2do Tiempo\n"
            "\n"
            "FORMACIONES: No disponibles aún\n"
            "\n"
            "GOLES: N. Molina (35'), L. Messi (pen 73') - W. Weghorst (83')\n"
            "\n"
            "POSESIÓN: ARG 50% - HOL 50%\n"
            "TIROS AL ARCO: ARG 3 - HOL 2\n"
            "xG: ARG 1.90 - HOL 1.20\n"
            "TIROS TOTALES: ARG 7 - HOL 5\n"
            "CÓRNERES: ARG 3 - HOL 2\n"
            "FOULTAS: ARG 9 - HOL 10\n"
            "OFFSIDE: ARG 1 - HOL 2\n"
            "PASES ACERTADOS: ARG 87% - HOL 85%\n"
            "TARJETAS AMARILLAS: ARG 1 - HOL 0\n"
            "TARJETAS ROJAS: ARG 0 - HOL 0\n"
            "\n"
            "JUGADORES DESTACADOS (por rating):\n"
            "- L. Messi (8.5) - 67', 1 gol, 1 asistencia, 1/1 al arco, 30 pases (85%), 3 pases clave, 4/6 regates, 3/5 duelos, 1 falta, 2 faltas recibidas\n"
            "- N. Molina (7.8) - 67', 1 gol, 1/1 al arco, 30 pases (85%), 2 pases clave, 1/3 regates, 3/5 duelos, 1 falta, 2 faltas recibidas\n"
            "\n"
            "JUGADORES FLOJOS: Sin datos suficientes\n"
            "\n"
            "TODOS LOS JUGADORES: Sin datos suficientes\n"
            "\n"
            "CAMBIOS REALIZADOS: L. Martínez → L. Paredes (82')\n"
            "\n"
            "TARJETAS: N. Montiel 🟨 (78')\n"
        )
        assert text == expected


# ---------------------------------------------------------------------------
# Player highlights helper
# ---------------------------------------------------------------------------


class TestPlayerHighlights:
    def test_highlights_with_full_stats_includes_all_fields(self):
        """Spec: enriched highlights include minutes, goals, assists,
        shots, passes, key passes, dribbles, duels, fouls, cards."""
        from backend.services.match_state import _player_highlights

        p = PlayerStats(
            name="Messi",
            position="FW",
            rating="8.5",
            minutes=67,
            goals=1,
            assists=1,
            shots_total=5,
            shots_on=3,
            passes_total=60,
            key_passes=4,
            pass_accuracy="88%",
            duels_won=10,
            duels_total=15,
            dribbles_success=4,
            dribbles_attempts=6,
            fouls_committed=1,
            fouls_drawn=5,
            yellow_cards=1,
            red_cards=0,
        )
        result = _player_highlights(p)

        # Minutes always shown
        assert "67'" in result
        # Goals
        assert "1 gol" in result
        # Assists
        assert "1 asistencia" in result
        # Shots (shots_on/shots_total al arco)
        assert "3/5 al arco" in result
        # Passes (total pases (accuracy))
        assert "60 pases (88%)" in result
        # Key passes
        assert "4 pases clave" in result
        # Dribbles always shown
        assert "4/6 regates" in result
        # Duels
        assert "10/15 duelos" in result
        # Fouls committed
        assert "1 falta" in result
        # Fouls drawn
        assert "5 faltas recibidas" in result
        # Yellow card
        assert "1 amarilla" in result

    def test_highlights_with_all_zeros_shows_only_minutes_and_dribbles(self):
        """Spec: when all stats are zero, only minutes and dribbles appear."""
        from backend.services.match_state import _player_highlights

        p = PlayerStats(
            name="Sub",
            position="M",
            rating="6.0",
            minutes=15,
            goals=0,
            assists=0,
            shots_total=0,
            shots_on=0,
            passes_total=0,
            key_passes=0,
            pass_accuracy="",
            duels_won=0,
            duels_total=0,
            dribbles_success=0,
            dribbles_attempts=0,
            fouls_committed=0,
            fouls_drawn=0,
            yellow_cards=0,
            red_cards=0,
        )
        result = _player_highlights(p)

        # Minutes always, dribbles always
        assert "15'" in result
        assert "0/0 regates" in result
        # Nothing else (no goals, assists, shots, passes, etc.)
        assert "gol" not in result
        assert "asistencia" not in result
        assert "al arco" not in result
        assert "pases" not in result
        assert "duelos" not in result
        assert "falta" not in result

    def test_highlights_pluralization_for_goals_and_assists(self):
        """Triangulation: singular/plural for gol/goles, asistencia/asistencias,
        falta/faltas, amarilla/amarillas."""
        from backend.services.match_state import _player_highlights

        p_one = PlayerStats(
            name="A", position="F", rating="7.0", minutes=90,
            goals=1, assists=1, fouls_committed=1, fouls_drawn=1,
            yellow_cards=1, dribbles_success=1, dribbles_attempts=1,
        )
        p_multi = PlayerStats(
            name="B", position="F", rating="7.0", minutes=90,
            goals=2, assists=2, fouls_committed=2, fouls_drawn=2,
            yellow_cards=2, dribbles_success=1, dribbles_attempts=1,
        )

        one = _player_highlights(p_one)
        multi = _player_highlights(p_multi)

        assert "1 gol" in one
        assert "1 asistencia" in one
        assert "1 falta" in one
        assert "1 falta recibida" in one
        assert "1 amarilla" in one

        assert "2 goles" in multi
        assert "2 asistencias" in multi
        assert "2 faltas" in multi
        assert "2 faltas recibidas" in multi
        assert "2 amarillas" in multi


class TestParseRating:
    def test_empty_string_parses_to_zero(self):
        """Spec edge case: rating="" → 0.0 (a player who has not
        received a rating MUST NOT appear in standouts OR weak).
        """
        from backend.services.match_state import _parse_rating

        assert _parse_rating("") == 0.0
        assert _parse_rating("0") == 0.0
        assert _parse_rating("7.5") == 7.5
        assert _parse_rating(None) == 0.0  # defensive

    def test_valid_rating_parses_to_float(self):
        """Triangulation: a typical rating string parses cleanly.
        """
        from backend.services.match_state import _parse_rating

        assert _parse_rating("8.2") == 8.2
        assert _parse_rating("6.0") == 6.0


# ---------------------------------------------------------------------------
# Prediction log
# ---------------------------------------------------------------------------


class TestPredictionLog:
    def test_get_predictions_empty_initially(self):
        """Triangulation: a fresh manager has no predictions.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()

        assert ms.get_predictions() == []

    def test_save_prediction_round_trips(self):
        """Spec: 'Save then read round-trips'.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()

        ms.save_prediction(momento=3, content="pred A")

        preds = ms.get_predictions()
        assert len(preds) == 1
        assert preds[0].momento == 3
        assert preds[0].content == "pred A"
        # Timestamp is set to a tz-aware UTC datetime.
        assert isinstance(preds[0].timestamp, datetime)
        assert preds[0].timestamp.tzinfo is not None

    def test_predictions_preserve_append_order(self):
        """Spec: 'Predictions preserve append order'.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.save_prediction(momento=1, content="A")
        ms.save_prediction(momento=3, content="B")
        ms.save_prediction(momento=6, content="C")

        preds = ms.get_predictions()
        assert [p.momento for p in preds] == [1, 3, 6]
        assert [p.content for p in preds] == ["A", "B", "C"]

    def test_save_prediction_momento_above_six_raises_value_error(self):
        """Spec: 'Out-of-range momento is rejected'.

        The Pydantic Prediction model enforces momento in 1..=6;
        momento=7 MUST raise a ValidationError (a subclass of
        ValueError).
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()

        with pytest.raises((ValueError, ValidationError)):
            ms.save_prediction(momento=7, content="x")

    def test_save_prediction_momento_below_one_raises(self):
        """Triangulation: momento=0 is also out of range.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()

        with pytest.raises((ValueError, ValidationError)):
            ms.save_prediction(momento=0, content="x")

    def test_get_predictions_returns_a_copy(self):
        """Triangulation: get_predictions returns a copy, not the
        internal list. Mutating the returned list MUST NOT affect
        the next call.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()
        ms.save_prediction(momento=1, content="A")

        preds = ms.get_predictions()
        preds.clear()

        assert len(ms.get_predictions()) == 1


# ---------------------------------------------------------------------------
# get_context_text gating
# ---------------------------------------------------------------------------


class TestContextTextGating:
    def test_get_context_text_before_update_fixture_raises(self):
        """Spec: get_state() raises before update_fixture. So must
        get_context_text() — it depends on the same state.
        """
        from backend.services.match_state import MatchStateManager

        ms = MatchStateManager()

        with pytest.raises(RuntimeError):
            ms.get_context_text()


# ---------------------------------------------------------------------------
# Module surface
# ---------------------------------------------------------------------------


class TestModuleSurface:
    def test_period_names_constant_is_exported(self):
        """Spec: the PERIOD_NAMES map covers all 19 API-Football v3
        statuses with the exact Spanish labels from the proposal.

        Previously the map had only 4 entries; the live API emits
        19 distinct statuses (TBD, NS, 1H, HT, 2H, ET, BT, P, SUSP,
        INT, FT, AET, PEN, PST, CANC, ABD, AWD, WO, LIVE). The
        fallback for any unknown status is the raw `short` value.

        The proposal text says "all 18" but the mapping table and
        the live API both have 19 entries; we pin the table.
        """
        from backend.services.match_state import PERIOD_NAMES

        assert len(PERIOD_NAMES) == 19
        assert PERIOD_NAMES == {
            "TBD": "Horario a confirmar",
            "NS": "No iniciado",
            "1H": "1er Tiempo",
            "HT": "Entretiempo",
            "2H": "2do Tiempo",
            "ET": "Tiempo extra",
            "BT": "Descanso tiempo extra",
            "P": "Penales en curso",
            "SUSP": "Suspendido",
            "INT": "Interrumpido",
            "FT": "Final",
            "AET": "Final (tiempo extra)",
            "PEN": "Final (penales)",
            "PST": "Postergado",
            "CANC": "Cancelado",
            "ABD": "Abandonado",
            "AWD": "Perdida por regla",
            "WO": "Ganado por ausencia",
            "LIVE": "En curso",
        }


# ---------------------------------------------------------------------------
# MOMENTO_STATUSES — the 6-key map from momento (1..6) to FixtureStatus.
# Spec: openspec/changes/backend-api/specs/match-state-manager/spec.md
# ---------------------------------------------------------------------------


class TestMomentoStatuses:
    def test_momento_statuses_all_six(self):
        """Spec: `MOMENTO_STATUSES` MUST be a `dict[int, FixtureStatus]`
        mapping momento keys 0..6 to the corresponding fixture statuses.

        Pins every (elapsed, short, long) triple so a drift on any
        single value is caught immediately.
        """
        from backend.services.match_state import MOMENTO_STATUSES

        assert set(MOMENTO_STATUSES.keys()) == {0, 1, 2, 3, 4, 5, 6}

        expected: dict[int, tuple[int, str, str]] = {
            0: (0, "NS", "Not Started"),
            1: (15, "1H", "First Half"),
            2: (30, "1H", "First Half"),
            3: (45, "HT", "Halftime"),
            4: (60, "2H", "Second Half"),
            5: (75, "2H", "Second Half"),
            6: (120, "PEN", "Match Finished After Penalty"),
        }

        for momento, (elapsed, short, long_) in expected.items():
            status = MOMENTO_STATUSES[momento]
            assert status.elapsed == elapsed, f"momento {momento} elapsed"
            assert status.short == short, f"momento {momento} short"
            assert status.long == long_, f"momento {momento} long"

    def test_momento_statuses_values_are_fixture_status_instances(self):
        """Triangulation: every value is a real `FixtureStatus` instance,
        not a plain dict — the endpoints rely on attribute access.
        """
        from backend.models import FixtureStatus
        from backend.services.match_state import MOMENTO_STATUSES

        for momento, status in MOMENTO_STATUSES.items():
            assert isinstance(status, FixtureStatus), f"momento {momento}"
