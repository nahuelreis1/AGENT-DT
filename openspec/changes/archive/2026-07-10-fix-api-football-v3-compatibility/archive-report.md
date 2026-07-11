# Archive Report — `fix-api-football-v3-compatibility`

**Change**: `fix-api-football-v3-compatibility`
**Archived to**: `openspec/changes/archive/2026-07-10-fix-api-football-v3-compatibility/`
**Archive date**: 2026-07-10
**Mode**: hybrid (openspec + engram)
**Verdict**: PASS

---

## Executive Summary

The `fix-api-football-v3-compatibility` change is **complete, verified, and archived**. It delivers 9 API compatibility fixes that align the parser, models, and services with the real API-Football v3 schema so the first live request succeeds. All 200 tests pass at 99.59% coverage. The 5 main specs (match-data-models, api-football-parsing, match-state-manager, milestone-detector, context-text-format) now reflect the post-fix contract and become the source of truth for the rest of the SDD pipeline (notably change 3 — `backend-api`).

---

## Test Results

| Metric | Value | Threshold | Status |
|---|---|---|---|
| Total tests | 200 | — | — |
| Passing | 200 | — | ✅ |
| Failing | 0 | 0 | ✅ |
| Coverage | 99.59% | ≥ 70% | ✅ |
| Strict TDD | active | — | ✅ |
| Runtime | 10.70s | — | — |

**Coverage by source file** (relevant to this change):

| File | Cover |
|---|---|
| `models.py` | 100% |
| `parsers.py` | 100% |
| `services/match_state.py` | 99% |
| `services/milestones.py` | 100% |
| `services/api_football.py` | 100% |
| `data_source.py` | 100% |

---

## Summary of Changes (9 Fixes)

| # | Severity | Area | Fix |
|---|---|---|---|
| 1 | CRITICAL | `models.py` | `FixtureStatus.short: str = Field(min_length=1)` (was `Literal["1H","HT","2H","FT"]`) |
| 2 | CRITICAL | `models.py` / `parsers.py` | `PlayerStats` / `TeamStats` defaults on ALL fields except `name`/`position`; `parse_players` null-safe end-to-end |
| 3 | CRITICAL | `parsers.py` | `STAT_TYPE_MAP` keys: `"Passes accurate"`, `"expected_goals"` (was Title Case) |
| 4 | MODERATE | `services/match_state.py` | Score reconciliation skips "Missed Penalty" events |
| 5 | MODERATE | `services/match_state.py` | Score reconciliation attributes "Own Goal" to opposing (BENEFITED) team |
| 6 | MODERATE | `services/match_state.py` | Goals section: Own Goal flipped with `(og X')`; "Missed Penalty" excluded; `(pen X')` only for scored penalties |
| 7 | MODERATE | `services/milestones.py` | Momento 6 trigger widened to `{"FT","AET","PEN"}`; momentos 4-5 guards widened with `ET, BT, P, AET, PEN` |
| 8 | LOW | `mock_data/fixture.json` | `short: "PEN"` (was `"FT"`) |
| 9 | LOW | `mock_data/statistics_*.json` (×6) + `players_*.json` (×6) | Correct stat keys + nulls on substitutes |

---

## Spec Sync Summary

**5 MODIFIED, 0 ADDED, 0 REMOVED** — all delta specs merged into the existing main specs.

| Domain | Action | Requirements Modified | New Scenarios Added |
|--------|--------|----------------------|---------------------|
| `match-data-models` | MODIFIED | `FixtureStatus and TeamScore`; `PlayerStats and TeamStats` | 5 (NS, AET, all-19-statuses, PlayerStats defaults, TeamStats defaults) |
| `api-football-parsing` | MODIFIED | `parse_statistics`; `parse_players` | 3 ("Passes accurate" maps, "expected_goals" maps, player null defaults) |
| `match-state-manager` | MODIFIED | `Detail Update and Score Reconciliation`; `Context Text Format` | 7 (Missed Penalty, Own Goal flipped, snapshot, AET/PEN headers, unknown fallback, GOLES Own Goal flip, GOLES Missed excluded, scored/Missed penalty format) |
| `milestone-detector` | MODIFIED | `Trigger Matrix with Status Guards` | 4 (momento 6 on AET, momento 6 on PEN, momento 4 on ET, momento 5 on ET) |
| `context-text-format` | MODIFIED | `Header`; `Goals` | 4 (AET header, PEN header, unknown fallback, Own Goal flip, Missed Penalty excluded, mixed penalty types) |

### Destructive Delta Notice (per `rules.archive` in `config.yaml`)

**`match-data-models` MODIFIED `FixtureStatus and TeamScore`** removes the `Literal[...]` constraint on `FixtureStatus.short` and replaces it with `str = Field(min_length=1)`. This is destructive in the sense that the old explicit allow-list (4 statuses: `1H`, `HT`, `2H`, `FT`) is gone; the new constraint accepts any non-empty string. **This is the intended fix** for Fix #1 (CRITICAL: Literal crashed on live API responses). All downstream code (match-state-manager, milestone-detector) already handles the full status set; the broadened constraint is matched by the wider interpretation logic added in this change. The 5 previously-uncovered scenarios (NS, AET, all-19-statuses) now have explicit coverage.

The destructive delta was anticipated by the proposal (line 18: "Previously: `short` was restricted to `Literal["1H","HT","2H","FT"]` — too narrow, crashed on live API responses for extra-time / penalty / not-started statuses") and approved during proposal review.

---

## Verify Verdict

**PASS** — full report at `verify-report.md` in the archive folder.

- ✅ All 9 fixes present in implementation, evidenced by source + passing tests
- ✅ All 16 success criteria from proposal satisfied
- ✅ All 10 design decisions implemented faithfully
- ✅ All 48 spec scenarios covered by passing tests (0 untested scenarios)
- ✅ Runtime evidence: 200/200 tests pass at 99.59% coverage
- ✅ API documentation cross-check confirmed (19 statuses, exact stat key spellings, 4 event types handled)
- ✅ No CRITICAL issues, no WARNING issues

### Suggestions from Verify (non-blocking)

1. **`test_data_source.py::statistics_payload`** (lines 125-126) still uses outdated Title Case keys (`"Passes Accurate"`, `"Expected Goals"`). Cosmetic — does not break any test, but inconsistent with the live API shape it claims to model. Recommended: update to `"Passes accurate"` and `"expected_goals"` for consistency with `test_parsers.py::make_team_statistics` (which was correctly updated per task 2.1).

2. **Proposal text vs. reality: "18 statuses" should be "19"**. The proposal's narrative says "18 statuses" in two places, but the proposal's own mapping table has 19 entries (including `LIVE`), the implementation has 19 keys, the test asserts 19, and the API spec lists 19. This is documentation drift, not a code issue. Recommended for a future revision: update proposal wording to "19".

---

## Archive Contents

```
openspec/changes/archive/2026-07-10-fix-api-football-v3-compatibility/
├── archive-report.md    (this file)
├── proposal.md          ✅
├── design.md            ✅
├── tasks.md             ✅ (6/6 phases, 13/13 tasks complete)
├── verify-report.md     ✅ (PASS)
└── specs/               ✅ (5 delta spec files preserved)
    ├── match-data-models/spec.md
    ├── api-football-parsing/spec.md
    ├── match-state-manager/spec.md
    ├── milestone-detector/spec.md
    └── context-text-format/spec.md
```

---

## Source of Truth Updated

The following main specs now reflect the post-fix behavior:

- `openspec/specs/match-data-models/spec.md` — `short` is `str`, PlayerStats/TeamStats have defaults
- `openspec/specs/api-football-parsing/spec.md` — `STAT_TYPE_MAP` uses API spellings, `parse_players` null-safe
- `openspec/specs/match-state-manager/spec.md` — score recon + goals section share helper, 19-key `PERIOD_NAMES`
- `openspec/specs/milestone-detector/spec.md` — momento 6 = `{"FT","AET","PEN"}`, widened guards 4-5
- `openspec/specs/context-text-format/spec.md` — header period mapping 19 keys, GOLES flipped own goals + excluded Missed Penalty

---

## Persistence Artifacts

- This report: `openspec/changes/archive/2026-07-10-fix-api-football-v3-compatibility/archive-report.md`
- Engram: `topic_key: sdd/fix-api-football-v3-compatibility/archive-report` (type: architecture, capture_prompt: false)

---

## Lineage

- **Depends on**: `backend-foundation` (change 1, archived 2026-07-09), `backend-services` (change 2, archived 2026-07-10)
- **Enables**: `backend-api` (change 3) — fixed models will be serialized by the HTTP endpoints
- **Commits**: 5 work-unit commits (`fix(models)`, `fix(parsers)`, `fix(match_state)`, `fix(milestones)`, `fix(mock-data)`)
- **Lines changed**: ~350 (4 source + 13 mocks + 5 test files)
- **PR strategy**: single PR (under 400-line review budget)

---

## Next Change Enabled

**`backend-api` (change 3)** — now that the models, parsers, and services are aligned with API-Football v3 and the goal-scoring / context-text logic is correct, the HTTP API can safely serialize the fixed models. This change was waiting on this archive.

---

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived. Ready for `backend-api` (change 3).
