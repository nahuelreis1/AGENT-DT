# Tasks: Enrich Context (7→9 sections, full data utilization)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~700-800 (8 files + tests + 22-player mock) |
| 400-line budget risk | Medium |
| Chained PRs recommended | No (tight coupling across all layers) |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Medium

## Phase 1: Models Foundation

- [x] 1.1 RED: 4 cases in `backend/tests/test_models.py::test_lineup_models` (grid null→None, grid string preserved, missing coach→None, empty XI valid)
- [x] 1.2 GREEN: Add `LineupPlayer` + `LineupTeam` to `backend/models.py`; add `home_lineup`/`away_lineup` (default `None`) to `MatchState`

## Phase 2: Lineups Parser

- [x] 2.1 RED: 6 cases in `backend/tests/test_parsers.py::test_parse_lineups` (both teams, empty→(None,None), missing coach, null grid, single element, order trust)
- [x] 2.2 GREEN: Implement `parse_lineups(items)` in `backend/parsers.py` using `_safe_int`/`_safe_str`; trust input order [0]=home, [1]=away

## Phase 3: APIFootballClient

- [x] 3.1 RED: 3 respx cases in `backend/tests/test_api_football.py::test_fetch_lineups` (200 list+count++, 204 []+count++, 4xx raises)
- [x] 3.2 GREEN: Add `_get` 204 early-return (`return []` before `resp.json()`) and `fetch_lineups(fixture_id)` to `backend/services/api_football.py`

## Phase 4: DataSource Protocol

- [x] 4.1 RED: 4 cases in `backend/tests/test_data_source.py::test_get_lineups` (mock reads file, missing file→(None,None), live delegates+parses, live empty→(None,None))
- [x] 4.2 GREEN: Add `get_lineups()` to `DataSource` Protocol; impl on `MockDataSource` (`_load_json` + `parse_lineups`) and `LiveDataSource` (`client.fetch_lineups` + `parse_lineups`)

## Phase 5: Mock Data Fixture

- [x] 5.1 Create `backend/mock_data/lineups.json` — v3 envelope, fixture 868019, ARG 4-3-3 (11 + bench, Scaloni), NED 3-4-1-2 (11 + bench, Van Gaal)

## Phase 6: MatchStateManager

- [x] 6.1 RED: 3 cases `test_match_state.py::test_update_lineups` (stores+readable, (None,None) no-op, before fixture raises)
- [x] 6.2 GREEN: Add `update_lineups(home, away)` to `MatchStateManager` in `backend/services/match_state.py`
- [x] 6.3 RED+GREEN: 3 cases + impl `_lineups_section()` (`FORMACIONES: {home} {f1} - {away} {f2}`; fallback `No disponibles aún`)
- [x] 6.4 RED+GREEN: 3 cases + impl `_all_players_section()` (`TODOS LOS JUGADORES:` + per-team group w/ formation prefix; pos G→ARQ, D→DEF, M→MED, F→ATK)
- [x] 6.5 RED+GREEN: 2 cases + extend `_stats_section()` 3→10 lines (POSESIÓN…TARJETAS ROJAS, xG 3rd)
- [x] 6.6 RED+GREEN: 3 cases + enrich `_player_highlights()` w/ 12-field zero-suppression (goals, assists, shots, passes, duels, fouls, cards)
- [x] 6.7 Update `get_context_text()` 7→9: insert `_lineups_section` after header, `_all_players_section` after weak; preserve `\n\n` + trailing `\n`

## Phase 7: Lifespan Integration

- [x] 7.1 RED: 2 cases in `backend/tests/test_main.py::test_lifespan_lineups` (lineups fetched on startup, (None,None) no-op)
- [x] 7.2 GREEN: In `backend/main.py` lifespan, after `update_fixture`, before `yield`: call `data_source.get_lineups()` + `match_state.update_lineups()`

## Phase 8: Verification & Regression

- [x] 8.1 Update snapshot `backend/tests/test_match_state.py::test_get_context_text_snapshot` — pin 9-section output, byte-stable at min length 67 with lineups
- [x] 8.2 Update section-count assertions 7→9 and stat-line assertions across affected test files
- [x] 8.3 Run `cd backend && pytest` — all green, coverage ≥ 70% per `config.yaml` `verify.coverage_threshold: 70`
