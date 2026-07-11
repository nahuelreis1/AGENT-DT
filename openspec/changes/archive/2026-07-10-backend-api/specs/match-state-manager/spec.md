# Delta for match-state-manager

## ADDED Requirements

### Requirement: MOMENTO_STATUSES Constant

`MOMENTO_STATUSES` MUST be a `dict[int, FixtureStatus]` mapping momento keys `1..6` to the corresponding fixture statuses:

| Momento | elapsed | short | long |
|---------|---------|-------|------|
| 1 | 15 | `1H` | `First Half` |
| 2 | 30 | `1H` | `First Half` |
| 3 | 45 | `HT` | `Halftime` |
| 4 | 60 | `2H` | `Second Half` |
| 5 | 75 | `2H` | `Second Half` |
| 6 | 120 | `PEN` | `Match Finished After Penalty` |

#### Scenario: Momento 1 maps to first half at 15 minutes

- GIVEN the `MOMENTO_STATUSES` constant
- WHEN `MOMENTO_STATUSES[1]` is accessed
- THEN `elapsed == 15` and `short == "1H"`

#### Scenario: Momento 6 maps to match finished at 120 minutes

- GIVEN the `MOMENTO_STATUSES` constant
- WHEN `MOMENTO_STATUSES[6]` is accessed
- THEN `elapsed == 120` and `short == "PEN"`
