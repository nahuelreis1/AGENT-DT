# Design: Fix API-Football v3 Compatibility

## Technical Approach

Bundle 9 fixes across the parsing boundary + downstream services + mock fixtures. Parsers stay the single seam (change 1 invariant). One new shared helper (`_goals_for_team`) extracts the Own-Goal-flip + Missed-Penalty-filter logic so `update_details` (score reconciliation) and `_goals_section` (context text) cannot drift. Strict TDD: every change has a failing test FIRST, then the code change, then green. No new files, no new dependencies, no migrations.

## Architecture Decisions

| Decision | Options considered | Choice | Rationale |
|---|---|---|---|
| Own-Goal flip + Missed filter scope | Inline in two places vs shared helper | **Shared helper `_goals_for_team`** (proposal) | Prevents logic drift between score recon and goals section text. `update_details` calls `len(_goals_for_team(...))`; `_goals_section` uses the list for rendering. |
| `FixtureStatus.short` typing | Keep `Literal` vs `str` | **`str = Field(min_length=1)`** | Live API emits 18 statuses; Literal would crash on first live call. Downstream services own per-status interpretation. |
| `PlayerStats` / `TeamStats` defaults | Required vs default `0`/`""` | **Defaults on ALL fields except `name`/`position`** (player) and `name` (team) | Live API sends nulls for substitutes; required fields crash the parser. `name` and `position` always present per API schema. |
| `STAT_TYPE_MAP` keys | Keep Title Case vs match API | **Exact API spelling**: `"Passes accurate"`, `"expected_goals"` | API uses lowercase snake_case for these two; keys must match byte-for-byte. |
| `parse_players` null-safety | Dict access vs `.get()` + helpers | **`.get()` + `_safe_int`/`_safe_str` on ALL fields** | Live API sends `null` for many stats on substitutes; direct access raises `KeyError`. |
| `PERIOD_NAMES` content | 4 keys vs 18 keys | **All 18 statuses with exact Spanish labels from proposal** | Live API emits 18; unknown falls back to raw `short` (existing behavior). |
| Momento 6 trigger | `FT` only vs `FT`/`AET`/`PEN` | **`{"FT", "AET", "PEN"}`** | Live matches that go to ET / penalties would otherwise skip the final webhook. |
| Momentos 4-5 guards | `(HT, 2H, FT)` vs widened | **`(HT, 2H, ET, BT, P, AET, PEN, FT)`** (4) / **`(2H, ET, BT, P, AET, PEN, FT)`** (5) | Extra-time matches must continue triggering. |
| Snapshot test at minute 67 | Patch expected string vs regenerate | **Regenerate by re-running** | Per `work-unit-commits` rule. Snapshot hand-crafted events contain NO Own Goals or Missed Penalties → byte-level output is IDENTICAL. Re-run to verify; only update if output differs. |
| `events_*.json` schema | Add fake Own Goal/Missed Penalty events vs leave | **Leave as-is** | Spec covers behavior; mock data exercises it. Snapshot in `test_match_state.py` uses hand-crafted `MatchEvent` objects, not mocks. New unit tests directly construct events with the new details. |

## Data Flow

```
Polling tick
  → LiveDataSource (unchanged)
  → parse_fixture / parse_statistics / parse_players / parse_events
  → MatchStateManager.update_details
  → _goals_for_team(home, away)  ←── single source of truth
       ├── len() → home.goals, away.goals
       └── list  → _goals_section  → _fmt  → "(pen X')" / "(og X')" / "(X')"
  → get_context_text() → 7-section string → n8n webhook
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/models.py` | Modify | `FixtureStatus.short: str = Field(min_length=1)`; defaults on all `PlayerStats`/`TeamStats` fields (see proposal) |
| `backend/parsers.py` | Modify | `STAT_TYPE_MAP`: `"Passes Accurate"`→`"Passes accurate"`, `"Expected Goals"`→`"expected_goals"`; `parse_players` uses `.get()` + helpers on every field |
| `backend/services/match_state.py` | Modify | `PERIOD_NAMES` → 18 entries; add `_goals_for_team()` + `_is_actual_goal()`; rewrite `_goals_section` to flip Own Goals + exclude Missed; rewrite `update_details` score loop via shared helper; add `(og X')` formatting |
| `backend/services/milestones.py` | Modify | `TRIGGER_MATRIX`: momento 6 = `{"FT","AET","PEN"}`; widen guards for 4-5 with `ET`/`BT`/`P`/`AET`/`PEN` |
| `backend/mock_data/fixture.json` | Modify | `short: "PEN"`, `long: "Match Finished After Penalty"`, `elapsed: 120` (unchanged) |
| `backend/mock_data/statistics_*.json` (×6) | Modify | `Passes Accurate`→`Passes accurate`; `Expected Goals`→`expected_goals` |
| `backend/mock_data/players_*.json` (×6) | Modify | 2-3 substitute players per team: `rating: null`, `goals.total: null`, `assists: null`, `duels.total: null`, `duels.won: null` |
| `backend/tests/test_models.py` | Modify | Remove `test_unknown_short_value_is_rejected`; add `test_all_18_api_statuses_accepted`; add default-construction tests |
| `backend/tests/test_parsers.py` | Modify | `make_team_statistics` / `statistics_payload`: fix 2 keys; add `test_player_with_all_null_stats_parses_to_defaults` |
| `backend/tests/test_match_state.py` | Modify | Update `test_period_names_constant_is_exported` (18 keys); add Missed Penalty/Own Goal scenarios; **re-run snapshot, verify identical, only update if different** |
| `backend/tests/test_milestones.py` | Modify | Add `test_trigger_6_fires_on_AET`, `test_trigger_6_fires_on_PEN`, `test_trigger_4_fires_during_ET`, `test_trigger_5_fires_during_ET` |
| `backend/tests/test_data_source.py` | Audit | No assertion checks `fixture.json short == "FT"` directly; all tests use the parsed `MatchState` and only assert structural fields. **No changes expected.** Confirm in PR review. |

## Interfaces / Contracts

```python
# backend/services/match_state.py — new shared helper
def _is_actual_goal(event: MatchEvent) -> bool:
    return event.type == "Goal" and "Missed" not in event.detail

def _goals_for_team(
    events: list[MatchEvent], team_name: str, opponent_name: str,
) -> list[MatchEvent]:
    """Filter Goal events for a team, flipping Own Goals to opponent,
    excluding Missed Penalties. Shared by score recon and context text."""
    goals: list[MatchEvent] = []
    for e in events:
        if not _is_actual_goal(e):
            continue
        if "Own Goal" in e.detail:
            if e.team == opponent_name:
                goals.append(e)  # opponent's own goal → benefits us
        elif e.team == team_name:
            goals.append(e)
    return goals
```

`update_details` score loop: `self._state.home.goals = len(_goals_for_team(events, home, away))`; symmetric for away. `_goals_section` calls the same helper, then formats each with `(pen X')` / `(og X')` / `(X')`.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit (models) | `short` accepts all 18, defaults on stats | Parametrize over 18 statuses; `PlayerStats(name="x")` constructs with all defaults |
| Unit (parsers) | `STAT_TYPE_MAP` exact keys, null players | Construct stat entries + players with null fields; assert defaults |
| Unit (match_state) | PERIOD_NAMES 18 keys, Missed skipped, Own Goal flipped, `(og X')` format, score recon | Direct `MatchEvent` construction; no mocks |
| Snapshot | Minute-67 byte-pinned | Re-run; output MUST be identical (no Own/Missed in snapshot events). If different, investigate — do NOT patch |
| Unit (milestones) | Momento 6 on AET/PEN, 4-5 on ET | respx-mocked webhook, hand-crafted `MatchState` |
| Audit (data_source) | `fixture.json` status change | Confirm no test asserts `status.short == "FT"` from `fixture.json`. Existing tests assert structural fields only — should pass unchanged |

## Migration / Rollout

No migration. All changes are in-memory models, JSON fixtures, and pure parsers. Rollback = `git revert`; mock mode returns to pre-fix state with old keys (functional but parser drops `pass_accuracy` and `expected_goals` — accepted degradation).

## Open Questions

- None. The revised proposal fixes all 4 prior gaps (PERIOD_NAMES completeness, Momento 6 trigger set, shared goal helper, snapshot regen plan).
