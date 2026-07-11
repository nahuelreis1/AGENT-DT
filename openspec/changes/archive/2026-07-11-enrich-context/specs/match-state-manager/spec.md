# Delta for match-state-manager

## ADDED Requirements

### Requirement: Lineup Update

`update_lineups(home_lineup: LineupTeam | None, away_lineup: LineupTeam | None) -> None` MUST store the supplied lineups on the current `MatchState` (overwriting any prior lineups). It MUST accept `(None, None)` without raising (pre-kickoff / 204 case). When called before `update_fixture()`, it MUST raise `RuntimeError` (same contract as `update_details`).

#### Scenario: Lineups stored and readable

- GIVEN a manager that has received `update_fixture` for fixture 868019
- WHEN `update_lineups(home=LineupTeam(...), away=LineupTeam(...))` is called
- THEN `get_state().home_lineup` and `get_state().away_lineup` are the supplied objects

#### Scenario: None lineups accepted without raising

- GIVEN a manager with a stored fixture
- WHEN `update_lineups(None, None)` is called
- THEN no exception is raised
- AND `get_state().home_lineup is None` and `get_state().away_lineup is None`

#### Scenario: Lineup update before fixture raises RuntimeError

- GIVEN a freshly constructed `MatchStateManager()`
- WHEN `update_lineups(None, None)` is called
- THEN a `RuntimeError` is raised

## MODIFIED Requirements

### Requirement: Construction and Fixture Update

`MatchStateManager` MUST take no constructor arguments. `update_fixture(match_state: MatchState) -> None` MUST store the supplied `MatchState` (overwriting any prior state, including the events list, stats, players, and lineups — `update_fixture` is a "snapshot" update). `get_state() -> MatchState` MUST return the stored state or raise `RuntimeError` if `update_fixture()` was never called.
(Previously: snapshot update covered events, stats, and players; now also resets lineups)

#### Scenario: Uninitialized state raises on get_state

- GIVEN a freshly constructed `MatchStateManager()`
- WHEN `get_state()` is called
- THEN a `RuntimeError` is raised

#### Scenario: Fixture update makes state readable

- GIVEN a `MatchState` with `fixture_id=868019`, `home.goals=0`, `away.goals=0`, `status.short="1H"`
- WHEN `update_fixture(state)` is called
- THEN `get_state().fixture_id == 868019`
- AND `get_state().status.short == "1H"`

### Requirement: Detail Update and Score Reconciliation

`update_details(events, home_stats, away_stats, home_players, away_players) -> None` MUST replace the stored `events`, `home_stats`, `away_stats`, `home_players`, and `away_players` with the supplied values. It MUST NOT touch the stored lineups (`home_lineup` / `away_lineup` remain unchanged by a details update — lineups are set once via `update_lineups`). It MUST THEN recompute `home.goals` and `away.goals` from the event list using the following rules, which OVERRIDE any value previously set by `update_fixture()`:

- An event is a candidate goal IFF `type == "Goal"`.
- A candidate goal with `"Missed" in detail` is NOT a goal and MUST be skipped.
- A candidate goal with `"Own Goal" in detail` MUST be attributed to the OPPOSING (BENEFITED) team, NOT to `event.team`.

This logic MUST be shared with the goals section text (via a shared helper, e.g. `_goals_for_team`).

#### Scenario: Min 15 with empty events yields 0-0

- GIVEN a manager that has already received `update_fixture` for fixture 868019
- WHEN `update_details(events=[], ...)` is called
- THEN `get_state().home.goals == 0` AND `get_state().away.goals == 0`

#### Scenario: 4 Goal events split 2-2 override API score

- GIVEN events with 2 home goals and 2 away goals AND the API score from `update_fixture` was `1-1`
- WHEN `update_details(events=events, ...)` is called
- THEN `get_state().home.goals == 2` AND `get_state().away.goals == 2`

#### Scenario: Detail update preserves previously set lineups

- GIVEN a manager that has received `update_lineups(home, away)` with populated lineups
- WHEN `update_details(events=[], ...)` is called
- THEN `get_state().home_lineup` and `get_state().away_lineup` are unchanged

#### Scenario: Missed Penalty does not increment the score

- GIVEN events: `[Goal Argentina Messi Missed Penalty 73']`
- WHEN `update_details(events, ...)` is called
- THEN `get_state().home.goals == 0` AND `get_state().away.goals == 0`

#### Scenario: Own Goal by Argentina counts for Netherlands

- GIVEN `event.team == "Argentina"`, `detail == "Own Goal"`, other team is `Netherlands`
- WHEN `update_details(events, ...)` is called
- THEN `get_state().home.goals == 0` AND `get_state().away.goals == 1`

### Requirement: Context Text Format

`get_context_text() -> str` MUST return a single UTF-8 string with exactly 9 sections in this fixed order: Header, Formaciones, Goals, Stats, Standout players, Weak players, All Players, Substitutions, Cards. Sections MUST be separated by a single blank line (`\n\n`) with one trailing `\n`. All section labels, period names, "Sin …" / "No disponibles aún" fallbacks, and highlight-line composition MUST match the `context-text-format` spec exactly (snapshot test pins the byte-level output).

The Stats section MUST emit one line per TeamStats field (10 lines). The Standout and Weak player lines MUST include enriched stats (minutes, goals, assists, shots, passes, duels, fouls, cards). The Formaciones and All Players sections MUST use the stored `home_lineup` / `away_lineup`, collapsing to their fallbacks when lineups are `None`.

`PERIOD_NAMES` MUST cover all 19 API-Football v3 statuses with the exact Spanish labels. Any `status.short` not in the map MUST fall back to the raw `short`. The goals section MUST (a) flip Own Goal events to the BENEFITED team, (b) exclude events with `"Missed" in detail`, (c) format penalty goals as `(pen X')` ONLY when `"Penalty" in detail AND "Missed" not in detail`, and (d) format own goals as `(og X')`.
(Previously: 7 sections — no Formaciones, no All Players; Stats had 3 lines; player highlights had 4 fields)

#### Scenario: Snapshot at minute 67 matches the pinned format

- GIVEN state `home=Argentina(2)`, `away=Holanda(1)`, `elapsed=67`, `short="2H"`, lineups loaded, with populated events/stats/players
- WHEN `get_context_text()` is called
- THEN the output starts with `⚽ Argentina 2 - 1 Holanda | Minuto 67 | 2do Tiempo`
- AND the output contains exactly 9 sections separated by blank lines

#### Scenario: Pre-kickoff uses every empty-section variant

- GIVEN empty events, `home_stats is None`, `away_stats is None`, empty player lists, `home_lineup is None`, `away_lineup is None`, elapsed=0
- WHEN `get_context_text()` is called
- THEN `FORMACIONES: No disponibles aún` AND `GOLES: Sin goles aún`
- AND `ESTADÍSTICAS: No disponibles aún` AND `JUGADORES DESTACADOS: Sin datos suficientes`
- AND `JUGADORES FLOJOS: Sin datos suficientes` AND `TODOS LOS JUGADORES: Sin datos suficientes`
- AND `CAMBIOS REALIZADOS: Ninguno` AND `TARJETAS: Ninguna`

#### Scenario: Stats section emits all 10 TeamStats fields

- GIVEN both `home_stats` and `away_stats` fully populated
- WHEN `get_context_text()` is called
- THEN the ESTADÍSTICAS section contains exactly 10 stat lines in the documented order

#### Scenario: Formaciones section reflects loaded lineups

- GIVEN `home_lineup.formation == "4-3-3"` and `away_lineup.formation == "3-4-1-2"`
- WHEN `get_context_text()` is called
- THEN the output contains `FORMACIONES: Argentina 4-3-3 - Holanda 3-4-1-2` in the second position

#### Scenario: All Players section lists 22 starters

- GIVEN `home_lineup.startXI` and `away_lineup.startXI` each have 11 players
- WHEN `get_context_text()` is called
- THEN the TODOS LOS JUGADORES section lists all 22 starters grouped by team with formation prefix

#### Scenario: Unknown status falls back to raw short value

- GIVEN `status.short == "ZZZ"` (not in `PERIOD_NAMES`)
- WHEN `get_context_text()` is called
- THEN the header's period name is the raw string `"ZZZ"`

#### Scenario: Own Goal appears under the BENEFITED team in goals section

- GIVEN event: `Goal Argentina Molina 35' detail="Own Goal"`, Argentina=home, Netherlands=away
- WHEN `get_context_text()` is called
- THEN the `GOLES` section lists `Molina (og 35')` under Netherlands' side
