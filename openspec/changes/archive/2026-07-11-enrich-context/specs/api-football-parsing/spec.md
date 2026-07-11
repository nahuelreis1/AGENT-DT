# Delta for api-football-parsing

## ADDED Requirements

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
