"""Pure-function parsers that convert raw API-Football v3 response dicts
into the Pydantic models from `backend.models`.

These four functions are the SINGLE seam that knows the API-Football
schema. Both `MockDataSource` and `LiveDataSource` call them, which is
how the "mock and live share parsing" invariant is enforced
structurally — there is no other place in the codebase that touches
the v3 envelope.

Spec: openspec/changes/backend-foundation/specs/api-football-parsing/spec.md
"""
from datetime import datetime, timezone

from backend.models import (
    FixtureStatus,
    MatchEvent,
    MatchState,
    PlayerStats,
    TeamScore,
    TeamStats,
)

# Map API-Football stat-type strings to the corresponding `TeamStats`
# field name. The boolean flag marks numeric vs string fields so the
# parser can apply the right null-defaulting rule.
STAT_TYPE_MAP: dict[str, tuple[str, bool]] = {
    "Ball Possession": ("possession", False),
    "Shots on Goal": ("shots_on_goal", True),
    "Total Shots": ("total_shots", True),
    "Corner Kicks": ("corners", True),
    "Fouls": ("fouls", True),
    "Offsides": ("offsides", True),
    "Yellow Cards": ("yellow_cards", True),
    "Red Cards": ("red_cards", True),
    "Passes Accurate": ("pass_accuracy", False),
    "Expected Goals": ("expected_goals", False),
}

# Event types we model in `MatchEvent`. Anything else is silently
# skipped — the live API emits "Var" and other types we don't surface
# to the UI, and we MUST NOT crash on them.
_KNOWN_EVENT_TYPES = frozenset({"Goal", "Card", "subst"})


def _safe_str(value) -> str:
    """Coerce a possibly-null value to a string, defaulting to "".

    Numeric and string stats that the API returns as null become "".
    """
    return value if isinstance(value, str) else ""


def _safe_int(value) -> int:
    """Coerce a possibly-null value to an int, defaulting to 0.

    Numeric stats that the API returns as null become 0. Strings are
    intentionally NOT parsed — the API sends ints for these fields,
    and a string here is a contract violation, not a coercion target.
    """
    return value if isinstance(value, int) else 0


def parse_fixture(raw: dict) -> MatchState:
    """Convert a single `/fixtures` response element into a `MatchState`.

    The returned `MatchState` has empty events, no stats, no players,
    and `last_updated` set to the current UTC time. Stats and events
    are populated separately by `parse_statistics` / `parse_events`
    and merged by the data-source layer.
    """
    fixture_block = raw["fixture"]
    teams_block = raw["teams"]
    goals_block = raw["goals"]

    status = FixtureStatus(
        elapsed=fixture_block["status"]["elapsed"],
        short=fixture_block["status"]["short"],
        long=fixture_block["status"]["long"],
    )
    home = TeamScore(
        id=teams_block["home"]["id"],
        name=teams_block["home"]["name"],
        goals=goals_block["home"] or 0,
    )
    away = TeamScore(
        id=teams_block["away"]["id"],
        name=teams_block["away"]["name"],
        goals=goals_block["away"] or 0,
    )
    return MatchState(
        fixture_id=fixture_block["id"],
        status=status,
        home=home,
        away=away,
        events=[],
        home_stats=None,
        away_stats=None,
        home_players=[],
        away_players=[],
        last_updated=datetime.now(tz=timezone.utc),
    )


def parse_events(items: list[dict]) -> list[MatchEvent]:
    """Convert a `/fixtures/events` response array into `MatchEvent`s.

    Events are returned in input order. Unknown event types
    (e.g. "Var") are silently skipped — the parser does not raise.
    The match minute is `time.elapsed + (time.extra or 0)`.
    """
    events: list[MatchEvent] = []
    for item in items:
        event_type = item["type"]
        if event_type not in _KNOWN_EVENT_TYPES:
            continue

        time_block = item["time"]
        minute = time_block["elapsed"] + (time_block.get("extra") or 0)

        assist_block = item.get("assist")
        assist_name = assist_block["name"] if assist_block else None

        events.append(
            MatchEvent(
                minute=minute,
                team=item["team"]["name"],
                player=item["player"]["name"],
                type=event_type,
                detail=item["detail"],
                assist=assist_name,
            )
        )
    return events


def parse_statistics(
    items: list[dict],
) -> tuple[TeamStats | None, TeamStats | None]:
    """Convert a `/fixtures/statistics` response array into a team tuple.

    Returns `(home_stats, away_stats)`. The first element in `items`
    is treated as home, the second as away. Returns `(None, None)`
    for an empty input. Unknown stat types are silently ignored;
    null values default to `""` for string fields and `0` for numeric
    fields.
    """
    if not items:
        return (None, None)

    parsed: list[TeamStats] = []
    for team_block in items:
        stats_kwargs: dict = {"name": team_block["team"]["name"]}
        for stat in team_block.get("statistics", []):
            mapping = STAT_TYPE_MAP.get(stat["type"])
            if mapping is None:
                continue
            field_name, is_numeric = mapping
            stats_kwargs[field_name] = (
                _safe_int(stat["value"]) if is_numeric else _safe_str(stat["value"])
            )
        parsed.append(TeamStats(**stats_kwargs))

    # Trust input order: [0] is home, [1] is away. If the API ever
    # returns only one team, the other side is None so the caller
    # can detect the partial response.
    home_stats = parsed[0] if len(parsed) >= 1 else None
    away_stats = parsed[1] if len(parsed) >= 2 else None
    return (home_stats, away_stats)


def parse_players(
    items: list[dict],
) -> tuple[list[PlayerStats], list[PlayerStats]]:
    """Convert a `/fixtures/players` response array into a team tuple.

    Returns `(home_players, away_players)`. The first element in
    `items` is treated as home, the second as away. The parser
    reads `statistics[0]` of each player entry — the v3 envelope
    wraps the stats in a one-element list.
    """
    parsed: list[list[PlayerStats]] = []
    for team_block in items:
        players: list[PlayerStats] = []
        for player_block in team_block.get("players", []):
            stats = player_block["statistics"][0]
            games = stats["games"]
            shots = stats["shots"]
            goals = stats["goals"]
            passes = stats["passes"]
            duels = stats["duels"]
            dribbles = stats["dribbles"]
            fouls = stats["fouls"]
            players.append(
                PlayerStats(
                    name=player_block["player"]["name"],
                    position=games["position"],
                    rating=games["rating"],
                    minutes=games["minutes"],
                    goals=goals["total"],
                    assists=goals["assists"],
                    shots_total=shots["total"],
                    shots_on=shots["on"],
                    passes_total=passes["total"],
                    key_passes=passes["key"],
                    pass_accuracy=passes["accuracy"],
                    duels_won=duels["won"],
                    duels_total=duels["total"],
                    dribbles_success=dribbles["success"],
                    dribbles_attempts=dribbles["attempts"],
                    fouls_committed=fouls["committed"],
                    fouls_drawn=fouls["drawn"],
                    yellow_cards=stats["cards"]["yellow"],
                    red_cards=stats["cards"]["red"],
                    substitute=games["substitute"],
                )
            )
        parsed.append(players)

    home_players = parsed[0] if len(parsed) >= 1 else []
    away_players = parsed[1] if len(parsed) >= 2 else []
    return (home_players, away_players)
