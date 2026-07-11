# Delta for match-data-models

## ADDED Requirements

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

## MODIFIED Requirements

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
