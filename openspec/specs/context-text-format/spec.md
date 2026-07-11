# context-text-format Specification

## Purpose

Exact text format produced by `MatchStateManager.get_context_text()` (change 2). The string is injected into n8n AI Agent prompts at every `momento` push (m=1..6), so its structure is a contract: same input MUST always produce the same text, and downstream prompt engineering assumes this exact section order and labels. A snapshot test in change 2 pins the format.

## Requirements

### Requirement: Sections and Order

The system MUST emit exactly 7 sections in this fixed order, separated by a single blank line: Header, Goals, Stats, Standout players, Weak players, Substitutions, Cards. Output MUST be a single UTF-8 string with `\n\n` between sections and a single trailing `\n`.

#### Scenario: Full match at minute 67 with all data

- GIVEN state home=Argentina(2) away=Holanda(1), elapsed=67, short="2H", events include Molina(35), Messi pen(73), Weghorst(83), Montiel yellow(78), Martínez→Paredes(82), all stats and players populated
- WHEN `get_context_text()` is called
- THEN the output starts with `⚽ Argentina 2 - 1 Holanda | Minuto 67 | 2do Tiempo`
- AND contains the 7 sections in order separated by blank lines

#### Scenario: Pre-kickoff uses every empty-section variant

- GIVEN empty `events`, `home_stats is None`, `away_stats is None`, empty player lists, elapsed=0
- WHEN `get_context_text()` is called
- THEN goals=`GOLES: Sin goles aún`, stats=`ESTADÍSTICAS: No disponibles aún`
- AND standout=`JUGADORES DESTACADOS: Sin datos suficientes`, weak=`JUGADORES FLOJOS: Sin datos suficientes`
- AND subs=`CAMBIOS REALIZADOS: Ninguno`, cards=`TARJETAS: Ninguna`

### Requirement: Header

Format: `⚽ {home_name} {home_goals} - {away_goals} {away_name} | Minuto {elapsed} | {period_name}`. Period name MUST map `status.short` to a Spanish label via the `PERIOD_NAMES` map in match-state-manager, which covers all 19 API-Football v3 statuses: `"1H"→"1er Tiempo"`, `"HT"→"Entretiempo"`, `"2H"→"2do Tiempo"`, `"ET"→"Tiempo extra"`, `"BT"→"Descanso tiempo extra"`, `"P"→"Penales en curso"`, `"FT"→"Final"`, `"AET"→"Final (tiempo extra)"`, `"PEN"→"Final (penales)"`, `"NS"→"No iniciado"`, `"TBD"→"Horario a confirmar"`, `"SUSP"→"Suspendido"`, `"INT"→"Interrumpido"`, `"PST"→"Postergado"`, `"CANC"→"Cancelado"`, `"ABD"→"Abandonado"`, `"AWD"→"Perdida por regla"`, `"WO"→"Ganado por ausencia"`, `"LIVE"→"En curso"`. Any `status.short` not in the map MUST fall back to the raw `short` value.

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

### Requirement: Stats

Three lines in order: `POSESIÓN: {home_abbr} {home_possession} - {away_abbr} {away_possession}`, `TIROS AL ARCO: {home_abbr} {home_sog} - {away_abbr} {away_sog}`, `xG: {home_abbr} {home_xg} - {away_abbr} {away_xg}`. Abbr = first 3 letters of team name uppercased (Argentina→ARG). If either `home_stats` or `away_stats` is `None`, the section collapses to the single line `ESTADÍSTICAS: No disponibles aún` (no per-line output).

#### Scenario: Stats not yet loaded collapses to single line

- GIVEN `home_stats is None` and `away_stats is None`
- WHEN the stats section is built
- THEN the section reads exactly `ESTADÍSTICAS: No disponibles aún`
- AND no `POSESIÓN`, `TIROS AL ARCO`, or `xG` lines are emitted

### Requirement: Standout Players

`JUGADORES DESTACADOS (por rating):` followed by up to 3 players with `rating >= 7.0`, sorted by rating descending. Each line: `- {name} ({rating}) - {highlights}` where `highlights` summarises goals, assists, key passes, and `dribbles_success/dribbles_attempts`. If none meet the threshold, the section is `JUGADORES DESTACADOS: Sin datos suficientes`.

### Requirement: Weak Players

`JUGADORES FLOJOS:` followed by up to 2 players with `0 < rating < 6.5`, sorted by rating ascending (worst first). Same line format as standout. If none: `JUGADORES FLOJOS: Sin datos suficientes`.

### Requirement: Substitutions

`CAMBIOS REALIZADOS: {list}` where each item is `{out_player} → {in_player} ({minute}')` (derived from events with `type == "subst"`); items joined by `, `. If empty: `CAMBIOS REALIZADOS: Ninguno`.

### Requirement: Cards

`TARJETAS: {list}` where each item is `{player} {emoji} ({minute}')` with 🟨 for yellow and 🟥 for red. If empty: `TARJETAS: Ninguna`.

### Requirement: Language

Labels, separators, and period names MUST be in Spanish (rioplatense: "1er Tiempo", "2do Tiempo", "GOLES", "Sin goles aún"). Team names and player names are passed through unchanged — NOT translated.
