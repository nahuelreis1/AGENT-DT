# Delta for match-state-manager

## MODIFIED Requirements

### Requirement: Detail Update and Score Reconciliation

`update_details(events, home_stats, away_stats, home_players, away_players) -> None` MUST replace the stored `events`, `home_stats`, `away_stats`, `home_players`, and `away_players` with the supplied values. It MUST THEN recompute `home.goals` and `away.goals` from the event list using the following rules, which OVERRIDE any value previously set by `update_fixture()`:

- An event is a candidate goal IFF `type == "Goal"`.
- A candidate goal with `"Missed" in detail` (e.g. `detail == "Missed Penalty"`) is NOT a goal and MUST be skipped.
- A candidate goal with `"Own Goal" in detail` MUST be attributed to the OPPOSING team (the team that BENEFITED), NOT to `event.team`. The team that committed the own goal is the one listed in `event.team`.

(Previously: every `type == "Goal"` event counted for `event.team`; "Missed Penalty" inflated the score; "Own Goal" credited the wrong team.)

#### Scenario: Min 15 with empty events yields 0-0

- GIVEN a manager that has already received `update_fixture` for fixture 868019
- WHEN `update_details(events=[], ...)` is called
- THEN `get_state().home.goals == 0`
- AND `get_state().away.goals == 0`

#### Scenario: 4 Goal events split 2-2 override API score

- GIVEN events: `[Goal Argentina Molina 35', Goal Argentina Messi pen 73', Goal Holanda Weghorst 83', Goal Holanda Weghorst 101']`
- AND the API score from `update_fixture` was `1-1`
- WHEN `update_details(events=events, ...)` is called
- THEN `get_state().home.goals == 2`
- AND `get_state().away.goals == 2`

#### Scenario: Reconciliation is idempotent

- GIVEN events with 2 home goals and 1 away goal
- WHEN `update_details(events, ...)` is called twice with the same input
- THEN `home.goals` and `away.goals` are unchanged

#### Scenario: Missed Penalty does not increment the score

- GIVEN events: `[Goal Argentina Messi Missed Penalty 73']` (type "Goal", detail "Missed Penalty")
- WHEN `update_details(events, ...)` is called
- THEN `get_state().home.goals == 0`
- AND `get_state().away.goals == 0`

#### Scenario: Own Goal by Argentina counts for Netherlands

- GIVEN `event.team == "Argentina"`, `event.player == "Molina"`, `type == "Goal"`, `detail == "Own Goal"`
- AND the other team is `Netherlands`
- WHEN `update_details(events, ...)` is called
- THEN `get_state().home.goals == 0` (Argentina did NOT score)
- AND `get_state().away.goals == 1` (Netherlands BENEFITED)

### Requirement: Context Text Format

`get_context_text() -> str` MUST return a single UTF-8 string with exactly 7 sections in this fixed order: Header, Goals, Stats, Standout players, Weak players, Substitutions, Cards. Sections MUST be separated by a single blank line (`\n\n`) with one trailing `\n`. All section labels, period names, "Sin …" fallbacks, and highlight-line composition MUST match the `context-text-format` spec exactly (snapshot test pins the byte-level output and is regenerated as part of this change).

`PERIOD_NAMES` MUST cover all 18 API-Football v3 statuses with the exact Spanish labels defined in the change proposal (e.g. `"AET" → "Final (tiempo extra)"`, `"PEN" → "Final (penales)"`, `"ET" → "Tiempo extra"`, `"LIVE" → "En curso"`). Any `status.short` value not in the map MUST fall back to the raw `short` value. The goals section MUST (a) flip Own Goal events to the BENEFITED team's list, (b) exclude any event with `"Missed" in detail` from the goals section, and (c) format penalty goals as `(pen X')` ONLY when `"Penalty" in detail AND "Missed" not in detail` — `"Missed Penalty"` MUST NOT be formatted as `(pen X')`.

(Previously: goals section listed every Goal event under `event.team` regardless of own-goal flip; "Missed Penalty" appeared as a regular goal; only 4 period names existed.)

#### Scenario: Snapshot at minute 67 matches the pinned format

- GIVEN state `home=Argentina(2)`, `away=Holanda(1)`, `elapsed=67`, `short="2H"`, with populated events/stats/players
- WHEN `get_context_text()` is called
- THEN the output starts with `⚽ Argentina 2 - 1 Holanda | Minuto 67 | 2do Tiempo`
- AND the output contains exactly 7 sections separated by blank lines

#### Scenario: Pre-kickoff uses every empty-section variant

- GIVEN empty events, `home_stats is None`, `away_stats is None`, empty player lists, `elapsed=0`
- WHEN `get_context_text()` is called
- THEN `GOLES: Sin goles aún`
- AND `ESTADÍSTICAS: No disponibles aún`
- AND `JUGADORES DESTACADOS: Sin datos suficientes`
- AND `JUGADORES FLOJOS: Sin datos suficientes`
- AND `CAMBIOS REALIZADOS: Ninguno`
- AND `TARJETAS: Ninguna`

#### Scenario: Status AET renders as Final (tiempo extra) in header

- GIVEN `status.elapsed == 120`, `status.short == "AET"`, home=Argentina(1) away=Holanda(0)
- WHEN `get_context_text()` is called
- THEN the header reads `⚽ Argentina 1 - 0 Holanda | Minuto 120 | Final (tiempo extra)`

#### Scenario: Status PEN renders as Final (penales) in header

- GIVEN `status.elapsed == 120`, `status.short == "PEN"`, home=Argentina(2) away=Holanda(2)
- WHEN `get_context_text()` is called
- THEN the header reads `⚽ Argentina 2 - 2 Holanda | Minuto 120 | Final (penales)`

#### Scenario: Unknown status falls back to raw short value

- GIVEN `status.short == "ZZZ"` (not in `PERIOD_NAMES`)
- WHEN `get_context_text()` is called
- THEN the header's period name is the raw string `"ZZZ"` (no crash, no translation)

#### Scenario: Own Goal appears under the BENEFITED team in goals section

- GIVEN event: `Goal Argentina Molina 35' detail="Own Goal"`, with Argentina=home and Netherlands=away
- WHEN `get_context_text()` is called
- THEN the `GOLES` section lists `Molina (og 35')` under Netherlands' side (NOT Argentina's)

#### Scenario: Missed Penalty does not appear in GOLES section

- GIVEN event: `Goal Argentina Messi 73' detail="Missed Penalty"`
- WHEN `get_context_text()` is called
- THEN the `GOLES` section does NOT contain the word `Messi`
- AND if no other goals exist, the section reads `GOLES: Sin goles aún`

#### Scenario: Scored Penalty is formatted as (pen X'), Missed Penalty is not

- GIVEN events: `Goal Argentina Messi 73' detail="Penalty"` AND `Goal Argentina Di Maria 80' detail="Missed Penalty"`
- WHEN `get_context_text()` is called
- THEN the goals section contains `Messi (pen 73')`
- AND the goals section does NOT contain the substring `Di Maria (pen 80')` (no penalty formatting on the missed one)
- AND the goals section does NOT contain `Di Maria` at all (missed penalty excluded)
