# Delta for milestone-detector

## MODIFIED Requirements

### Requirement: Trigger Matrix with Status Guards

`async check_and_push() -> None` MUST iterate moments `1..6` in order. For each moment that is unfired AND whose trigger condition AND status guard are satisfied by `match_state.get_state().status`, the detector MUST (a) call `await data_source.get_details(momento)`, (b) call `match_state.update_details(...)`, (c) build the webhook payload from the updated state, (d) POST the payload, and (e) mark the moment fired regardless of POST success. The matrix is:

| M | Trigger | Status guard |
|---|---------|--------------|
| 1 | `elapsed >= 15` | `short == "1H"` |
| 2 | `elapsed >= 30` | `short in ("1H", "HT", "2H")` |
| 3 | `short == "HT"` | — |
| 4 | `elapsed >= 60` | `short in ("HT", "2H", "ET", "BT", "P", "AET", "PEN", "FT")` |
| 5 | `elapsed >= 75` | `short in ("2H", "ET", "BT", "P", "AET", "PEN", "FT")` |
| 6 | `short in ("FT", "AET", "PEN")` | — |

(Previously: momento 6 fired only on `FT`; status guards for momentos 4-5 did not include `ET`, `BT`, `P`, `AET`, `PEN` — so extra-time and penalty matches would skip later moments.)

#### Scenario: Momento 1 fires at min 16 in 1H

- GIVEN `state.elapsed=16, state.short="1H"` and all moments unfired
- WHEN `await check_and_push()` runs
- THEN `data_source.get_details(1)` is awaited
- AND the webhook is posted once
- AND `_fired[1] is True`
- AND `_fired[2..6]` remain `False`

#### Scenario: Status guard blocks late minute-16 in 2H

- GIVEN `state.elapsed=16, state.short="2H"` and moment 1 unfired
- WHEN `await check_and_push()` runs
- THEN moment 1 does NOT fire (status guard `short == "1H"` fails)
- AND no `data_source.get_details(1)` is awaited
- AND `_fired[1] is False`

#### Scenario: Momento 6 fires exactly once at FT

- GIVEN `state.short="FT"` and all moments unfired
- WHEN `await check_and_push()` runs twice
- THEN `_fired[6] is True` after the first call
- AND the second call does not re-post (data_source.get_details(6) is awaited at most once across both calls)

#### Scenario: Multiple moments fire in the same tick when guards are satisfied

- GIVEN `state.elapsed=82, state.short="2H"` and all moments unfired
- WHEN `await check_and_push()` runs
- THEN moments 1, 2, 4, and 5 all fire (in that order)
- AND moment 3 (HT guard) and moment 6 (FT guard) do NOT fire

#### Scenario: Momento 6 fires on AET

- GIVEN `state.short="AET"`, `state.elapsed=120`, all moments unfired
- WHEN `await check_and_push()` runs
- THEN `data_source.get_details(6)` is awaited
- AND the webhook is posted once
- AND `_fired[6] is True`

#### Scenario: Momento 6 fires on PEN

- GIVEN `state.short="PEN"`, `state.elapsed=120`, all moments unfired
- WHEN `await check_and_push()` runs
- THEN `data_source.get_details(6)` is awaited
- AND the webhook is posted once
- AND `_fired[6] is True`

#### Scenario: Momento 4 fires during ET

- GIVEN `state.elapsed=95, state.short="ET"`, all moments unfired
- WHEN `await check_and_push()` runs
- THEN `data_source.get_details(4)` is awaited
- AND `_fired[4] is True`

#### Scenario: Momento 5 fires during ET

- GIVEN `state.elapsed=105, state.short="ET"`, all moments unfired
- WHEN `await check_and_push()` runs
- THEN `data_source.get_details(5)` is awaited
- AND `_fired[5] is True`
