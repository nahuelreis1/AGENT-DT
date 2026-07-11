# Proposal: Fix API-Football v3 Compatibility

## Intent

The backend was built from a description of API-Football v3, not the official spec. 9 incompatibilities (3 CRITICAL: crash; 3 MODERATE: wrong data; 3 LOW: mock drift) will block or corrupt the first live call. This change aligns parser, models, and services with the real API shape so the first real request succeeds.

## Scope

### In Scope
- `backend/models.py` — `FixtureStatus.short` → `str` (all 18 statuses); add defaults to all `PlayerStats` / `TeamStats` fields
- `backend/parsers.py` — fix `STAT_TYPE_MAP` keys (`"Passes accurate"`, `"expected_goals"`); null-safe `parse_players`
- `backend/services/match_state.py` — skip `"Missed Penalty"` events, attribute `"Own Goal"` to opponent (BOTH score reconciliation AND goals section text), fix penalty text, expand `PERIOD_NAMES` with all 18 statuses
- `backend/services/milestones.py` — momento 6 on `{"FT","AET","PEN"}`; expand guards for 4-5; expand `PERIOD_NAMES`
- `backend/mock_data/fixture.json` — `short: "PEN"` (was `"FT", elapsed: 120`)
- `backend/mock_data/statistics_*.json` (6 files) — correct stat keys
- `backend/mock_data/players_*.json` (6 files) — add nulls on substitutes
- Tests: `test_models`, `test_parsers`, `test_match_state`, `test_milestones`, `test_data_source` (fixture.json status change may break assertions)

### Out of Scope
- `backend/data_source.py`, `backend/config.py` — no changes
- `backend/services/api_football.py` — no changes (see xG limitation note below)
- Change 3 (backend-api), n8n workflows

### xG Limitation (accepted)
The official API documentation lists 16 available statistics in the default (no `half` parameter) response: Shots on Goal, Shots off Goal, Shots insidebox, Shots outsidebox, Total Shots, Blocked Shots, Fouls, Corner Kicks, Offsides, Ball Possession, Yellow Cards, Red Cards, Goalkeeper Saves, Total passes, Passes accurate, Passes %.

`expected_goals` only appears when the `half=true` query parameter is sent, and only for data from the 2024 season onward. Since `APIFootballClient.fetch_statistics()` does NOT send `half=true`, `expected_goals` will NOT be present in live responses for most fixtures.

**Decision**: Fix the `STAT_TYPE_MAP` key to `"expected_goals"` anyway (so the parser is prepared if the API ever includes it), but accept that the xG line in context text will show empty values in live mode without `half=true`. When xG is needed in production, a future change can add `half=true` to `fetch_statistics` — that change is out of scope here.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `match-data-models`: `FixtureStatus.short` accepts all 18 statuses; all `PlayerStats` / `TeamStats` fields default to `""` / `0`
- `api-football-parsing`: `STAT_TYPE_MAP` matches `"Passes accurate"` + `"expected_goals"`; `parse_players` null-safe end-to-end
- `match-state-manager`: score reconciliation skips missed penalties and flips team for own goals; context text filters missed penalties from goals section AND flips own goals to opposing team's goals section; `(pen X')` formatting excludes missed penalties; `PERIOD_NAMES` covers all 18 statuses with defined Spanish labels (see mapping below)
- `milestone-detector`: momento 6 trigger is `short in ("FT","AET","PEN")`; status guards for momentos 4-5 widened with `ET`, `BT`, `P`, `AET`, `PEN`; `PERIOD_NAMES` covers all 18 statuses (shared with match-state-manager)

## Approach

Bundle all 9 fixes — they share one root cause (API compatibility) and the same files. No new files; no new dependencies. The parsing boundary stays the single seam (Change 1's `MockDataSource` and live both call `parse_*`), so updating parser + mocks together keeps mock and live symmetric.

> **CONFIG RULE FLAG**: This change alters the 6-milestone trigger matrix. Momento 6 now fires on `AET` / `PEN`; status guards for momentos 4-5 widened with extra-time and penalty statuses.

### PERIOD_NAMES — Complete mapping (18 statuses)

The `PERIOD_NAMES` constant in `match_state.py` MUST be updated to cover all 18 API-Football v3 statuses with these exact Spanish labels:

| API `short` | Spanish label |
|-------------|---------------|
| `TBD` | `Horario a confirmar` |
| `NS` | `No iniciado` |
| `1H` | `1er Tiempo` |
| `HT` | `Entretiempo` |
| `2H` | `2do Tiempo` |
| `ET` | `Tiempo extra` |
| `BT` | `Descanso tiempo extra` |
| `P` | `Penales en curso` |
| `SUSP` | `Suspendido` |
| `INT` | `Interrumpido` |
| `FT` | `Final` |
| `AET` | `Final (tiempo extra)` |
| `PEN` | `Final (penales)` |
| `PST` | `Postergado` |
| `CANC` | `Cancelado` |
| `ABD` | `Abandonado` |
| `AWD` | `Perdida por regla` |
| `WO` | `Ganado por ausencia` |
| `LIVE` | `En curso` |

The fallback for any unknown status is the raw `short` value (existing behavior).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/models.py` | Modified | Literal → str, add defaults |
| `backend/parsers.py` | Modified | Map keys, null safety |
| `backend/services/match_state.py` | Modified | Score recon, context text, PERIOD_NAMES |
| `backend/services/milestones.py` | Modified | Triggers, PERIOD_NAMES |
| `backend/mock_data/*.json` (13 files) | Modified | Keys, status, nulls |
| `backend/tests/test_*.py` | Modified | Cover 9 fixes |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Context-text snapshot test breaks | High | Regenerate snapshot (not patch) — missed-penalty filter + own-goal flip changes byte-level output |
| `PlayerStats` default change breaks existing tests | Med | `_safe_int` / `_safe_str` already exists; update test fixtures |
| Mock JSON drift | Low | Update parser and mocks atomically in the same change |
| `fixture.json` status change (`FT` → `PEN`) breaks `test_data_source.py` assertions | High | Explicitly audit and update any test that asserts `status.short == "FT"` or `status.elapsed == 120` from fixture.json |
| Own Goal appears in wrong team's goals section | Med | `_goals_section` must flip Own Goal events to opposing team (same logic as score reconciliation), not just filter by `event.team` |
| xG not available in live mode without `half=true` | Accepted | `STAT_TYPE_MAP` key fixed; xG shows empty in live mode. Future change can add `half=true` to `fetch_statistics` |

## Rollback Plan

`git revert` the merge commit. All changes are modifications to existing files — no schema migration, no external system impact. Mock mode continues to work (reverts to pre-fix state with old keys but functional mocks).

## Dependencies

- Depends on changes 1 and 2 (complete)
- Enables change 3 (backend-api) — fixed models will be serialized by the HTTP endpoints
- No new external dependencies

## Success Criteria

- [ ] `cd backend && pytest` passes with ≥70% coverage (ALL 163+ tests, including test_data_source.py)
- [ ] `FixtureStatus(short="NS")` and `FixtureStatus(short="AET")` validate without error
- [ ] `PlayerStats` accepts null fields end-to-end via the parser (verified with a dict containing null goals, assists, duels, rating)
- [ ] `STAT_TYPE_MAP` maps `"Passes accurate"` and `"expected_goals"`
- [ ] Score reconciliation skips "Missed Penalty" events
- [ ] Score reconciliation attributes "Own Goal" to opposing team
- [ ] Context text goals section: Own Goal appears under the BENEFITED team, not the team that scored it
- [ ] Context text goals section: "Missed Penalty" events are excluded entirely
- [ ] Context text `(pen X')` formatting excludes "Missed Penalty"
- [ ] Momento 6 fires on `{"FT", "AET", "PEN"}`
- [ ] `PERIOD_NAMES` covers all 18 API statuses with the exact Spanish labels from the mapping table
- [ ] Mock `fixture.json` has `short: "PEN"`
- [ ] All `statistics_*.json` use correct API keys (`"Passes accurate"`, `"expected_goals"`)
- [ ] At least one mock player has null fields (rating, goals, duels)
- [ ] `test_data_source.py` updated if any assertions depend on `fixture.json` status being "FT"
- [ ] Context text snapshot test regenerated with correct output (not patched)
