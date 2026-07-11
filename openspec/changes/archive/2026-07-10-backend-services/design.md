# Design: Backend Services

## Technical Approach

Three services fill the gap between change 1's data layer and change 3's HTTP API. `APIFootballClient` is an async `httpx` wrapper with auth header, request counter, and 80/100-call warnings. `LiveDataSource` (modified) wires that client into the existing `parse_*` functions — parser-path invariant stays structural. `MatchStateManager` owns the in-memory `MatchState`, recomputes the score from cumulative Goal events, and emits the 7-section context text per `context-text-format`. `MilestoneDetector` walks a 6-row trigger matrix, fetches details BEFORE updating state, and POSTs a fixed-shape payload to n8n — log-and-continue on failure, mark-fired even on error.

## Architecture Decisions

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | State holder | Plain `MatchStateManager` (no singleton) | One instance per process in lifespan (change 3); testable without env. |
| 2 | Score source of truth | Recompute from `Goal` events in `update_details` (Option A) | API `goals` is incremental, events cumulative. One ground truth. |
| 3 | Live source DI | `LiveDataSource(client, fixture_id)` — injected, no client ownership | Factory controls client lifecycle; `aclose()` in one place. |
| 4 | `request_count` timing | Increment BEFORE the HTTP call | Timeout still counts against 100/day free-tier budget. |
| 5 | `fetch_fixture` return | `dict` (response[0]) | One fixture per id; `{}` on empty keeps parser call simple. |
| 6 | `MilestoneDetector` HTTP | Owns client unless injected | Production owns (one pool), tests inject (`respx.MockRouter`). |
| 7 | Trigger matrix | `list[tuple[int, callable, callable]]` | Ordered iteration, declarative, every lambda unit-testable. |
| 8 | Fetch details timing | BEFORE `update_details` | `context_text` reflects momento snapshot, not stale prior. |
| 9 | Mark fired on POST fail | Yes (no retry) | Polling runs every 90s — same milestone re-fires indefinitely. |
| 10 | Empty `n8n_url` | No-op with `log.info`, leave unfired | Mock has no n8n; future tick with n8n can still fire. |
| 11 | POST exception scope | `except Exception` | Catches serialization errors too, not just transport. |
| 12 | Snapshot test | Byte-pinned at min 67, full state | One canonical snapshot per archived spec. |
| 13 | PR split (400-line budget) | PR1: match_state → PR2: api_football + milestones + data_source | Review focus; PR1 is pure logic. |

## Data Flow

### Polling tick (change 3 implements; design here)
```
polling_loop (every POLLING_INTERVAL s, default 90)
  └─→ data_source.get_fixture() → MatchState
  └─→ match_state.update_fixture(MatchState)
  └─→ milestone_detector.check_and_push()
        for m in 1..6 (unfired):
          if condition(state) AND guard(state):
            ev, hs, as_, hp, ap = await data_source.get_details(m)
            match_state.update_details(...)         # score recomputed
            POST {n8n_url}/webhook/momento          # log-and-continue
              {m, context_text, match_state.model_dump('json')}
            _fired[m] = True                        # even on failure
```

### Momento 3 → Momento 6 prediction lineage (THE MAGIC)
```
[HT] Detector fires m=3 → POST n8n/webhook/momento
  n8n AI Agent: HT recommendation (DeepSeek)
  n8n: POST /partido/prediccion {momento:3, content:"..."}    # change 3
    └─→ match_state.save_prediction(3, "...")                  # THIS change
[FT] Detector fires m=6 → POST n8n/webhook/momento
  n8n AI Agent: GET /partido/predicciones → gets m=3 prediction  # change 3
  n8n: compare prediction vs actual → TTS → audio
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/services/__init__.py` | Create | Package marker. |
| `backend/services/api_football.py` | Create | `APIFootballClient`: async httpx, 4 fetches, counter + 80/100 warnings, `aclose()`. |
| `backend/services/match_state.py` | Create | `MatchStateManager`, `PERIOD_NAMES`, 7 section builders, helpers, prediction log. |
| `backend/services/milestones.py` | Create | `TRIGGER_MATRIX` (6 lambdas), `MilestoneDetector` with optional injected client. |
| `backend/data_source.py` | Modify | `LiveDataSource(client, fixture_id)` fills stubs → `parse_*`; factory wires client live. |
| `backend/tests/test_match_state.py` | Create | Unit + snapshot (min 67). |
| `backend/tests/test_api_football.py` | Create | respx for 4 endpoints, counter, warnings, 4xx/5xx/network. |
| `backend/tests/test_milestones.py` | Create | respx for n8n, 6 triggers, no-refire, guards, full-timeline sim. |
| `backend/tests/conftest.py` | Modify | Add `match_state`, `populated_match_state`, `respx_mock`; preserve existing. |
| `openspec/specs/context-text-format/spec.md` | Sync | Pull from archive (no content change). |

## Interfaces (signatures only; types in specs)

```python
class APIFootballClient:
    def __init__(self, api_key, base_url="https://v3.football.api-sports.io/", timeout=10.0)
    request_count: int
    async def fetch_fixture(self, fixture_id) -> dict
    async def fetch_events/fetch_statistics/fetch_players(self, fixture_id) -> list[dict]
    async def aclose(self) -> None

PERIOD_NAMES = {"1H": "1er Tiempo", "HT": "Entretiempo", "2H": "2do Tiempo", "FT": "Final"}
class MatchStateManager:
    def __init__(self) -> None
    def update_fixture(self, state: MatchState) -> None
    def update_details(self, events, hs, as_, hp, ap) -> None  # RuntimeError if uninit
    def get_state(self) -> MatchState                            # RuntimeError if uninit
    def get_context_text(self) -> str
    def save_prediction(self, momento: int, content: str) -> None
    def get_predictions(self) -> list[Prediction]

TRIGGER_MATRIX: list[tuple[int, Callable, Callable]]           # 6 rows
class MilestoneDetector:
    def __init__(self, data_source, match_state, n8n_url, http_client: httpx.AsyncClient | None = None)
    async def check_and_push(self) -> None
    async def aclose(self) -> None                               # no-op if injected

# Webhook: POST {n8n_url}/webhook/momento, timeout=5.0s
# { "momento": int, "context_text": str, "match_state": <MatchState.model_dump('json')> }

class LiveDataSource:                                            # data_source.py MODIFIED
    def __init__(self, client: APIFootballClient, fixture_id: int)
    async def get_fixture(self) -> MatchState
    async def get_details(self, momento: int) -> 5-tuple         # 3 fetches + 3 parsers
def create_data_source(config) -> DataSource                    # live: LiveDataSource(APIFootballClient(key), fixture_id)
```

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | `MatchStateManager`: init, fixture, details, score reconciliation, 7 sections, snapshot min 67, predictions (append, order, out-of-range) | Hand-built state; real mock JSONs for snapshot |
| Unit | `APIFootballClient`: 4 fetches, counter, 80/100 warnings, 4xx→HTTPStatusError, network→RequestError, `aclose`, empty fixture → `{}` | `respx` + `caplog` |
| Unit | `MilestoneDetector`: 6 triggers, guards block, no re-firing, empty url no-op, POST fail → fired+log+continue, full-timeline sim, injected client not closed | `respx` + `MockDataSource` |
| Integration | `LiveDataSource` + `APIFootballClient`: 3 endpoints per `get_details`, piped through `parse_*`, factory live branch | `respx` + real parsers |
| Coverage | ≥70% on `services/` + `data_source.py`; change 1 tests green | `cd backend && pytest` |

## Migration / Rollout

No migration. Rollback = `git revert`. `LiveDataSource` reverts to stub; mock mode unaffected. `_fired` state loss on process restart is a known limitation (re-fires all 6).

## Open Questions

None.
