"""Tests for backend Pydantic v2 match-data models.

Covers every scenario in openspec/changes/backend-foundation/specs/match-data-models/spec.md
plus triangulation cases that exercise the actual constraint logic
(not just happy-path smoke tests).
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.models import (
    FixtureStatus,
    MatchEvent,
    MatchState,
    PlayerStats,
    Prediction,
    TeamScore,
    TeamStats,
)


# ---------------------------------------------------------------------------
# Requirement: FixtureStatus and TeamScore
# ---------------------------------------------------------------------------

class TestFixtureStatus:
    def test_valid_round_trip_preserves_values(self):
        """Spec: 'Valid fixture status and team score round-trip' — happy path."""
        status = FixtureStatus(elapsed=67, short="2H", long="Second Half")
        assert status.elapsed == 67
        assert status.short == "2H"
        assert status.long == "Second Half"

    def test_valid_team_score_round_trip(self):
        score = TeamScore(id=26, name="Argentina", goals=2)
        assert score.id == 26
        assert score.name == "Argentina"
        assert score.goals == 2

    def test_empty_short_is_rejected(self):
        """Spec: 'Empty status short is rejected'."""
        with pytest.raises(ValidationError):
            FixtureStatus(elapsed=0, short="", long="Not Started")

    def test_unknown_short_value_is_rejected(self):
        """Triangulation: any value outside the Literal set must be rejected."""
        with pytest.raises(ValidationError):
            FixtureStatus(elapsed=10, short="3H", long="Extra Half")

    def test_long_must_be_non_empty(self):
        """Triangulation: the min_length=1 constraint on `long` is enforced."""
        with pytest.raises(ValidationError):
            FixtureStatus(elapsed=0, short="HT", long="")

    def test_elapsed_must_be_non_negative(self):
        """Triangulation: extra time allowed (e.g. 101) but negatives are not."""
        with pytest.raises(ValidationError):
            FixtureStatus(elapsed=-1, short="2H", long="Second Half")

    def test_elapsed_accepts_extra_time_above_90(self):
        """Spec note: extra time allowed, e.g. 101. Confirm upper bound is open."""
        status = FixtureStatus(elapsed=101, short="FT", long="Full Time")
        assert status.elapsed == 101

    def test_team_id_must_be_positive(self):
        """Triangulation: gt=0 on TeamScore.id."""
        with pytest.raises(ValidationError):
            TeamScore(id=0, name="Argentina", goals=0)

    def test_team_name_must_be_non_empty(self):
        """Triangulation: min_length=1 on TeamScore.name."""
        with pytest.raises(ValidationError):
            TeamScore(id=1, name="", goals=0)

    def test_team_goals_must_be_non_negative(self):
        """Triangulation: ge=0 on TeamScore.goals."""
        with pytest.raises(ValidationError):
            TeamScore(id=1, name="Argentina", goals=-1)


# ---------------------------------------------------------------------------
# Requirement: MatchEvent
# ---------------------------------------------------------------------------

class TestMatchEvent:
    def test_goal_event_with_assist_is_valid(self):
        """Spec: 'Goal event with assist is valid'."""
        event = MatchEvent(
            minute=35,
            team="Argentina",
            player="Molina",
            type="Goal",
            detail="Normal Goal",
            assist="Messi",
        )
        assert event.assist == "Messi"
        assert event.type == "Goal"

    def test_card_event_with_null_assist_is_valid(self):
        """Spec: 'Card event with null assist'."""
        event = MatchEvent(
            minute=78,
            team="Argentina",
            player="Montiel",
            type="Card",
            detail="Yellow Card",
            assist=None,
        )
        assert event.assist is None
        assert event.type == "Card"

    def test_unknown_event_type_is_rejected(self):
        """Spec: 'Unknown event type is rejected'."""
        with pytest.raises(ValidationError):
            MatchEvent(
                minute=50,
                team="Argentina",
                player="Di Maria",
                type="PenaltySaved",
                detail="Saved",
                assist=None,
            )

    def test_substitution_event_is_valid(self):
        """Triangulation: third Literal value 'subst' must be accepted."""
        event = MatchEvent(
            minute=82,
            team="Argentina",
            player="Lautaro",
            type="subst",
            detail="Substitution 1",
            assist=None,
        )
        assert event.type == "subst"

    def test_minute_must_be_non_negative(self):
        """Triangulation: ge=0 on minute."""
        with pytest.raises(ValidationError):
            MatchEvent(
                minute=-5,
                team="Argentina",
                player="Messi",
                type="Goal",
                detail="Offside",
                assist=None,
            )

    def test_team_and_player_must_be_non_empty(self):
        """Triangulation: min_length=1 on team and player."""
        with pytest.raises(ValidationError):
            MatchEvent(
                minute=10,
                team="",
                player="Messi",
                type="Goal",
                detail="x",
                assist=None,
            )
        with pytest.raises(ValidationError):
            MatchEvent(
                minute=10,
                team="Argentina",
                player="",
                type="Goal",
                detail="x",
                assist=None,
            )


# ---------------------------------------------------------------------------
# Requirement: PlayerStats and TeamStats
# ---------------------------------------------------------------------------

class TestPlayerStats:
    def test_substitute_defaults_to_false(self):
        """Spec: 'PlayerStats substitute defaults to False'."""
        player = PlayerStats(
            name="Emiliano Martinez",
            position="GK",
            rating="6.5",
            minutes=90,
            goals=0,
            assists=0,
            shots_total=0,
            shots_on=0,
            passes_total=42,
            key_passes=0,
            pass_accuracy="78%",
            duels_won=2,
            duels_total=3,
            dribbles_success=0,
            dribbles_attempts=0,
            fouls_committed=0,
            fouls_drawn=0,
            yellow_cards=0,
            red_cards=0,
        )
        assert player.substitute is False

    def test_substitute_can_be_explicitly_true(self):
        """Triangulation: explicit True is preserved (not just defaulted)."""
        player = PlayerStats(
            name="Paredes",
            position="CM",
            rating="6.0",
            minutes=8,
            goals=0,
            assists=0,
            shots_total=0,
            shots_on=0,
            passes_total=12,
            key_passes=0,
            pass_accuracy="83%",
            duels_won=1,
            duels_total=2,
            dribbles_success=0,
            dribbles_attempts=0,
            fouls_committed=0,
            fouls_drawn=0,
            yellow_cards=0,
            red_cards=0,
            substitute=True,
        )
        assert player.substitute is True

    def test_rating_stays_string(self):
        """Triangulation: rating must remain a string, not coerced to float."""
        player = PlayerStats(
            name="Messi",
            position="RW",
            rating="8.2",
            minutes=90,
            goals=1,
            assists=1,
            shots_total=5,
            shots_on=3,
            passes_total=60,
            key_passes=3,
            pass_accuracy="88%",
            duels_won=10,
            duels_total=15,
            dribbles_success=4,
            dribbles_attempts=6,
            fouls_committed=1,
            fouls_drawn=5,
            yellow_cards=0,
            red_cards=0,
        )
        assert isinstance(player.rating, str)
        assert player.rating == "8.2"


class TestTeamStats:
    def test_possession_stays_string(self):
        """Spec: 'TeamStats possession stays a string'."""
        stats = TeamStats(
            name="Argentina",
            possession="44%",
            shots_on_goal=3,
            total_shots=8,
            corners=4,
            fouls=11,
            offsides=2,
            yellow_cards=2,
            red_cards=0,
            pass_accuracy="87%",
            expected_goals="1.78",
        )
        assert stats.possession == "44%"
        assert isinstance(stats.possession, str)
        # And the other "str stays str" fields from the spec
        assert stats.pass_accuracy == "87%"
        assert stats.expected_goals == "1.78"
        assert isinstance(stats.pass_accuracy, str)
        assert isinstance(stats.expected_goals, str)

    def test_numeric_fields_are_ints(self):
        """Triangulation: numeric stats must be ints, not coerced from strings."""
        stats = TeamStats(
            name="Holland",
            possession="56%",
            shots_on_goal=2,
            total_shots=6,
            corners=3,
            fouls=9,
            offsides=1,
            yellow_cards=1,
            red_cards=0,
            pass_accuracy="83%",
            expected_goals="1.42",
        )
        assert isinstance(stats.shots_on_goal, int)
        assert stats.shots_on_goal == 2
        assert stats.total_shots == 6


# ---------------------------------------------------------------------------
# Requirement: MatchState and Prediction
# ---------------------------------------------------------------------------

class TestMatchState:
    def test_at_minute_zero_with_empty_lists_and_none_stats_is_valid(self):
        """Spec: 'MatchState at minute 0 has no stats or events'."""
        state = MatchState(
            fixture_id=868019,
            status=FixtureStatus(elapsed=0, short="1H", long="First Half"),
            home=TeamScore(id=26, name="Argentina", goals=0),
            away=TeamScore(id=24, name="Holland", goals=0),
            events=[],
            home_stats=None,
            away_stats=None,
            home_players=[],
            away_players=[],
            last_updated=datetime(2022, 12, 9, 20, 0, 0, tzinfo=timezone.utc),
        )
        assert state.fixture_id == 868019
        assert state.events == []
        assert state.home_players == []
        assert state.away_players == []
        assert state.home_stats is None
        assert state.away_stats is None
        assert isinstance(state.last_updated, datetime)

    def test_match_state_with_populated_data(self):
        """Triangulation: a fully populated MatchState round-trips end-to-end."""
        event = MatchEvent(
            minute=35,
            team="Argentina",
            player="Molina",
            type="Goal",
            detail="Normal Goal",
            assist="Messi",
        )
        home_stats = TeamStats(
            name="Argentina",
            possession="48%",
            shots_on_goal=3,
            total_shots=7,
            corners=3,
            fouls=8,
            offsides=2,
            yellow_cards=1,
            red_cards=0,
            pass_accuracy="85%",
            expected_goals="1.65",
        )
        state = MatchState(
            fixture_id=868019,
            status=FixtureStatus(elapsed=35, short="1H", long="First Half"),
            home=TeamScore(id=26, name="Argentina", goals=1),
            away=TeamScore(id=24, name="Holland", goals=0),
            events=[event],
            home_stats=home_stats,
            away_stats=None,
            home_players=[],
            away_players=[],
            last_updated=datetime(2022, 12, 9, 20, 35, 0, tzinfo=timezone.utc),
        )
        assert len(state.events) == 1
        assert state.events[0].player == "Molina"
        assert state.home_stats.possession == "48%"
        assert state.home.goals == 1


class TestPrediction:
    def test_momento_in_range_is_valid(self):
        """Triangulation: bounds 1..=6 — values at the edges (1, 6) must work."""
        for momento in (1, 2, 3, 4, 5, 6):
            pred = Prediction(
                momento=momento,
                timestamp=datetime(2022, 12, 9, 20, 0, 0, tzinfo=timezone.utc),
                content="x",
            )
            assert pred.momento == momento

    def test_momento_above_six_is_rejected(self):
        """Spec: 'Prediction momento is bounded 1-6' (7 must be rejected)."""
        with pytest.raises(ValidationError):
            Prediction(
                momento=7,
                timestamp=datetime(2022, 12, 9, 20, 0, 0, tzinfo=timezone.utc),
                content="x",
            )

    def test_momento_below_one_is_rejected(self):
        """Triangulation: 0 is outside 1..=6 and must be rejected."""
        with pytest.raises(ValidationError):
            Prediction(
                momento=0,
                timestamp=datetime(2022, 12, 9, 20, 0, 0, tzinfo=timezone.utc),
                content="x",
            )
