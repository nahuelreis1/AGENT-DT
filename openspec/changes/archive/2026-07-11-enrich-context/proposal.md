# Proposal: Enrich Context (7 to 9 sections, full data utilization)

## Intent

`get_context_text()` uses ~30% of available data: 3/10 TeamStats fields, 4/19 PlayerStats fields for 5/22 players, lineups never fetched. DeepSeek needs full tactical context for quality commentary.

## Scope

### In Scope
- FORMACIONES section (new) — formation strings from lineups endpoint
- Extend ESTADÍSTICAS — add total_shots, corners, fouls, offsides, pass_accuracy, yellow_cards, red_cards (all 10 fields)
- Enrich JUGADORES DESTACADOS/FLOJOS — all 19 PlayerStats fields per player
- TODOS LOS JUGADORES section (new) — all 22 starters, compact stats, grouped by team with formation prefix
- `fetch_lineups()` on APIFootballClient; `get_lineups()` on DataSource Protocol
- LineupTeam, LineupPlayer models; MatchState gains home_lineup/away_lineup
- `parse_lineups()` parser (trusts input order; (None, None) on empty)
- `backend/mock_data/lineups.json` (Argentina 4-3-3, Netherlands 3-4-1-2, fixture 868019)
- Lifespan fetches lineups on startup

### Out of Scope
- Lineup grid positions (`X:Y`) — parsed, not surfaced (future)
- Re-fetch lineups on substitution events (deferred)

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `context-text-format`: 7 -> 9 sections, enriched stats, all-players block
- `match-state-manager`: update_lineups, new section builders
- `match-data-models`: LineupTeam, LineupPlayer, MatchState fields
- `api-football-parsing`: parse_lineups
- `api-football-client`: fetch_lineups
- `data-source-strategy`: get_lineups on Protocol

## Approach

Additive (Approach A). New sections/fields APPENDED — existing 7 keep format. Lineups fetched once at startup; `parse_lineups` returns `(None, None)` on 204, FORMACIONES falls back. Context ~3-5KB vs ~500B — trivial for DeepSeek 64k window.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/models.py` | Modified | LineupTeam, LineupPlayer, MatchState fields |
| `backend/parsers.py` | Modified | parse_lineups() |
| `backend/services/api_football.py` | Modified | fetch_lineups() |
| `backend/services/match_state.py` | Modified | update_lineups, new sections, enriched stats |
| `backend/data_source.py` | Modified | get_lineups() on Protocol + impls |
| `backend/mock_data/lineups.json` | New | ARG 4-3-3, NED 3-4-1-2 |
| `backend/app.py` | Modified | Lifespan lineups fetch |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| ~53 refs to get_context_text break | High | Expected — snapshot updates |
| Token budget ~3-5KB | Low | DeepSeek 64k window trivial |
| Lineups 204 pre-kickoff | Med | (None, None); fallback text |
| API quota 1-3 calls/day | Low | Within 100/day |

## Rollback Plan

`git revert` — no migration, no external systems. 7-section format returns. 6 milestone triggers unchanged.

## Dependencies

- API-Football `/fixtures/lineups` (20-40 min before kickoff)

## Success Criteria

- [ ] get_context_text emits 9 sections in fixed order
- [ ] All 10 TeamStats fields in ESTADÍSTICAS
- [ ] All 22 players in TODOS LOS JUGADORES
- [ ] Lineups fetched on startup; 204 handled gracefully
- [ ] Coverage >= 70%; tests updated
