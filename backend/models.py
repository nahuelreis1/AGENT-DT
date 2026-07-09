"""Pydantic v2 models for AI DT backend match data.

Contract between data sources (mock or live) and downstream services.
Spec: openspec/changes/backend-foundation/specs/match-data-models/spec.md
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FixtureStatus(BaseModel):
    """Compact representation of a fixture's live status."""

    elapsed: int = Field(ge=0, description="Minutes elapsed; extra time allowed (e.g. 101)")
    short: Literal["1H", "HT", "2H", "FT"]
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
    the upstream representation and avoid precision loss.
    """

    name: str
    position: str
    rating: str
    minutes: int
    goals: int
    assists: int
    shots_total: int
    shots_on: int
    passes_total: int
    key_passes: int
    pass_accuracy: str
    duels_won: int
    duels_total: int
    dribbles_success: int
    dribbles_attempts: int
    fouls_committed: int
    fouls_drawn: int
    yellow_cards: int
    red_cards: int
    substitute: bool = False


class TeamStats(BaseModel):
    """Per-team aggregate statistics.

    `possession`, `pass_accuracy`, and `expected_goals` stay as strings —
    they carry units ("44%", "87%") or upstream-decimal precision ("1.78").
    """

    name: str
    possession: str
    shots_on_goal: int
    total_shots: int
    corners: int
    fouls: int
    offsides: int
    yellow_cards: int
    red_cards: int
    pass_accuracy: str
    expected_goals: str


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
