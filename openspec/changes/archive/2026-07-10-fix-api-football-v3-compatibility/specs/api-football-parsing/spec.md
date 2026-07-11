# Delta for api-football-parsing

## MODIFIED Requirements

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

(Previously: `STAT_TYPE_MAP` used `"Passes Accurate"` and `"Expected Goals"` (Title Case) which never matched the live API's lowercase keys — the parser silently dropped `pass_accuracy` and `expected_goals`.)

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

(Previously: only some fields were null-safe; null `goals.total` or null `rating` raised during construction.)

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
