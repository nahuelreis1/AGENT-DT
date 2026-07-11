# Design: Backend Foundation

## Technical Approach

Greenfield foundation for the AI DT backend: typed config (`pydantic-settings`), 7 Pydantic v2 models, 4 pure-function parsers, and a `DataSource` strategy. The 19 mock JSONs (`fixture.json` + 6 events + 6 statistics + 6 players) replicate the API-Football v3 envelope so `MockDataSource` and (change 2) `LiveDataSource` produce identical Pydantic shapes via the same `parse_*` functions. **Invariant**: parsers are the single seam that knows the API-Football v3 schema; downstream speaks only Pydantic.

## Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Config loader | `pydantic-settings.BaseSettings` | Typed env vars + `model_validator` for live-mode cross-field rules |
| `MatchEvent.type` | `Literal["Goal","Card","subst"]` | No import in parsers; clean `ValidationError` for unknowns |
| `DataSource` shape | `typing.Protocol` (structural) | Duck-typing matches the invariant; trivial test fakes |
| Moment→file map | `MOMENTO_FILE_KEYS: dict[int,str]` constant | Single source of truth, matches spec table |
| Mock file count | 19 (1 + 6×3) not 13 | Spec requires all 6 momentos; ch.2 snapshot test needs full input |
| Unknown events | Silently skipped in `parse_events` | Defensive against live noise (`Var`, `GoalCancelled`) |
| Test runner | `pytest` + `pytest-asyncio` (`asyncio_mode=auto`) | Removes `@pytest.mark.asyncio` boilerplate |
| Mock data path | `Path(__file__).parent / "mock_data"` (module-relative) | CWD-independent — identical path from project root, `backend/`, tests, or VPS deploy dir; hardcoded `Path("backend/mock_data")` breaks per CWD |

## Data Flow

```
mock_data/*.json (19) ─► MockDataSource ─┐
                                          ├─► parse_*() ─► Pydantic ─► MatchState
LiveDataSource (ch.2, same parsers) ──────┘   parsers are the only API-schema-aware code
```

## File Changes

| Path | Action |
|---|---|
| `backend/{__init__,config,models,parsers,data_source}.py` | Create (5 modules) |
| `backend/mock_data/{fixture,events_{15,30,ht,60,75,ft},statistics_{15,30,ht,60,75,ft},players_{15,30,ht,60,75,ft}}.json` | Create 19 files |
| `backend/tests/{conftest,test_config,test_models,test_parsers,test_data_source}.py` | Create (5 modules) |
| `backend/{.env.example,requirements.txt,requirements-dev.txt,pyproject.toml}` | Create config + deps |

`pyproject.toml`: `asyncio_mode=auto`, `testpaths=["tests"]`, cov ≥70%.

## Interfaces

**Models** (`models.py` — per `match-data-models` spec):
- `FixtureStatus(elapsed: int≥0, short: Literal["1H","HT","2H","FT"], long: str min_length=1)`
- `TeamScore(id: int>0, name: str min_length=1, goals: int≥0)`
- `MatchEvent(minute≥0, team, player, type: Literal["Goal","Card","subst"], detail, assist: str|None)`
- `PlayerStats(20 fields, substitute: bool=False)`; `TeamStats` (possession/pass_accuracy/xG stay `str`)
- `MatchState(fixture_id, status, home, away, events, home_stats, away_stats, home_players, away_players, last_updated: datetime=utcnow)`
- `Prediction(momento: int 1..6, timestamp, content)`

**Parsers** (`parsers.py` — non-obvious bits):
```python
STAT_TYPE_MAP = {  # (model_field, is_numeric)
    "Ball Possession": ("possession", False), "Shots on Goal": ("shots_on_goal", True),
    "Total Shots": ("total_shots", True), "Corner Kicks": ("corners", True),
    "Fouls": ("fouls", True), "Offsides": ("offsides", True),
    "Yellow Cards": ("yellow_cards", True), "Red Cards": ("red_cards", True),
    "Passes Accurate": ("pass_accuracy", False), "Expected Goals": ("expected_goals", False),
}

def parse_events(items):
    out = []
    for it in items:
        if it.get("type") not in ("Goal", "Card", "subst"): continue
        m = it["time"]["elapsed"] + (it["time"].get("extra") or 0)
        out.append(MatchEvent(..., assist=(it.get("assist") or {}).get("name")))
    return out
```

**DataSource** (`data_source.py`):
```python
MOMENTO_FILE_KEYS = {1: "15", 2: "30", 3: "ht", 4: "60", 5: "75", 6: "ft"}

class DataSource(Protocol):
    async def get_fixture(self) -> MatchState: ...
    async def get_details(self, m: int) -> tuple[list[MatchEvent], TeamStats|None, TeamStats|None, list[PlayerStats], list[PlayerStats]]: ...

class LiveDataSource:  # change 2 fills these
    async def get_fixture(self): raise NotImplementedError
    async def get_details(self, m): raise NotImplementedError

_MOCK_DATA_DIR = Path(__file__).parent / "mock_data"

def create_data_source(cfg: Settings) -> DataSource:
    return MockDataSource(_MOCK_DATA_DIR) if cfg.MOCK_MODE else LiveDataSource(...)
```

**`MockDataSource._load_json` helper** — the single I/O seam for all 19 mock files:

```python
def _load_json(self, filename: str) -> list[dict]:
    with open(self.mock_dir / filename) as f:
        data = json.load(f)
    if data.get("errors"):  # defensive: mock data should have empty errors
        log.warning("mock %s contains errors: %s", filename, data["errors"])
    return data.get("response") or []  # API-Football v3 envelope: {"response": [...]}
```

| Case | Behavior | Why |
|---|---|---|
| File missing | Raises `FileNotFoundError` | Spec: "MockDataSource raises on missing JSON" (scenario `events_99.json`) |
| `data["errors"]` non-empty | Logs warning, still returns `data["response"]` | Defensive — mock fixtures should have empty errors, but don't fail the load |
| `data["response"]` missing or `null` | Returns `[]` | Lets parsers handle empty input gracefully (empty events/stats/players list) |
| Happy path | Returns `data["response"]` (the array inside the v3 envelope) | Matches API-Football v3 shape so `MockDataSource` and `LiveDataSource` feed identical parsers |

## Testing Strategy

| Layer | What | How |
|---|---|---|
| Unit config | Defaults, `.env` override, int coercion, 3 live-mode reject cases | `monkeypatch.setenv` + `pytest.raises(ValidationError)` |
| Unit models | All field constraints, `Literal` rejects unknowns, `substitute` default, `possession` stays str | Direct model instantiation |
| Unit parsers | Extra time, null assist, null stat defaults, unknown event skipped | Hand-crafted dicts, no file I/O |
| Integration data_source | All 6 momentos return correct snapshot, factory branches, `LiveDataSource` raises, `events_ft.json` has 90+11 equalizer | Reads real `mock_data/*.json` via conftest |
| Snapshot (deferred) | `get_context_text()` output | **Change 2** — mock data prepared here is the input |

## Mock Data Progression (fixture 868019)

| Momento | Score | Events (cumulative) | Notes |
|---|---|---|---|
| 15 | 0-0 | none | ARG 55% pos |
| 30 | 0-0 | none | possession equalizes |
| ht | 1-0 | Molina 35' (assist Messi) | ARG 48% |
| 60 | 2-0 | + Messi pen 40+3' | ARG dominant xG |
| 75 | 2-1 | + Weghorst 73' | HOL comeback |
| ft | 2-2 | + Weghorst 90+11' | Montiel 🟨 78', Lautaro→Paredes 82' |

Ratings evolve: Messi 7.0→8.2, Molina peak 7.8. Only the 6-moment structure is factual; granular stats are illustrative.

## Migration / Rollout

None. Greenfield — rollback = `rm -rf backend/`.

## Seam to Change 2

- `LiveDataSource` interface ready; full impl in change 2
- `MatchState` ready for `MatchStateManager` (`home_stats: TeamStats|None` allows pre-detail state)
- `context-text-format` spec pinned here; change 2 implements `get_context_text()` + snapshot test
- `PERIOD_NAMES` map lives in change 2; webhook payload per momento also documented in change 2 per `config.yaml`

## Open Questions

None. `MOMENTO_FILE_KEYS` mixes string (`"ht"`, `"ft"`) and numeric (`"15"`) keys — asymmetry contained in this single map.
