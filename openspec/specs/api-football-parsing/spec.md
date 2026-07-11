# api-football-parsing Specification

## Purpose

Pure-function parsers that convert raw API-Football v3 response dicts (elements inside `response` arrays, not the envelope) into the Pydantic models from `match-data-models`. These five functions are the SINGLE seam that knows the API-Football schema — both `MockDataSource` and `LiveDataSource` call them, enforcing "mock and live share parsing" structurally.

## Requirements

### Requirement: parse_fixture

The system MUST expose `parse_fixture(raw: dict) -> MatchState` consuming a single element of the `/fixtures` `response` array. It MUST extract fixture id, status, and both team scores, and return a `MatchState` with `events == []`, `home_stats is None`, `away_stats is None`, and `last_updated` set to the current UTC time.

#### Scenario: Pre-kickoff fixture with no events

- GIVEN a fixture dict with `status.elapsed == 0`, `goals.home == 0`, `goals.away == 0`
- WHEN `parse_fixture(raw)` is called
- THEN it returns a `MatchState` with `events == []`, `home_stats is None`, `away_stats is None`

#### Scenario: Extra-time elapsed is preserved

- GIVEN a fixture dict with `status.elapsed == 101` and `status.short == "FT"`
- WHEN `parse_fixture(raw)` is called
- THEN `status.elapsed == 101` (no clamping to 90)

#### Scenario: Score 2-2 at full time

- GIVEN a fixture dict with `goals.home == 2`, `goals.away == 2`
- WHEN `parse_fixture(raw)` is called
- THEN `home.goals == 2` and `away.goals == 2`

### Requirement: parse_events

The system MUST expose `parse_events(items: list[dict]) -> list[MatchEvent]` consuming the `/fixtures/events` response array and returning events in input order. `minute` MUST be `time.elapsed + (time.extra or 0)`. Events with a type not in the `MatchEvent` allowed set (`"Goal"`, `"Card"`, `"subst"`) MUST be silently skipped — the parser MUST NOT raise an exception. This ensures live API-Football data with event types like `"Var"` does not crash the system.

#### Scenario: Goal event with assist

- GIVEN an event with `time.elapsed=35`, `team.name="Argentina"`, `player.name="Molina"`, `assist.name="Messi"`, `type="Goal"`
- WHEN `parse_events([item])` is called
- THEN the result is `[MatchEvent(minute=35, player="Molina", assist="Messi")]`

#### Scenario: Event with null assist

- GIVEN an event with `assist: None`
- WHEN `parse_events([item])` is called
- THEN the resulting `MatchEvent.assist is None`

#### Scenario: Extra-time minute is elapsed + extra

- GIVEN an event with `time.elapsed == 90` and `time.extra == 11`
- WHEN `parse_events([item])` is called
- THEN the resulting `MatchEvent.minute == 101`

#### Scenario: Unknown event type is skipped, not crashed

- GIVEN an events list with one "Goal" event and one "Var" event
- WHEN parse_events(items) is called
- THEN the result contains only the Goal event (the Var event is silently skipped)
- AND no exception is raised

### Requirement: parse_statistics

The system MUST expose `parse_statistics(items: list[dict]) -> tuple[TeamStats | None, TeamStats | None]` consuming the `/fixtures/statistics` response array (one entry per team) and returning `(home_stats, away_stats)`. It MUST map API-Football stat types to model fields per the table below; any unknown stat type MUST be ignored. String fields (`possession`, `pass_accuracy`, `expected_goals`) with null values MUST default to empty string. Numeric fields (`shots_on_goal`, `total_shots`, `corners`, `fouls`, `offsides`, `yellow_cards`, `red_cards`) with null values MUST default to `0`. The `STAT_TYPE_MAP` keys MUST match the exact API-Football v3 spellings (lowercase, no Title Case).

| API-Football `type` | Model field |
|---------------------|-------------|
| "Ball Possession" | `possession` (string) |
| "Shots on Goal" | `shots_on_goal` (numeric) |
| "Total Shots" | `total_shots` (numeric) |
| "Corner Kicks" | `corners` (numeric) |
| "Fouls" | `fouls` (numeric) |
| "Offsides" | `offsides` (numeric) |
| "Yellow Cards" | `yellow_cards` (numeric) |
| "Red Cards" | `red_cards` (numeric) |
| "Passes accurate" | `pass_accuracy` (string) |
| "expected_goals" | `expected_goals` (string) |

#### Scenario: Both teams present returns populated tuple

- GIVEN a 2-element list with "Ball Possession" = "44%" / "56%" and "Total Shots" = 5 / 8
- WHEN `parse_statistics(items)` is called
- THEN the result is two non-None `TeamStats` with possession and shots correctly mapped

#### Scenario: Null string stat value defaults to empty string

- GIVEN a stat entry with type "Ball Possession" and `value: None`
- WHEN the entry is parsed
- THEN the corresponding string field (`possession`) is `""` (empty string, never `None`)

#### Scenario: Null numeric stat value defaults to zero

- GIVEN a stat entry with type "Shots on Goal" and value: None
- WHEN the entry is parsed
- THEN the corresponding numeric field (shots_on_goal) is 0 (not None, not empty string)

#### Scenario: Empty input returns (None, None)

- GIVEN `parse_statistics([])`
- WHEN called
- THEN it returns `(None, None)`

#### Scenario: Parser correctly maps "Passes accurate" to pass_accuracy

- GIVEN a stat entry with `type: "Passes accurate"` and `value: "312 (87%)"`
- WHEN the entry is parsed
- THEN the corresponding `pass_accuracy` field equals `"312 (87%)"` (NOT the empty string, NOT silently dropped)

#### Scenario: Parser correctly maps "expected_goals" to expected_goals

- GIVEN a stat entry with `type: "expected_goals"` and `value: "1.78"`
- WHEN the entry is parsed
- THEN the corresponding `expected_goals` field equals `"1.78"` (NOT the empty string, NOT silently dropped)

#### Scenario: Unknown stat type is silently ignored

- GIVEN a stat entry with `type: "Some New Statistic"` not in the map
- WHEN the entry is parsed
- THEN the entry is dropped and no error is raised

### Requirement: parse_players

The system MUST expose `parse_players(items: list[dict]) -> tuple[list[PlayerStats], list[PlayerStats]]` consuming the `/fixtures/players` response array (one entry per team) and returning `(home_players, away_players)`. The first element MUST map to home, the second to away. EVERY field MUST be extracted through the project's null-safety helpers (`_safe_int` for numeric, `_safe_str` for string) so a player entry with null `goals.total`, null `assists`, null `duels`, null `rating`, or any other missing field becomes the model's default (`0` or `""`) — the parser MUST NOT raise on any null field.

#### Scenario: Players parsed per team

- GIVEN a 2-element players list (home + away), each with 11 player entries
- WHEN `parse_players(items)` is called
- THEN it returns `(11 players, 11 players)`

#### Scenario: Substitute flag is preserved

- GIVEN a player dict with `statistics[0].games.substitute == True`
- WHEN `parse_players([...])` is called
- THEN the corresponding `PlayerStats.substitute is True`

#### Scenario: Player with all null stats parses to defaults

- GIVEN a player entry with `goals.total: null`, `goals.assists: null`, `duels.total: null`, `games.rating: null`
- WHEN `parse_players([...])` is called
- THEN the returned `PlayerStats` is valid (no exception raised)
- AND `goals == 0`, `assists == 0`, `duels_total == 0`, `rating == ""`
- AND all other numeric fields equal `0` and all other string fields equal `""`

### Requirement: parse_lineups

The system MUST expose `parse_lineups(items: list[dict]) -> tuple[LineupTeam | None, LineupTeam | None]` consuming the `/fixtures/lineups` response array (one entry per team) and returning `(home_lineup, away_lineup)`. It MUST trust the input order: the first element maps to home, the second to away (same pattern as `parse_statistics`). The parser MUST map API-Football lineup fields to `LineupTeam` / `LineupPlayer` model fields per the table below. The `coach` field MUST be optional — a missing `coach` key MUST produce `coach_name = None` rather than raising. Player `grid` MUST be passed through as a string or `None`. Empty input (`[]`) MUST return `(None, None)`.

| API-Football field | Model field |
|--------------------|-------------|
| `team.id` | `LineupTeam.team_id` |
| `team.name` | `LineupTeam.team_name` |
| `formation` | `LineupTeam.formation` |
| `startXI` (array of `{player.id, player.name, number, pos, grid}`) | `LineupTeam.startXI` (list of `LineupPlayer`) |
| `substitutes` (same shape) | `LineupTeam.substitutes` |
| `coach.name` (optional) | `LineupTeam.coach_name` |

Every field MUST be extracted through the project's null-safety helpers (`_safe_int`, `_safe_str`) so a lineup entry with null `grid`, null `number`, or a missing `coach` becomes the model's default — the parser MUST NOT raise on any null field.

#### Scenario: Both teams present returns populated tuple

- GIVEN a 2-element list with `formation: "4-3-3"` / `"3-4-1-2"` and 11 starters each
- WHEN `parse_lineups(items)` is called
- THEN the result is two non-None `LineupTeam` with formations `"4-3-3"` and `"3-4-1-2"`
- AND `startXI` has 11 `LineupPlayer` entries each

#### Scenario: Empty input returns (None, None)

- GIVEN `parse_lineups([])`
- WHEN called
- THEN it returns `(None, None)`

#### Scenario: Missing coach field produces None

- GIVEN a lineup entry with no `coach` key
- WHEN `parse_lineups([item])` is called
- THEN the resulting `LineupTeam.coach_name is None` (no exception raised)

#### Scenario: Null grid defaults to None

- GIVEN a starter entry with `grid: null`
- WHEN `parse_lineups([item])` is called
- THEN the corresponding `LineupPlayer.grid is None`

#### Scenario: Single-element input returns (team, None)

- GIVEN a 1-element list (only home lineup present)
- WHEN `parse_lineups(items)` is called
- THEN the result is `(LineupTeam, None)`

#### Scenario: Trusts input order home then away

- GIVEN a 2-element list where the first has `team.name == "Argentina"` and the second `team.name == "Netherlands"`
- WHEN `parse_lineups(items)` is called
- THEN the first tuple element is Argentina (home) and the second is Netherlands (away)
