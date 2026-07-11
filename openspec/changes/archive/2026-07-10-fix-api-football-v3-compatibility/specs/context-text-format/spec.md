# Delta for context-text-format

## MODIFIED Requirements

### Requirement: Header

Format: `⚽ {home_name} {home_goals} - {away_goals} {away_name} | Minuto {elapsed} | {period_name}`. Period name MUST map `status.short` to a Spanish label via the `PERIOD_NAMES` map in match-state-manager, which covers all 18 API-Football v3 statuses (e.g. `1H`→`"1er Tiempo"`, `HT`→`"Entretiempo"`, `2H`→`"2do Tiempo"`, `ET`→`"Tiempo extra"`, `BT`→`"Descanso tiempo extra"`, `P`→`"Penales en curso"`, `FT`→`"Final"`, `AET`→`"Final (tiempo extra)"`, `PEN`→`"Final (penales)"`, `LIVE`→`"En curso"`). Any `status.short` not in the map MUST fall back to the raw `short` value.

(Previously: only 4 period names existed — `1H`, `HT`, `2H`, `FT`.)

#### Scenario: Extra time minute 101 renders as Final period

- GIVEN elapsed=101, short="FT", home=Argentina(2) away=Holanda(2)
- WHEN the header is built
- THEN it reads `⚽ Argentina 2 - 2 Holanda | Minuto 101 | Final`

#### Scenario: AET status renders as Final (tiempo extra)

- GIVEN elapsed=120, short="AET", home=Argentina(1) away=Holanda(0)
- WHEN the header is built
- THEN it reads `⚽ Argentina 1 - 0 Holanda | Minuto 120 | Final (tiempo extra)`

#### Scenario: PEN status renders as Final (penales)

- GIVEN elapsed=120, short="PEN", home=Argentina(2) away=Holanda(2)
- WHEN the header is built
- THEN it reads `⚽ Argentina 2 - 2 Holanda | Minuto 120 | Final (penales)`

#### Scenario: Unknown status falls back to raw short value

- GIVEN short="ZZZ" (not in PERIOD_NAMES)
- WHEN the header is built
- THEN the period name segment is the raw string `"ZZZ"`

### Requirement: Goals

Format: `GOLES: {home_goals} - {away_goals}`. Each item is `{player} ({minute}')`, `{player} (pen {minute}')` when `"Penalty" in detail AND "Missed" not in detail`, or `{player} (og {minute}')` for an own goal (when `"Own Goal" in detail`). Items joined by `, `. Own Goal events MUST appear under the BENEFITED team (the team that did NOT commit the own goal), NOT under `event.team`. Events with `"Missed" in detail` (e.g. `detail == "Missed Penalty"`) MUST be EXCLUDED from the goals section entirely — they are NOT goals, scored or otherwise. If a team has no goals, its side is empty. If neither scored, the section is `GOLES: Sin goles aún`.

(Previously: every `type == "Goal"` event appeared under `event.team`; Missed Penalty inflated the section; Own Goal credited the wrong team.)

#### Scenario: Match with no goals

- GIVEN events with no Goal entries
- WHEN the goals section is built
- THEN it reads exactly `GOLES: Sin goles aún`

#### Scenario: Scored Penalty renders as (pen X')

- GIVEN event: `Goal Argentina Messi 73' detail="Penalty"`
- WHEN the goals section is built
- THEN it contains `Messi (pen 73')`

#### Scenario: Own Goal is flipped to the BENEFITED team

- GIVEN event: `Goal Argentina Molina 35' detail="Own Goal"`, home=Argentina, away=Netherlands
- WHEN the goals section is built
- THEN the section contains `Molina (og 35')` under Netherlands' side (away)
- AND the home (Argentina) side of the goals list is empty for this event

#### Scenario: Missed Penalty is excluded from GOLES section

- GIVEN event: `Goal Argentina Messi 73' detail="Missed Penalty"`
- WHEN the goals section is built
- THEN the section does NOT contain the substring `Messi` (no `(pen)`, no `(og)`, no plain goal)
- AND if no other goals exist, the section reads `GOLES: Sin goles aún`

#### Scenario: Mixed scored-penalty and missed-penalty in same section

- GIVEN events: `Goal Argentina Messi 73' detail="Penalty"` AND `Goal Argentina Di Maria 80' detail="Missed Penalty"`
- WHEN the goals section is built
- THEN the section contains `Messi (pen 73')`
- AND the section does NOT contain `Di Maria` anywhere
