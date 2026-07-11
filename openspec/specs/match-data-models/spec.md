# match-data-models Specification

## Purpose

Pydantic v2 models that represent every piece of match state the AI DT backend produces, consumes, and serializes. These models are the contract between the data source (mock or live) and the rest of the system (services in change 2, HTTP API in change 3).

## Requirements

### Requirement: FixtureStatus and TeamScore

The system MUST define `FixtureStatus` and `TeamScore` Pydantic v2 models. `FixtureStatus.short` MUST accept ANY non-empty string (the API-Football v3 spec defines 19 statuses: `TBD`, `NS`, `1H`, `HT`, `2H`, `ET`, `BT`, `P`, `SUSP`, `INT`, `FT`, `AET`, `PEN`, `PST`, `CANC`, `ABD`, `AWD`, `WO`, `LIVE`) — the model MUST NOT restrict `short` to a fixed `Literal` set. A `min_length=1` constraint is the only validation on `short`. Downstream code (match-state-manager, milestone-detector) owns the per-status interpretation.

| Model | Field | Type | Constraint |
|-------|-------|------|-----------|
| `FixtureStatus` | `elapsed` | `int` | `>= 0` (extra time allowed, e.g. 101) |
| `FixtureStatus` | `short` | `str` | `min_length=1` (no `Literal` restriction) |
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

#### Scenario: All 18 API statuses are accepted on short

- GIVEN `short` values from the full set `{TBD, NS, 1H, HT, 2H, ET, BT, P, SUSP, INT, FT, AET, PEN, PST, CANC, ABD, AWD, WO, LIVE}`
- WHEN `FixtureStatus(short=..., elapsed=0, long=...)` is instantiated for each
- THEN every instance is valid (no `ValidationError`)

#### Scenario: Not-started status NS is accepted

- GIVEN `{"elapsed": 0, "short": "NS", "long": "Not Started"}`
- WHEN `FixtureStatus(...)` is instantiated
- THEN the instance is valid and `status.short == "NS"`

#### Scenario: After-extra-time status AET is accepted

- GIVEN `{"elapsed": 120, "short": "AET", "long": "After Extra Time"}`
- WHEN `FixtureStatus(...)` is instantiated
- THEN the instance is valid and `status.short == "AET"`

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

The system MUST define `PlayerStats` and `TeamStats` Pydantic v2 models. EVERY field MUST have a default value so the models accept construction from parsers that emit partial or null-derived data: `int` fields default to `0`, `str` fields default to `""`, `bool` fields default to `False`. `possession`, `pass_accuracy`, `expected_goals`, and `rating` MUST remain `str` (not coerced to float). This guarantees a malformed or sparse player response from the live API never crashes the model layer — nulls become safe defaults at parse time.

`PlayerStats` fields: name, position, rating, minutes, goals, assists, shots_total, shots_on, passes_total, key_passes, pass_accuracy, duels_won, duels_total, dribbles_success, dribbles_attempts, fouls_committed, fouls_drawn, yellow_cards, red_cards, `substitute: bool`. `TeamStats` fields: name, possession, shots_on_goal, total_shots, corners, fouls, offsides, yellow_cards, red_cards, pass_accuracy, expected_goals.

#### Scenario: PlayerStats substitute defaults to False

- GIVEN a player dict without a `substitute` field
- WHEN `PlayerStats(...)` is instantiated
- THEN `substitute is False`

#### Scenario: TeamStats possession stays a string

- GIVEN `{"name": "Argentina", "possession": "44%", "pass_accuracy": "87%", "expected_goals": "1.78"}`
- WHEN `TeamStats(...)` is instantiated
- THEN `possession == "44%"` (string preserved)

#### Scenario: PlayerStats with all default values is valid

- GIVEN an empty dict `{}` (or one with only `name="Paredes"`)
- WHEN `PlayerStats(...)` is instantiated
- THEN the instance is valid
- AND every numeric field equals `0`
- AND every string field equals `""`
- AND `substitute is False`

#### Scenario: TeamStats with all default values is valid

- GIVEN an empty dict `{}` (or one with only `name="Argentina"`)
- WHEN `TeamStats(...)` is instantiated
- THEN the instance is valid
- AND every numeric field equals `0`
- AND every string field equals `""`

### Requirement: Lineup Models

The system MUST define `LineupPlayer` and `LineupTeam` Pydantic v2 models. `LineupPlayer` represents a single player in a lineup (starter or substitute). `LineupTeam` represents one team's full lineup: formation, starting XI, substitutes, and coach. Every field MUST have a default value (`int` → `0`, `str` → `""`, `list` → `[]`, `None`-able → `None`) so the models accept construction from parsers that emit partial data without raising.

| Model | Field | Type | Constraint |
|-------|-------|------|-----------|
| `LineupPlayer` | `player_id` | `int` | `>= 0` (0 = unknown) |
| `LineupPlayer` | `name` | `str` | non-empty |
| `LineupPlayer` | `number` | `int` | `>= 0` |
| `LineupPlayer` | `pos` | `str` | non-empty (e.g. "GK", "DF") |
| `LineupPlayer` | `grid` | `str \| None` | `None` when not provided |
| `LineupTeam` | `team_id` | `int` | `> 0` |
| `LineupTeam` | `team_name` | `str` | non-empty |
| `LineupTeam` | `formation` | `str` | non-empty (e.g. "4-3-3") |
| `LineupTeam` | `startXI` | `list[LineupPlayer]` | defaults to `[]` |
| `LineupTeam` | `substitutes` | `list[LineupPlayer]` | defaults to `[]` |
| `LineupTeam` | `coach_name` | `str \| None` | `None` when not provided |

#### Scenario: LineupPlayer with grid null defaults to None

- GIVEN `{"player_id": 1, "name": "Dibu", "number": 23, "pos": "GK", "grid": null}`
- WHEN `LineupPlayer(...)` is instantiated
- THEN `grid is None` (no `ValidationError`)

#### Scenario: LineupPlayer with grid string preserved

- GIVEN `{"player_id": 1, "name": "Dibu", "number": 23, "pos": "GK", "grid": "1:1"}`
- WHEN `LineupPlayer(...)` is instantiated
- THEN `grid == "1:1"`

#### Scenario: LineupTeam with missing coach defaults to None

- GIVEN a lineup dict without a `coach` field
- WHEN `LineupTeam(...)` is instantiated
- THEN `coach_name is None` (tolerated, no `ValidationError`)

#### Scenario: LineupTeam with empty startXI and substitutes is valid

- GIVEN `{"team_id": 26, "team_name": "Argentina", "formation": "4-3-3"}` (no XI/subs)
- WHEN `LineupTeam(...)` is instantiated
- THEN `startXI == []` AND `substitutes == []` AND the instance is valid

### Requirement: MatchState and Prediction

The system MUST define `MatchState` with `fixture_id: int`, `status: FixtureStatus`, `home: TeamScore`, `away: TeamScore`, `events: list[MatchEvent]`, `home_stats: TeamStats | None`, `away_stats: TeamStats | None`, `home_players: list[PlayerStats]`, `away_players: list[PlayerStats]`, `home_lineup: LineupTeam | None = None`, `away_lineup: LineupTeam | None = None`, `last_updated: datetime`. The `home_lineup` and `away_lineup` fields MUST default to `None` so a pre-lineup `MatchState` (constructed without lineups) is valid. The system MUST also define `Prediction` with `momento: int` (constrained `1..=6`), `timestamp: datetime`, `content: str`.
(Previously: MatchState had 10 fields and no lineup fields; now adds home_lineup and away_lineup, both optional and defaulting to None)

#### Scenario: MatchState at minute 0 has no stats, events, or lineups

- GIVEN a freshly parsed pre-kickoff fixture
- WHEN `MatchState` is constructed with empty lists, `None` stats, and no lineup fields
- THEN the instance is valid, `last_updated` is a `datetime`
- AND `home_lineup is None` AND `away_lineup is None`

#### Scenario: MatchState with populated lineups round-trips

- GIVEN a `MatchState` with `home_lineup=LineupTeam(formation="4-3-3", ...)` and `away_lineup=LineupTeam(formation="3-4-1-2", ...)`
- WHEN the state is serialized and re-parsed
- THEN `home_lineup.formation == "4-3-3"` AND `away_lineup.formation == "3-4-1-2"`

#### Scenario: Prediction momento is bounded 1-6

- GIVEN `{"momento": 7, "timestamp": now, "content": "x"}`
- WHEN `Prediction(...)` is instantiated
- THEN a `ValidationError` is raised
