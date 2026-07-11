# Delta for match-data-models

## MODIFIED Requirements

### Requirement: FixtureStatus and TeamScore

The system MUST define `FixtureStatus` and `TeamScore` Pydantic v2 models. `FixtureStatus.short` MUST accept ANY non-empty string (the API-Football v3 spec defines 18 statuses: `TBD`, `NS`, `1H`, `HT`, `2H`, `ET`, `BT`, `P`, `SUSP`, `INT`, `FT`, `AET`, `PEN`, `PST`, `CANC`, `ABD`, `AWD`, `WO`, `LIVE`) — the model MUST NOT restrict `short` to a fixed `Literal` set. A `min_length=1` constraint is the only validation on `short`. Downstream code (match-state-manager, milestone-detector) owns the per-status interpretation.

| Model | Field | Type | Constraint |
|-------|-------|------|-----------|
| `FixtureStatus` | `elapsed` | `int` | `>= 0` (extra time allowed, e.g. 101) |
| `FixtureStatus` | `short` | `str` | `min_length=1` (no `Literal` restriction) |
| `FixtureStatus` | `long` | `str` | non-empty |
| `TeamScore` | `id` | `int` | `> 0` |
| `TeamScore` | `name` | `str` | non-empty |
| `TeamScore` | `goals` | `int` | `>= 0` |

(Previously: `short` was restricted to `Literal["1H","HT","2H","FT"]` — too narrow, crashed on live API responses for extra-time / penalty / not-started statuses.)

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

### Requirement: PlayerStats and TeamStats

The system MUST define `PlayerStats` and `TeamStats` Pydantic v2 models. EVERY field MUST have a default value so the models accept construction from parsers that emit partial or null-derived data: `int` fields default to `0`, `str` fields default to `""`, `bool` fields default to `False`. `possession`, `pass_accuracy`, `expected_goals`, and `rating` MUST remain `str` (not coerced to float). This guarantees a malformed or sparse player response from the live API never crashes the model layer — nulls become safe defaults at parse time.

(Previously: required fields without defaults; null-derived values from the parser raised `ValidationError`.)

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
