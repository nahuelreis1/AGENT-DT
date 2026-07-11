# Design: Enrich Context (7 to 9 sections, full data utilization)

## Technical Approach

Additive enrichment: append two new sections (FORMACIONES, TODOS LOS JUGADORES) and extend existing sections (Stats 3→10 lines, player highlights 4→12 fields). New `LineupTeam`/`LineupPlayer` models, `parse_lineups` parser, `fetch_lineups` client method, `get_lineups` on the DataSource Protocol. Lineups fetched once in lifespan (not per-momento). All new code follows existing patterns: null-safe parsers, structural Protocol, shared parse seam.

## Architecture Decisions

| Decision | Choice | Rejected | Rationale |
|----------|--------|----------|-----------|
| Lineup data source | `LineupTeam.startXI` for player list; join to `PlayerStats` by name for ratings/stats | Use `PlayerStats` directly (filter `substitute=False`) | Spec says "Players MUST be listed in lineup input order" — only the lineup preserves that order |
| 204 handling | Check `resp.status_code == 204` in shared `_get`, return `[]` before `.json()` | Per-method override | 204 only occurs on lineups; `_get` change is 1 line, harmless to other endpoints, no duplication |
| Stats section labels/order | Follow spec: 10 lines, `POSESIÓN…TARJETAS ROJAS` | Task's 8-line variant | Specs are committed source of truth; snapshot test pins spec |
| FORMACIONES format | Single line per spec: `FORMACIONES: {home} {f1} - {away} {f2}` | Task's multi-line | Spec scenario explicitly pins single-line format |
| Stats section header | No header line — section IS the stat lines (existing pattern) | Add "ESTADÍSTICAS DE EQUIPO:" header | Existing snapshot test has no header; spec fallback uses `ESTADÍSTICAS:` not `ESTADÍSTICAS DE EQUIPO:` |
| Position abbreviation | First letter of `LineupPlayer.pos`: G→ARQ, D→DEF, M→MED, F→ATK | Full position string | API lineup `pos` is "GK"/"DF"/"MF"/"FW"; first letter always maps cleanly |

## Data Flow

```
lifespan startup
  │
  ├─ get_fixture() → update_fixture(state)
  ├─ get_lineups() → parse_lineups() → (home, away)
  │   └─ update_lineups(home, away)    # (None,None) → no-op
  └─ yield (app serves)

milestone fire (per-momento)
  │
  ├─ get_details(momento) → update_details(events, stats, players)
  └─ get_context_text()
       ├─ _header_section         # unchanged
       ├─ _lineups_section         # NEW (formation strings)
       ├─ _goals_section           # unchanged
       ├─ _stats_section           # EXTENDED 3→10 lines
       ├─ _standout_players_section # ENRICHED highlights
       ├─ _weak_players_section    # ENRICHED highlights
       ├─ _all_players_section     # NEW (22 starters + stats)
       ├─ _substitutions_section   # unchanged
       └─ _cards_section           # unchanged
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/models.py` | Modify | Add `LineupPlayer`, `LineupTeam`; add `home_lineup`/`away_lineup` to `MatchState` (default `None`) |
| `backend/parsers.py` | Modify | Add `parse_lineups(items)`; import new models |
| `backend/services/api_football.py` | Modify | Add `fetch_lineups(fixture_id)`; add 204 check in `_get` |
| `backend/data_source.py` | Modify | Add `get_lineups()` to Protocol, MockDataSource, LiveDataSource; import `parse_lineups` |
| `backend/services/match_state.py` | Modify | Add `update_lineups()`; extend `_stats_section` (3→10); enrich `_player_highlights`; add `_lineups_section`, `_all_players_section`; update `get_context_text` section list (7→9) |
| `backend/mock_data/lineups.json` | Create | ARG 4-3-3 (11 starters, Scaloni), NED 3-4-1-2 (11 starters, Van Gaal); v3 envelope |
| `backend/main.py` | Modify | Lifespan: fetch lineups after `update_fixture`, before `yield` |
| `backend/tests/test_*.py` | Modify | New tests for all new code; update snapshot + section-count tests |

## Interfaces / Contracts

### Models (`backend/models.py`)

```python
class LineupPlayer(BaseModel):
    player_id: int = Field(ge=0)       # 0 = unknown
    name: str = Field(min_length=1)
    number: int = Field(ge=0)          # default 0
    pos: str = Field(min_length=1)     # "GK", "DF", etc.
    grid: str | None = None            # "1:1" or None

class LineupTeam(BaseModel):
    team_id: int = Field(gt=0)
    team_name: str = Field(min_length=1)
    formation: str = Field(min_length=1)  # "4-3-3"
    startXI: list[LineupPlayer] = []
    substitutes: list[LineupPlayer] = []
    coach_name: str | None = None

# MatchState additions (after away_players):
    home_lineup: LineupTeam | None = None
    away_lineup: LineupTeam | None = None
```

### Parser (`backend/parsers.py`)

```python
def parse_lineups(items: list[dict]) -> tuple[LineupTeam | None, LineupTeam | None]:
    # [] → (None, None). Trust input order [0]=home, [1]=away.
    # Per team: team.id→team_id, team.name→team_name, formation→formation,
    #   startXI[].{player.id,player.name,number,pos,grid} → LineupPlayer
    #   substitutes[] same shape
    #   coach.name → coach_name (missing key → None)
    # All fields via _safe_int/_safe_str; null grid → None
```

### Client (`backend/services/api_football.py`)

```python
# _get change (1 line added):
if resp.status_code == 204:
    return []  # before resp.json()

async def fetch_lineups(self, fixture_id: int) -> list[dict]:
    return await self._get("/fixtures/lineups", {"fixture": fixture_id})
```

### Data Source (`backend/data_source.py`)

```python
# Protocol addition:
async def get_lineups(self) -> tuple[LineupTeam | None, LineupTeam | None]: ...

# MockDataSource.get_lineups:
#   read lineups.json → _load_json → parse_lineups; missing file → (None, None)
# LiveDataSource.get_lineups:
#   await client.fetch_lineups(fixture_id) → parse_lineups
```

### Context Text — EXACT 9-section format

Section order: Header, Formaciones, Goals, Stats, Standout, Weak, AllPlayers, Subs, Cards. Joined by `\n\n`, trailing `\n`.

**FORMACIONES** (single line, spec-pinned):
```
FORMACIONES: Argentina 4-3-3 - Holanda 3-4-1-2
```
Fallback (either lineup None): `FORMACIONES: No disponibles aún`

**STATS** (10 lines, no header, spec order):
```
POSESIÓN: ARG 55% - HOL 45%
TIROS AL ARCO: ARG 1 - HOL 0
xG: ARG 0.18 - HOL 0.05
TIROS TOTALES: ARG 2 - HOL 1
CÓRNERES: ARG 1 - HOL 0
FOULTAS: ARG 3 - HOL 4
OFFSIDE: ARG 0 - HOL 1
PASES ACERTADOS: ARG 92% - HOL 84%
TARJETAS AMARILLAS: ARG 0 - HOL 0
TARJETAS ROJAS: ARG 0 - HOL 0
```
Fallback: `ESTADÍSTICAS: No disponibles aún`

**ENRICHED player highlights** (standout `—` and weak `—`):
`- {name} ({rating}) - {highlights}` where highlights is a comma-joined list:
- `{minutes}'` — always
- `{n} gol/goles` — if goals > 0
- `{n} asistencia/asistencias` — if assists > 0
- `{shots_on}/{shots_total} al arco` — if shots_total > 0
- `{passes_total} pases ({pass_accuracy})` — if passes_total > 0
- `{key_passes} pases clave` — if key_passes > 0
- `{dribbles_success}/{dribbles_attempts} regates` — ALWAYS
- `{duels_won}/{duels_total} duelos` — if duels_total > 0
- `{n} faltas` — if fouls_committed > 0
- `{n} falta recibida/faltas recibidas` — if fouls_drawn > 0
- `{n} amarilla/amarillas` — if yellow > 0
- `{n} roja/rojas` — if red > 0

**TODOS LOS JUGADORES** (new section):
```
TODOS LOS JUGADORES:
Argentina (4-3-3):
- D. Martínez (ARQ, 6.8) - 15', 0 tiros, 3 pases, 0/0 duelos
- N. Molina (DEF, 7.5) - 15', 0 tiros, 8 pases (75%), 2/3 regates, 1/2 duelos
[... 11 starters ...]
Netherlands (3-4-1-2):
- A. Noppert (ARQ, 6.3) - 15', 0 tiros, 3 pases, 1/2 duelos
[... 11 starters ...]
```
Fallback (both lineups None): `TODOS LOS JUGADORES: Sin datos suficientes`

Compact line: `- {name} ({pos_abbr}, {rating}) - {minutes}', {compact_highlights}`
- pos_abbr: `LineupPlayer.pos[0]` → G=ARQ, D=DEF, M=MED, F=ATK
- rating: actual or `—` if empty
- compact_highlights (zero-suppressed, always-shown baseline):
  - `{shots_total} tiros` — always
  - `{passes_total} pases` — always, `({pass_accuracy})` appended if non-empty
  - `{dribbles_success}/{dribbles_attempts} regates` — if attempts > 0
  - `{duels_won}/{duels_total} duelos` — always
  - goals/assists/key_passes/fouls/cards — only if > 0

**Lifespan** (`backend/main.py`): after `update_fixture()`, before `yield`:
```python
home_lineup, away_lineup = await app.state.data_source.get_lineups()
app.state.match_state.update_lineups(home_lineup, away_lineup)
```
`(None, None)` → `update_lineups` stores None/None (no-op effect).

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | `parse_lineups` | 6 scenarios: both teams, empty→(None,None), missing coach→None, null grid→None, single element→(team,None), order trust |
| Unit | `fetch_lineups` | 3 scenarios via respx: 200 returns list + count++, 204 returns [] + count++, 4xx raises |
| Unit | `get_lineups` (both DS) | 4 scenarios: mock reads file, mock missing file→(None,None), live delegates+parses, live empty→(None,None) |
| Unit | `update_lineups` | 3 scenarios: stores+readable, (None,None) no raise, before fixture raises |
| Unit | `_lineups_section` | 3 scenarios: both loaded (single line), not loaded (fallback), one missing (fallback) |
| Unit | `_all_players_section` | 3 scenarios: 22 starters grouped, both None (fallback), one team only |
| Unit | enriched `_stats_section` | 2 scenarios: all 10 lines in order, fallback when None |
| Unit | enriched `_player_highlights` | 3 scenarios: full stats, all zeros (only minutes+dribbles), partial |
| Unit | `LineupPlayer`/`LineupTeam` models | 4 scenarios: grid null→None, grid string preserved, missing coach→None, empty XI valid |
| Snapshot | `get_context_text` | UPDATED: 9 sections, byte-pinned at min 67 with lineups |
| Integration | lifespan | lineups fetched on startup; (None,None) no-op |
| Regression | existing tests | update section count 7→9, snapshot expected string, stat line assertions |

## Migration / Rollout

No migration required. `git revert` restores 7-section format. No DB, no external systems, 6 milestone triggers unchanged.

## Open Questions

- [ ] **Stats labels discrepancy**: Task brief shows 8 lines with "CORNERS/FALTAS/OFFSIDES/PRECISIÓN DE PASES" and xG last; specs show 10 lines with "CÓRNERES/FOULTAS/OFFSIDE/PASES ACERTADOS" and xG 3rd, plus TARJETAS AMARILLAS/ROJAS. Design follows specs (authoritative). Confirm before apply.
- [ ] **Standout header text**: Task shows `(rating >= 7.0)`, spec + existing code use `(por rating)`. Design follows spec. Confirm.
- [ ] **Compact highlights rules**: Task says "same zero-suppression rules" but examples show `0 tiros` and `0/0 duelos` always rendered (opposite of enriched rules). Design matches examples (always-show baseline for shots/passes/duels; suppress 0/0 dribbles). Confirm before apply.
- [ ] **Lineup→PlayerStats join key**: Matching by `name` string. If API-Football uses different name formats between `/lineups` and `/players` endpoints, a player may not match. Fallback: rating="—", no stats. Verify name consistency in mock data.
