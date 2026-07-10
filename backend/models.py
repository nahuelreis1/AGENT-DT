"""Pydantic v2 models for AI DT backend match data.

Contract between data sources (mock or live) and downstream services.
Spec: openspec/changes/backend-foundation/specs/match-data-models/spec.md
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FixtureStatus(BaseModel):
    """Compact representation of a fixture's live status.

    `short` is a plain `str` (not a `Literal`) because the live
    API-Football v3 endpoint emits 18 distinct statuses (TBD, NS,
    1H, HT, 2H, ET, BT, P, SUSP, INT, FT, AET, PEN, PST, CANC,
    ABD, AWD, WO, LIVE). Constraining to a Literal would crash on
    the first live call. Downstream services interpret each value
    (e.g. `services.match_state.PERIOD_NAMES`).
    """

    elapsed: int = Field(ge=0, description="Minutes elapsed; extra time allowed (e.g. 101)")
    short: str = Field(min_length=1, description="API-Football v3 status code (18 values)")
    long: str = Field(min_length=1, description="Human-readable status label")


class TeamScore(BaseModel):
    """Team identity + current goal count."""

    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    goals: int = Field(ge=0)


class MatchEvent(BaseModel):
    """A single match event (goal, card, substitution)."""

    minute: int = Field(ge=0)
    team: str = Field(min_length=1)
    player: str = Field(min_length=1)
    type: Literal["Goal", "Card", "subst"]
    detail: str = Field(min_length=1)
    assist: str | None = None


class PlayerStats(BaseModel):
    """Per-player statistics from the API-Football v3 envelope.

    `rating` and `pass_accuracy` are intentionally kept as strings to mirror
    the upstream representation and avoid precision loss. All fields
    except `name` and `position` have defaults because the live API
    sends `null` for substitutes (no minutes played, no rating yet).
    """

    name: str
    position: str
    rating: str = ""
    minutes: int = 0
    goals: int = 0
    assists: int = 0
    shots_total: int = 0
    shots_on: int = 0
    passes_total: int = 0
    key_passes: int = 0
    pass_accuracy: str = ""
    duels_won: int = 0
    duels_total: int = 0
    dribbles_success: int = 0
    dribbles_attempts: int = 0
    fouls_committed: int = 0
    fouls_drawn: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    substitute: bool = False


class TeamStats(BaseModel):
    """Per-team aggregate statistics.

    `possession`, `pass_accuracy`, and `expected_goals` stay as strings —
    they carry units ("44%", "87%") or upstream-decimal precision ("1.78").
    All fields except `name` have defaults because the live API may
    send partial responses (e.g. the xG line only appears with the
    `half=true` query parameter, on 2024+ fixtures).
    """

    name: str
    possession: str = ""
    shots_on_goal: int = 0
    total_shots: int = 0
    corners: int = 0
    fouls: int = 0
    offsides: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    pass_accuracy: str = ""
    expected_goals: str = ""


class MatchState(BaseModel):
    """Complete snapshot of a fixture at a given moment.

    Pre-kickoff fixtures have empty events/players and `None` stats.
    """

    fixture_id: int
    status: FixtureStatus
    home: TeamScore
    away: TeamScore
    events: list[MatchEvent] = []
    home_stats: TeamStats | None = None
    away_stats: TeamStats | None = None
    home_players: list[PlayerStats] = []
    away_players: list[PlayerStats] = []
    last_updated: datetime


class Prediction(BaseModel):
    """A timestamped momento-tagged prediction.

    `momento` maps to the 6 file keys (15, 30, ht, 60, 75, ft) in change 2.
    """

    momento: int = Field(ge=1, le=6)
    timestamp: datetime
    content: str
