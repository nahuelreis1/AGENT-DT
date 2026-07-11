# context-text-format Specification

## Purpose

Exact text format produced by `MatchStateManager.get_context_text()` (change 2). The string is injected into n8n AI Agent prompts at every `momento` push (m=1..6), so its structure is a contract: same input MUST always produce the same text, and downstream prompt engineering assumes this exact section order and labels. A snapshot test in change 2 pins the format.

## Requirements

### Requirement: Sections and Order

The system MUST emit exactly 9 sections in this fixed order, separated by a single blank line: Header, Formaciones, Goals, Stats, Standout players, Weak players, All Players, Substitutions, Cards. Output MUST be a single UTF-8 string with `\n\n` between sections and a single trailing `\n`.
(Previously: 7 sections — Header, Goals, Stats, Standout, Weak, Subs, Cards)

#### Scenario: Full match at minute 67 with all data

- GIVEN state home=Argentina(2) away=Holanda(1), elapsed=67, short="2H", lineups loaded, events include Molina(35), Messi pen(73), Weghorst(83), Montiel yellow(78), Martínez→Paredes(82), all stats and players populated
- WHEN `get_context_text()` is called
- THEN the output starts with `⚽ Argentina 2 - 1 Holanda | Minuto 67 | 2do Tiempo`
- AND contains the 9 sections in order separated by blank lines

#### Scenario: Pre-kickoff uses every empty-section variant

- GIVEN empty `events`, `home_stats is None`, `away_stats is None`, empty player lists, `home_lineup is None`, `away_lineup is None`, elapsed=0
- WHEN `get_context_text()` is called
- THEN formaciones=`FORMACIONES: No disponibles aún`, goals=`GOLES: Sin goles aún`, stats=`ESTADÍSTICAS: No disponibles aún`
- AND standout=`JUGADORES DESTACADOS: Sin datos suficientes`, weak=`JUGADORES FLOJOS: Sin datos suficientes`
- AND all-players=`TODOS LOS JUGADORES: Sin datos suficientes`, subs=`CAMBIOS REALIZADOS: Ninguno`, cards=`TARJETAS: Ninguna`

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

### Requirement: Formations

The system MUST emit a FORMACIONES section immediately after the Header. Format: `FORMACIONES: {home_name} {home_formation} - {away_name} {away_formation}`. When either `home_lineup` or `away_lineup` is `None` (lineups not loaded, e.g. 204 pre-kickoff), the section MUST collapse to `FORMACIONES: No disponibles aún`.

#### Scenario: Both lineups loaded

- GIVEN `home_lineup.formation == "4-3-3"` and `away_lineup.formation == "3-4-1-2"`, home=Argentina, away=Holanda
- WHEN the formations section is built
- THEN it reads `FORMACIONES: Argentina 4-3-3 - Holanda 3-4-1-2`

#### Scenario: Lineups not loaded collapses to fallback

- GIVEN `home_lineup is None` and `away_lineup is None`
- WHEN the formations section is built
- THEN it reads exactly `FORMACIONES: No disponibles aún`

#### Scenario: One lineup missing collapses to fallback

- GIVEN `home_lineup` is populated but `away_lineup is None`
- WHEN the formations section is built
- THEN it reads `FORMACIONES: No disponibles aún`

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

One line per TeamStats field (10 lines total) in this order: `POSESIÓN`, `TIROS AL ARCO`, `xG`, `TIROS TOTALES`, `CÓRNERES`, `FOULTAS`, `OFFSIDE`, `PASES ACERTADOS`, `TARJETAS AMARILLAS`, `TARJETAS ROJAS` — each formatted `{label}: {home_abbr} {home_val} - {away_abbr} {away_val}`. Abbr = first 3 letters of team name uppercased (Argentina→ARG). If either `home_stats` or `away_stats` is `None`, the section collapses to `ESTADÍSTICAS: No disponibles aún`.
(Previously: 3 lines — POSESIÓN, TIROS AL ARCO, xG)

#### Scenario: Stats not yet loaded collapses to single line

- GIVEN `home_stats is None` and `away_stats is None`
- WHEN the stats section is built
- THEN the section reads exactly `ESTADÍSTICAS: No disponibles aún`
- AND no `POSESIÓN`, `TIROS AL ARCO`, or `xG` lines are emitted

#### Scenario: All ten stat lines emitted when stats loaded

- GIVEN both teams' `TeamStats` fully populated (all 10 stat fields)
- WHEN the stats section is built
- THEN the section contains exactly 10 lines, one per TeamStats field
- AND the lines appear in the documented order

### Requirement: Standout Players

`JUGADORES DESTACADOS (por rating):` followed by up to 3 players with `rating >= 7.0`, sorted by rating descending. Each line: `- {name} ({rating}) - {highlights}` where `highlights` MUST summarise minutes, goals, assists, shots, passes, duels, fouls, and cards. If none meet the threshold, the section is `JUGADORES DESTACADOS: Sin datos suficientes`.
(Previously: highlights covered only goals, assists, key passes, dribbles)

#### Scenario: Enriched standout line includes minutes and cards

- GIVEN a player with `rating=8.1`, `minutes=67`, `goals=1`, `yellow_cards=1`
- WHEN the standout section is built
- THEN the line includes the minutes played and the yellow card count
- AND the line includes goals, shots, passes, duels, and fouls

### Requirement: Weak Players

`JUGADORES FLOJOS:` followed by up to 2 players with `0 < rating < 6.5`, sorted by rating ascending (worst first). Each line MUST use the same enriched format as standout players (minutes, goals, assists, shots, passes, duels, fouls, cards). If none: `JUGADORES FLOJOS: Sin datos suficientes`.
(Previously: same 4-field highlights as standout — goals, assists, key passes, dribbles)

#### Scenario: Enriched weak line matches standout format

- GIVEN a weak player with `rating=5.9`, `fouls_committed=3`, `minutes=67`
- WHEN the weak section is built
- THEN the line uses the same enriched format as standout players

### Requirement: All Players

The system MUST emit a TODOS LOS JUGADORES section immediately after Weak players. It MUST list all starters grouped by team, each team prefixed with its formation: `{team_name} ({formation}): {player1}, {player2}, ...`. Players MUST be listed in lineup input order. When no starters are available (`home_lineup is None` and `away_lineup is None`), the section MUST collapse to `TODOS LOS JUGADORES: Sin datos suficientes`.

#### Scenario: All 22 starters listed grouped by team

- GIVEN `home_lineup.startXI` has 11 players (formation 4-3-3) and `away_lineup.startXI` has 11 players (formation 3-4-1-2)
- WHEN the all-players section is built
- THEN it lists all 22 players grouped under their team with the formation prefix
- AND home starters appear before away starters

#### Scenario: No lineups loaded collapses to fallback

- GIVEN `home_lineup is None` and `away_lineup is None`
- WHEN the all-players section is built
- THEN it reads exactly `TODOS LOS JUGADORES: Sin datos suficientes`

### Requirement: Substitutions

`CAMBIOS REALIZADOS: {list}` where each item is `{out_player} → {in_player} ({minute}')` (derived from events with `type == "subst"`); items joined by `, `. If empty: `CAMBIOS REALIZADOS: Ninguno`.

### Requirement: Cards

`TARJETAS: {list}` where each item is `{player} {emoji} ({minute}')` with 🟨 for yellow and 🟥 for red. If empty: `TARJETAS: Ninguna`.

### Requirement: Language

Labels, separators, and period names MUST be in Spanish (rioplatense: "1er Tiempo", "2do Tiempo", "GOLES", "Sin goles aún"). Team names and player names are passed through unchanged — NOT translated.
