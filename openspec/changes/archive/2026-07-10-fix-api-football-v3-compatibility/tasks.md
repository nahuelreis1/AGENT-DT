# Tasks: Fix API-Football v3 Compatibility

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~350 (4 src + 13 mocks + 5 test files) |
| 400-line budget risk | Medium (close to budget) |
| Chained PRs recommended | No (single PR fits) |
| Suggested split | Single PR |
| Delivery strategy | ask-always |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: stacked-to-main
400-line budget risk: Medium

## Phase 1: Match Data Models (TDD)

- [x] 1.1 RED — In `backend/tests/test_models.py` add `test_all_18_api_statuses_accepted` parametrized over the full 18-status set; add `test_playerstats_with_all_default_values_is_valid` and `test_teamstats_with_all_default_values_is_valid`; remove `test_unknown_short_value_is_rejected`
- [x] 1.2 GREEN — In `backend/models.py` change `FixtureStatus.short` from `Literal[...]` to `str = Field(min_length=1)`; add default values (`0` / `""` / `False`) to every `PlayerStats` and `TeamStats` field except `name` and `position`
- [x] 1.3 Run `cd backend && pytest tests/test_models.py` — all pass

## Phase 2: API-Football Parsing (TDD)

- [x] 2.1 RED — In `backend/tests/test_parsers.py` add `test_player_with_all_null_stats_parses_to_defaults`; fix `make_team_statistics` / `statistics_payload` fixtures to use `"Passes accurate"` and `"expected_goals"`
- [x] 2.2 GREEN — In `backend/parsers.py` change `STAT_TYPE_MAP` keys `"Passes Accurate"`→`"Passes accurate"` and `"Expected Goals"`→`"expected_goals"`; rewrite `parse_players` to use `.get()` + `_safe_int` / `_safe_str` on every field
- [x] 2.3 Run `cd backend && pytest tests/test_parsers.py` — all pass

## Phase 3: Match State Manager (TDD)

- [x] 3.1 RED — In `backend/tests/test_match_state.py` update `test_period_names_constant_is_exported` to assert 19 keys (table has 19 entries, not 18 as the proposal text states); add `test_missed_penalty_does_not_increment_score`, `test_own_goal_counts_for_opponent`, `test_goals_section_own_goal_under_benefited_team`, `test_goals_section_missed_penalty_excluded`, `test_scored_penalty_formatted_missed_not`, `test_status_AET_renders_Final_tiempo_extra`, `test_status_PEN_renders_Final_penales`, `test_status_NS_renders_No_iniciado`, `test_header_unknown_status_falls_back_to_raw_short`
- [x] 3.2 GREEN — In `backend/services/match_state.py` expand `PERIOD_NAMES` to 19 entries per proposal mapping; add `_is_actual_goal()` and `_goals_for_team()` helpers; rewrite `update_details` score loop via helper; rewrite `_goals_section` to flip Own Goals + exclude Missed; add `(og X')` formatting
- [x] 3.3 Re-run snapshot test minute-67 — output IDENTICAL (no Own/Missed in snapshot events) — no regeneration needed
- [x] 3.4 Run `cd backend && pytest tests/test_match_state.py` — all pass

## Phase 4: Milestone Detector (TDD)

- [x] 4.1 RED — In `backend/tests/test_milestones.py` add `test_trigger_6_fires_on_AET`, `test_trigger_6_fires_on_PEN`, `test_trigger_4_fires_during_ET`, `test_trigger_5_fires_during_ET`
- [x] 4.2 GREEN — In `backend/services/milestones.py` update `TRIGGER_MATRIX`: momento 6 = `{"FT","AET","PEN"}`; widen momentos 4-5 guards to include `ET, BT, P, AET, PEN`
- [x] 4.3 Run `cd backend && pytest tests/test_milestones.py` — all pass

## Phase 5: Mock Data Updates

- [x] 5.1 Edit `backend/mock_data/fixture.json` — set `short: "PEN"`, `long: "Match Finished After Penalty"` (elapsed stays 120)
- [x] 5.2 Edit 6 files `backend/mock_data/statistics_*.json` — rename key `"Passes Accurate"`→`"Passes accurate"` and `"Expected Goals"`→`"expected_goals"`
- [x] 5.3 Edit 6 files `backend/mock_data/players_*.json` — add `null` for `rating`, `goals.total`, `goals.assists`, `duels.total`, `duels.won` on 2 substitute players per team (4 subs per file total)

## Phase 6: Audit & Full Suite

- [x] 6.1 Audit `backend/tests/test_data_source.py` — confirmed no assertion depends on `fixture.json` `short == "FT"`; no test changes needed
- [x] 6.2 Run `cd backend && pytest` — all 200 tests pass (163 → 200), coverage 99.59% (well above 70%)
- [x] 6.3 Committed in 5 work-unit commits: `fix(models)`, `fix(parsers)`, `fix(match_state)`, `fix(milestones)`, `fix(mock-data)`
