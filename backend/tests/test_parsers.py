"""Tests for backend API-Football v3 parsers.

Covers every scenario in
openspec/changes/backend-foundation/specs/api-football-parsing/spec.md
plus triangulation cases that exercise real code paths (extra-time
minutes, skipped unknown event types, full 11-player team rosters,
null safety in statistics, etc.).

The test dicts match the real API-Football v3 response shape — not
the Pydantic model — so these tests pin the contract between the
network layer and the parser.
"""
import pytest

from backend.models import MatchEvent, MatchState, PlayerStats, TeamStats
from backend.parsers import parse_events, parse_fixture, parse_players, parse_statistics


# ---------------------------------------------------------------------------
# Helpers — build hand-crafted API-Football v3 dicts for fixture, events,
# statistics, and players. They centralize the v3 schema so individual tests
# stay focused on the parser's behavior, not on dict construction.
# ---------------------------------------------------------------------------


def make_fixture_dict(
    fixture_id: int = 868019,
    elapsed: int = 0,
    short_status: str = "1H",
    long_status: str = "First Half",
    home_name: str = "Argentina",
    away_name: str = "Holland",
    home_goals: int = 0,
    away_goals: int = 0,
    home_winner: bool | None = None,
    away_winner: bool | None = None,
    fulltime_home: int | None = 0,
    fulltime_away: int | None = 0,
) -> dict:
    """Build a `/fixtures` response element matching the v3 shape."""
    return {
        "fixture": {
            "id": fixture_id,
            "date": "2022-12-09T18:00:00+00:00",
            "status": {
                "long": long_status,
                "short": short_status,
                "elapsed": elapsed,
            },
        },
        "teams": {
            "home": {"id": 26, "name": home_name, "logo": "url", "winner": home_winner},
            "away": {"id": 41, "name": away_name, "logo": "url", "winner": away_winner},
        },
        "goals": {"home": home_goals, "away": away_goals},
        "score": {
            "halftime": {"home": 0, "away": 0},
            "fulltime": {"home": fulltime_home, "away": fulltime_away},
            "extratime": {"home": None, "away": None},
            "penalty": {"home": None, "away": None},
        },
    }


def make_event_dict(
    elapsed: int,
    team_name: str,
    player_name: str,
    event_type: str,
    detail: str = "Normal Goal",
    extra: int | None = None,
    assist_name: str | None = None,
) -> dict:
    """Build a `/fixtures/events` response element matching the v3 shape."""
    return {
        "time": {"elapsed": elapsed, "extra": extra},
        "team": {"id": 26, "name": team_name, "logo": "url"},
        "player": {"id": 1521, "name": player_name},
        "assist": {"id": 154, "name": assist_name} if assist_name else None,
        "type": event_type,
        "detail": detail,
        "comments": None,
    }


def make_stat_entry(stat_type: str, value):
    """Build a single `statistics[]` entry (type/value pair)."""
    return {"type": stat_type, "value": value}


def make_team_statistics(
    team_id: int,
    team_name: str,
    possession: str | None,
    shots_on_goal: int | None,
    total_shots: int | None,
) -> dict:
    """Build a `/fixtures/statistics` response element for one team."""
    return {
        "team": {"id": team_id, "name": team_name, "logo": "url"},
        "statistics": [
            make_stat_entry("Ball Possession", possession),
            make_stat_entry("Shots on Goal", shots_on_goal),
            make_stat_entry("Total Shots", total_shots),
            make_stat_entry("Corner Kicks", 3),
            make_stat_entry("Fouls", 10),
            make_stat_entry("Offsides", 2),
            make_stat_entry("Yellow Cards", 2),
            make_stat_entry("Red Cards", 0),
            make_stat_entry("Passes Accurate", "87%"),
            make_stat_entry("Expected Goals", "1.78"),
        ],
    }


def make_player_dict(
    name: str,
    position: str = "F",
    rating: str = "7.0",
    minutes: int = 90,
    substitute: bool = False,
) -> dict:
    """Build a single player entry inside a team's `players` array."""
    return {
        "player": {"id": 0, "name": name, "photo": "url"},
        "statistics": [
            {
                "games": {
                    "minutes": minutes,
                    "number": 10,
                    "position": position,
                    "rating": rating,
                    "captain": False,
                    "substitute": substitute,
                },
                "shots": {"total": 3, "on": 2},
                "goals": {"total": 1, "assists": 1, "conceded": 0, "saves": 0},
                "passes": {"total": 45, "key": 4, "accuracy": "87%"},
                "duels": {"total": 9, "won": 6},
                "dribbles": {"attempts": 9, "success": 6, "past": 0},
                "fouls": {"drawn": 3, "committed": 1},
                "cards": {"yellow": 1, "yellowred": 0, "red": 0},
                "penalty": {
                    "won": 0,
                    "commited": 0,
                    "scored": 1,
                    "missed": 0,
                    "saved": 0,
                },
            }
        ],
    }


def make_team_players(team_id: int, team_name: str, players: list[dict]) -> dict:
    """Wrap a list of player dicts in the v3 `/fixtures/players` shape."""
    return {
        "team": {"id": team_id, "name": team_name, "logo": "url"},
        "players": players,
    }


# ---------------------------------------------------------------------------
# Requirement: parse_fixture
# ---------------------------------------------------------------------------

class TestParseFixture:
    def test_pre_kickoff_fixture_with_no_events(self):
        """Spec: 'Pre-kickoff fixture with no events'.

        A 0-0 fixture at minute 0 must produce a MatchState with
        empty events, no stats, and the team scores round-tripped.
        """
        raw = make_fixture_dict(elapsed=0, short_status="1H", home_goals=0, away_goals=0)
        state = parse_fixture(raw)

        assert isinstance(state, MatchState)
        assert state.fixture_id == 868019
        assert state.status.elapsed == 0
        assert state.status.short == "1H"
        assert state.events == []
        assert state.home_stats is None
        assert state.away_stats is None
        assert state.home_players == []
        assert state.away_players == []
        assert state.home.name == "Argentina"
        assert state.away.name == "Holland"
        assert state.home.goals == 0
        assert state.away.goals == 0

    def test_extra_time_elapsed_is_preserved(self):
        """Spec: 'Extra-time elapsed is preserved'.

        An elapsed value above 90 (e.g. 101) MUST NOT be clamped.
        The parser treats it as a plain integer.
        """
        raw = make_fixture_dict(
            elapsed=101,
            short_status="FT",
            long_status="Full Time",
            home_goals=2,
            away_goals=2,
        )
        state = parse_fixture(raw)

        assert state.status.elapsed == 101
        assert state.status.short == "FT"

    def test_score_2_2_at_full_time(self):
        """Spec: 'Score 2-2 at full time'.

        Goals from the `goals` block (not the `score.fulltime` block)
        are what power the live UI, so they MUST be extracted verbatim.
        """
        raw = make_fixture_dict(
            elapsed=120,
            short_status="FT",
            long_status="Full Time",
            home_goals=2,
            away_goals=2,
            fulltime_home=2,
            fulltime_away=2,
        )
        state = parse_fixture(raw)

        assert state.home.goals == 2
        assert state.away.goals == 2

    def test_parse_fixture_uses_team_names_from_teams_block(self):
        """Triangulation: team names come from `teams.home.name` and
        `teams.away.name`, not from `goals` or `score`.
        """
        raw = make_fixture_dict(home_name="Argentina", away_name="Netherlands")
        state = parse_fixture(raw)

        assert state.home.name == "Argentina"
        assert state.away.name == "Netherlands"

    def test_parse_fixture_sets_last_updated_to_recent_utc(self):
        """Triangulation: `last_updated` must be a tz-aware UTC datetime
        close to "now" — not a fixed string and not naive.
        """
        from datetime import datetime, timezone, timedelta

        before = datetime.now(tz=timezone.utc)
        state = parse_fixture(make_fixture_dict())
        after = datetime.now(tz=timezone.utc)

        assert isinstance(state.last_updated, datetime)
        assert state.last_updated.tzinfo is not None
        # Within a 5-second window — generous for slow CI.
        assert before - timedelta(seconds=5) <= state.last_updated <= after + timedelta(seconds=5)


# ---------------------------------------------------------------------------
# Requirement: parse_events
# ---------------------------------------------------------------------------

class TestParseEvents:
    def test_goal_event_with_assist(self):
        """Spec: 'Goal event with assist'.

        A Goal event with assist.name="Messi" must produce a
        MatchEvent with assist="Messi" (the assist is a string,
        not a nested dict).
        """
        item = make_event_dict(
            elapsed=35,
            team_name="Argentina",
            player_name="N. Molina",
            event_type="Goal",
            detail="Normal Goal",
            assist_name="L. Messi",
        )
        events = parse_events([item])

        assert len(events) == 1
        assert isinstance(events[0], MatchEvent)
        assert events[0].minute == 35
        assert events[0].team == "Argentina"
        assert events[0].player == "N. Molina"
        assert events[0].type == "Goal"
        assert events[0].detail == "Normal Goal"
        assert events[0].assist == "L. Messi"

    def test_event_with_null_assist(self):
        """Spec: 'Event with null assist'.

        A Goal with assist=None in the source dict must produce a
        MatchEvent with assist=None — not "" and not a missing key.
        """
        item = make_event_dict(
            elapsed=78,
            team_name="Argentina",
            player_name="G. Montiel",
            event_type="Card",
            detail="Yellow Card",
            assist_name=None,
        )
        events = parse_events([item])

        assert len(events) == 1
        assert events[0].type == "Card"
        assert events[0].assist is None

    def test_extra_time_minute_is_elapsed_plus_extra(self):
        """Spec: 'Extra-time minute is elapsed + extra'.

        The parser must add `time.extra` to `time.elapsed` to get
        the canonical match minute (90 + 11 = 101).
        """
        item = make_event_dict(
            elapsed=90,
            team_name="Holland",
            player_name="W. Weghorst",
            event_type="Goal",
            detail="Normal Goal",
            extra=11,
            assist_name="T. Koopmeiners",
        )
        events = parse_events([item])

        assert len(events) == 1
        assert events[0].minute == 101

    def test_extra_time_minute_uses_zero_when_extra_is_null(self):
        """Triangulation: if `time.extra` is null, the parser must
        default to 0 (don't error, don't treat None as 0 silently
        with a wrong value). The minute is just `elapsed`.
        """
        item = make_event_dict(
            elapsed=35,
            team_name="Argentina",
            player_name="N. Molina",
            event_type="Goal",
            detail="Normal Goal",
            extra=None,
        )
        events = parse_events([item])

        assert events[0].minute == 35

    def test_unknown_event_type_is_skipped_not_crashed(self):
        """Spec: 'Unknown event type is skipped, not crashed'.

        A list with [Goal, Var] must produce [Goal] and must not
        raise — the live API emits "Var" entries that we ignore.
        """
        goal = make_event_dict(
            elapsed=35,
            team_name="Argentina",
            player_name="N. Molina",
            event_type="Goal",
        )
        var_event = make_event_dict(
            elapsed=36,
            team_name="Argentina",
            player_name="VAR Check",
            event_type="Var",
            detail="Goal confirmed",
        )
        events = parse_events([goal, var_event])

        assert len(events) == 1
        assert events[0].type == "Goal"
        assert events[0].player == "N. Molina"

    def test_events_preserve_input_order(self):
        """Triangulation: the parser returns events in the same order
        as the input list. Ordering matters for the live UI timeline.
        """
        first = make_event_dict(elapsed=15, team_name="Argentina", player_name="A", event_type="Goal")
        second = make_event_dict(elapsed=30, team_name="Holland", player_name="B", event_type="Card", detail="Yellow")
        third = make_event_dict(elapsed=45, team_name="Argentina", player_name="C", event_type="subst", detail="Sub")

        events = parse_events([first, second, third])

        assert [e.minute for e in events] == [15, 30, 45]
        assert [e.player for e in events] == ["A", "B", "C"]

    def test_all_three_event_types_are_accepted(self):
        """Triangulation: the parser must accept all three allowed
        MatchEvent types — Goal, Card, subst — without skipping any.
        """
        goal = make_event_dict(elapsed=10, team_name="Argentina", player_name="A", event_type="Goal")
        card = make_event_dict(elapsed=20, team_name="Argentina", player_name="B", event_type="Card", detail="Yellow")
        subst = make_event_dict(elapsed=30, team_name="Argentina", player_name="C", event_type="subst", detail="Sub")

        events = parse_events([goal, card, subst])

        assert [e.type for e in events] == ["Goal", "Card", "subst"]

    def test_empty_events_list_returns_empty_list(self):
        """Triangulation: the parser must accept an empty list and
        return an empty list — no exception, no sentinel value.
        """
        assert parse_events([]) == []


# ---------------------------------------------------------------------------
# Requirement: parse_statistics
# ---------------------------------------------------------------------------

class TestParseStatistics:
    def test_both_teams_present_returns_populated_tuple(self):
        """Spec: 'Both teams present returns populated tuple'.

        A 2-element list (home, away) with non-null values for
        'Ball Possession' and 'Total Shots' must produce two
        non-None TeamStats with the right values mapped.
        """
        items = [
            make_team_statistics(
                team_id=26,
                team_name="Argentina",
                possession="44%",
                shots_on_goal=2,
                total_shots=5,
            ),
            make_team_statistics(
                team_id=41,
                team_name="Holland",
                possession="56%",
                shots_on_goal=4,
                total_shots=8,
            ),
        ]
        home, away = parse_statistics(items)

        assert home is not None and away is not None
        assert isinstance(home, TeamStats) and isinstance(away, TeamStats)
        assert home.name == "Argentina"
        assert home.possession == "44%"
        assert home.total_shots == 5
        assert home.shots_on_goal == 2
        assert away.name == "Holland"
        assert away.possession == "56%"
        assert away.total_shots == 8
        assert away.shots_on_goal == 4

    def test_null_string_stat_value_defaults_to_empty_string(self):
        """Spec: 'Null string stat value defaults to empty string'.

        If 'Ball Possession' has value=None, the parsed
        TeamStats.possession MUST be "" (never None, never "None").
        """
        items = [
            make_team_statistics(
                team_id=26,
                team_name="Argentina",
                possession=None,
                shots_on_goal=2,
                total_shots=5,
            ),
        ]
        home, away = parse_statistics(items)

        assert home is not None
        assert home.possession == ""
        assert isinstance(home.possession, str)
        # The other string fields must also be safe when null.
        assert home.pass_accuracy == "87%"  # explicitly provided
        assert home.expected_goals == "1.78"  # explicitly provided

    def test_null_numeric_stat_value_defaults_to_zero(self):
        """Spec: 'Null numeric stat value defaults to zero'.

        If 'Shots on Goal' has value=None, the parsed
        TeamStats.shots_on_goal MUST be 0 (never None, never "").
        """
        items = [
            make_team_statistics(
                team_id=26,
                team_name="Argentina",
                possession="44%",
                shots_on_goal=None,
                total_shots=5,
            ),
        ]
        home, _ = parse_statistics(items)

        assert home is not None
        assert home.shots_on_goal == 0
        assert isinstance(home.shots_on_goal, int)
        # Other numeric fields with non-null values must pass through.
        assert home.total_shots == 5

    def test_empty_input_returns_none_none(self):
        """Spec: 'Empty input returns (None, None)'.

        `parse_statistics([])` MUST return `(None, None)` so the
        caller can `if home_stats is None` to detect a missing
        statistics response from the API.
        """
        assert parse_statistics([]) == (None, None)

    def test_home_is_first_away_is_second(self):
        """Triangulation: the spec's design decision is that the
        parser trusts input order — first entry is home, second is
        away. Pin the contract so a future reorder is caught.
        """
        items = [
            make_team_statistics(
                team_id=26,
                team_name="HomeTeam",
                possession="60%",
                shots_on_goal=3,
                total_shots=7,
            ),
            make_team_statistics(
                team_id=41,
                team_name="AwayTeam",
                possession="40%",
                shots_on_goal=1,
                total_shots=3,
            ),
        ]
        home, away = parse_statistics(items)

        assert home.name == "HomeTeam"
        assert away.name == "AwayTeam"
        assert home.possession == "60%"
        assert away.possession == "40%"

    def test_unknown_stat_types_are_silently_ignored(self):
        """Triangulation: extra stat types the parser doesn't know
        (e.g. a future API field) must not crash and must not
        surface in any TeamStats field.
        """
        items = [
            {
                "team": {"id": 26, "name": "Argentina", "logo": "url"},
                "statistics": [
                    make_stat_entry("Ball Possession", "44%"),
                    make_stat_entry("Shots on Goal", 2),
                    make_stat_entry("Total Shots", 5),
                    make_stat_entry("Corner Kicks", 3),
                    make_stat_entry("Fouls", 10),
                    make_stat_entry("Offsides", 2),
                    make_stat_entry("Yellow Cards", 2),
                    make_stat_entry("Red Cards", 0),
                    make_stat_entry("Passes Accurate", "87%"),
                    make_stat_entry("Expected Goals", "1.78"),
                    # Unknown stat types the parser must ignore.
                    make_stat_entry("Shots Outside Box", 1),
                    make_stat_entry("Brand New Metric 2099", "yes"),
                ],
            }
        ]
        home, _ = parse_statistics(items)

        assert home is not None
        # The known stats still come through correctly.
        assert home.possession == "44%"
        assert home.shots_on_goal == 2
        assert home.total_shots == 5
        # TeamStats exposes exactly the 10 known fields. The unknown
        # stat types must NOT have leaked in as extra attributes.
        allowed_fields = {
            "name", "possession", "shots_on_goal", "total_shots", "corners",
            "fouls", "offsides", "yellow_cards", "red_cards",
            "pass_accuracy", "expected_goals",
        }
        actual_fields = set(TeamStats.model_fields.keys())
        assert actual_fields == allowed_fields


# ---------------------------------------------------------------------------
# Requirement: parse_players
# ---------------------------------------------------------------------------

class TestParsePlayers:
    def test_players_parsed_per_team(self):
        """Spec: 'Players parsed per team'.

        A 2-element list (home, away) each containing 11 player
        entries must return `(11 players, 11 players)`.
        """
        home_players = [
            make_player_dict(f"HomePlayer{i+1}", position="F", rating="7.0", minutes=90)
            for i in range(11)
        ]
        away_players = [
            make_player_dict(f"AwayPlayer{i+1}", position="F", rating="7.0", minutes=90)
            for i in range(11)
        ]
        items = [
            make_team_players(team_id=26, team_name="Argentina", players=home_players),
            make_team_players(team_id=41, team_name="Holland", players=away_players),
        ]
        home, away = parse_players(items)

        assert len(home) == 11
        assert len(away) == 11
        assert all(isinstance(p, PlayerStats) for p in home)
        assert all(isinstance(p, PlayerStats) for p in away)

    def test_substitute_flag_is_preserved(self):
        """Spec: 'Substitute flag is preserved'.

        A player with `statistics[0].games.substitute == True` must
        come through as `PlayerStats.substitute is True` — the
        parser must read the flag, not default to False.
        """
        starter = make_player_dict("L. Messi", position="F", rating="8.2", minutes=90, substitute=False)
        sub = make_player_dict("L. Paredes", position="CM", rating="6.0", minutes=8, substitute=True)
        items = [
            make_team_players(team_id=26, team_name="Argentina", players=[starter, sub]),
        ]
        home, _ = parse_players(items)

        assert home[0].substitute is False
        assert home[1].substitute is True

    def test_first_team_is_home_second_is_away(self):
        """Triangulation: the parser returns `(home, away)` based
        on input order — first entry is home. Pin the contract.
        """
        items = [
            make_team_players(
                team_id=26,
                team_name="HomeTeam",
                players=[make_player_dict("HomeP1")],
            ),
            make_team_players(
                team_id=41,
                team_name="AwayTeam",
                players=[make_player_dict("AwayP1")],
            ),
        ]
        home, away = parse_players(items)

        assert home[0].name == "HomeP1"
        assert away[0].name == "AwayP1"

    def test_player_fields_are_extracted_from_nested_statistics(self):
        """Triangulation: the parser must read the FIRST statistics
        block (`statistics[0]`) and pull the 20 fields listed in
        the PlayerStats model. If any field is dropped or
        mistranslated, this test catches it.
        """
        player = make_player_dict(
            name="L. Messi",
            position="F",
            rating="8.2",
            minutes=90,
            substitute=False,
        )
        items = [make_team_players(team_id=26, team_name="Argentina", players=[player])]
        home, _ = parse_players(items)

        p = home[0]
        assert p.name == "L. Messi"
        assert p.position == "F"
        assert p.rating == "8.2"
        assert p.minutes == 90
        assert p.shots_total == 3
        assert p.shots_on == 2
        assert p.goals == 1
        assert p.assists == 1
        assert p.passes_total == 45
        assert p.key_passes == 4
        assert p.pass_accuracy == "87%"
        assert p.duels_won == 6
        assert p.duels_total == 9
        assert p.dribbles_success == 6
        assert p.dribbles_attempts == 9
        assert p.fouls_committed == 1
        assert p.fouls_drawn == 3
        assert p.yellow_cards == 1
        assert p.red_cards == 0

    def test_empty_player_lists_return_empty_tuples(self):
        """Triangulation: teams with no players produce empty lists,
        not `None` and not a crash. This protects callers that
        iterate over the returned lists.
        """
        items = [
            make_team_players(team_id=26, team_name="HomeTeam", players=[]),
            make_team_players(team_id=41, team_name="AwayTeam", players=[]),
        ]
        home, away = parse_players(items)

        assert home == []
        assert away == []


# ---------------------------------------------------------------------------
# Module-level sanity: the parsers must be importable as `parse_*` symbols.
# This guards against a rename that would silently break the public API.
# ---------------------------------------------------------------------------

class TestModuleSurface:
    def test_all_four_parsers_are_exported(self):
        import backend.parsers as parsers

        for name in ("parse_fixture", "parse_events", "parse_statistics", "parse_players"):
            assert hasattr(parsers, name), f"backend.parsers missing {name!r}"
            assert callable(getattr(parsers, name))
