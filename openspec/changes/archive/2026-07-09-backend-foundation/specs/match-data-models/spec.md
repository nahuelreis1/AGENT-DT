# match-data-models Specification

## Purpose

Pydantic v2 models that represent every piece of match state the AI DT backend produces, consumes, and serializes. These models are the contract between the data source (mock or live) and the rest of the system (services in change 2, HTTP API in change 3).

## Requirements

### Requirement: FixtureStatus and TeamScore

The system MUST define `FixtureStatus` and `TeamScore` Pydantic v2 models.

| Model | Field | Type | Constraint |
|-------|-------|------|-----------|
| `FixtureStatus` | `elapsed` | `int` | `>= 0` (extra time allowed, e.g. 101) |
| `FixtureStatus` | `short` | `str` | one of `"1H"`, `"HT"`, `"2H"`, `"FT"` |
| `FixtureStatus` | `long` | `str` | non-empty |
| `TeamScore` | `id` | `int` | `> 0` |
| `TeamScore` | `name` | `str` | non-empty |
| `TeamScore` | `goals` | `int` | `>= 0` |

#### Scenario: Valid fixture status and team score round-trip

- GIVEN `{"elapsed": 67, "short": "2H", "long": "Second Half"}` and `{"id": 26, "name": "Argentina", "goals": 2}`
- WHEN both models are instantiated
- THEN both succeed and the values round-trip exactly

#### Scenario: Empty status short is rejected

- GIVEN `{"elapsed": 0, "short": "", "long": "Not Started"}`
- WHEN `FixtureStatus(...)` is instantiated
- THEN a `ValidationError` is raised

### Requirement: MatchEvent

The system MUST define `MatchEvent` with: `minute: int` (`>= 0`), `team: str` (non-empty), `player: str` (non-empty), `type: str` (one of `"Goal" | "Card" | "subst"`), `detail: str` (non-empty), `assist: str | None`.

#### Scenario: Goal event with assist is valid

- GIVEN `{"minute": 35, "team": "Argentina", "player": "Molina", "type": "Goal", "detail": "Normal Goal", "assist": "Messi"}`
- WHEN `MatchEvent(...)` is instantiated
- THEN the event is valid and `assist == "Messi"`

#### Scenario: Card event with null assist

- GIVEN an event dict with `type == "Card"` and `assist: None`
- WHEN `MatchEvent(...)` is instantiated
- THEN the event is valid and `assist is None`

#### Scenario: Unknown event type is rejected

- GIVEN an event with `type: "PenaltySaved"`
- WHEN `MatchEvent(...)` is instantiated
- THEN a `ValidationError` is raised

### Requirement: PlayerStats and TeamStats

The system MUST define `PlayerStats` (name, position, rating, minutes, goals, assists, shots_total, shots_on, passes_total, key_passes, pass_accuracy, duels_won, duels_total, dribbles_success, dribbles_attempts, fouls_committed, fouls_drawn, yellow_cards, red_cards, `substitute: bool`) and `TeamStats` (name, possession, shots_on_goal, total_shots, corners, fouls, offsides, yellow_cards, red_cards, pass_accuracy, expected_goals). `possession`, `pass_accuracy`, `expected_goals`, and `rating` MUST be `str` (not coerced to float).

#### Scenario: PlayerStats substitute defaults to False

- GIVEN a player dict without a `substitute` field
- WHEN `PlayerStats(...)` is instantiated
- THEN `substitute is False`

#### Scenario: TeamStats possession stays a string

- GIVEN `{"name": "Argentina", "possession": "44%", "pass_accuracy": "87%", "expected_goals": "1.78"}`
- WHEN `TeamStats(...)` is instantiated
- THEN `possession == "44%"` (string preserved)

### Requirement: MatchState and Prediction

The system MUST define `MatchState` with `fixture_id: int`, `status: FixtureStatus`, `home: TeamScore`, `away: TeamScore`, `events: list[MatchEvent]`, `home_stats: TeamStats | None`, `away_stats: TeamStats | None`, `home_players: list[PlayerStats]`, `away_players: list[PlayerStats]`, `last_updated: datetime`. The system MUST also define `Prediction` with `momento: int` (constrained `1..=6`), `timestamp: datetime`, `content: str`.

#### Scenario: MatchState at minute 0 has no stats or events

- GIVEN a freshly parsed pre-kickoff fixture
- WHEN `MatchState` is constructed with empty lists and `None` stats
- THEN the instance is valid and `last_updated` is a `datetime`

#### Scenario: Prediction momento is bounded 1-6

- GIVEN `{"momento": 7, "timestamp": now, "content": "x"}`
- WHEN `Prediction(...)` is instantiated
- THEN a `ValidationError` is raised
