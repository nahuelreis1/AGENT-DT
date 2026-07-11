# match-state-manager Specification

## Purpose

In-memory holder for the live `MatchState` and the `Prediction` log. Owns the lifecycle methods the polling loop calls, recomputes the score from Goal events (overriding the API's incremental value), and produces the 7-section context text consumed by the n8n AI Agent prompts. Mode-agnostic — the same class backs mock and live data sources.

## Requirements

### Requirement: Construction and Fixture Update

`MatchStateManager` MUST take no constructor arguments. `update_fixture(match_state: MatchState) -> None` MUST store the supplied `MatchState` (overwriting any prior state, including the events list, stats, and players — `update_fixture` is a "snapshot" update). `get_state() -> MatchState` MUST return the stored state or raise `RuntimeError` if `update_fixture()` was never called.

#### Scenario: Uninitialized state raises on get_state

- GIVEN a freshly constructed `MatchStateManager()`
- WHEN `get_state()` is called
- THEN a `RuntimeError` is raised

#### Scenario: Fixture update makes state readable

- GIVEN a `MatchState` with `fixture_id=868019`, `home.goals=0`, `away.goals=0`, `status.short="1H"`
- WHEN `update_fixture(state)` is called
- THEN `get_state().fixture_id == 868019`
- AND `get_state().status.short == "1H"`

### Requirement: Detail Update and Score Reconciliation

`update_details(events, home_stats, away_stats, home_players, away_players) -> None` MUST replace the stored `events`, `home_stats`, `away_stats`, `home_players`, and `away_players` with the supplied values. It MUST THEN recompute `home.goals` and `away.goals` by counting events where `type == "Goal"` per `event.team == home.name` (and same for away). The recomputed score OVERRIDES any value previously set by `update_fixture()`. This reconciles the API's incremental `goals` field with the cumulative event list.

#### Scenario: Min 15 with empty events yields 0-0

- GIVEN a manager that has already received `update_fixture` for fixture 868019
- WHEN `update_details(events=[], ...)` is called
- THEN `get_state().home.goals == 0`
- AND `get_state().away.goals == 0`

#### Scenario: 4 Goal events split 2-2 override API score

- GIVEN events: `[Goal Argentina Molina 35', Goal Argentina Messi pen 73', Goal Holanda Weghorst 83', Goal Holanda Weghorst 101']`
- AND the API score from `update_fixture` was `1-1`
- WHEN `update_details(events=events, ...)` is called
- THEN `get_state().home.goals == 2`
- AND `get_state().away.goals == 2`

#### Scenario: Reconciliation is idempotent

- GIVEN events with 2 home goals and 1 away goal
- WHEN `update_details(events, ...)` is called twice with the same input
- THEN `home.goals` and `away.goals` are unchanged

### Requirement: Context Text Format

`get_context_text() -> str` MUST return a single UTF-8 string with exactly 7 sections in this fixed order: Header, Goals, Stats, Standout players, Weak players, Substitutions, Cards. Sections MUST be separated by a single blank line (`\n\n`) with one trailing `\n`. All section labels, period names, "Sin …" fallbacks, and highlight-line composition MUST match the `context-text-format` spec exactly (snapshot test pins the byte-level output).

#### Scenario: Snapshot at minute 67 matches the pinned format

- GIVEN state `home=Argentina(2)`, `away=Holanda(1)`, `elapsed=67`, `short="2H"`, with populated events/stats/players
- WHEN `get_context_text()` is called
- THEN the output starts with `⚽ Argentina 2 - 1 Holanda | Minuto 67 | 2do Tiempo`
- AND the output contains exactly 7 sections separated by blank lines

#### Scenario: Pre-kickoff uses every empty-section variant

- GIVEN empty events, `home_stats is None`, `away_stats is None`, empty player lists, `elapsed=0`
- WHEN `get_context_text()` is called
- THEN `GOLES: Sin goles aún`
- AND `ESTADÍSTICAS: No disponibles aún`
- AND `JUGADORES DESTACADOS: Sin datos suficientes`
- AND `JUGADORES FLOJOS: Sin datos suficientes`
- AND `CAMBIOS REALIZADOS: Ninguno`
- AND `TARJETAS: Ninguna`

### Requirement: Prediction Log

`save_prediction(momento: int, content: str) -> None` MUST append a `Prediction(momento=momento, timestamp=datetime.now(tz=UTC), content=content)` to the in-memory list. `get_predictions() -> list[Prediction]` MUST return all saved predictions in append order. Both methods MUST raise `ValueError` if `momento` is outside the closed range `1..=6` (Pydantic `Prediction` validation).

#### Scenario: Save then read round-trips

- GIVEN an empty prediction list
- WHEN `save_prediction(momento=3, content="pred A")` is called
- THEN `get_predictions()` returns one `Prediction` with `momento == 3` and `content == "pred A"`

#### Scenario: Predictions preserve append order

- GIVEN three calls to `save_prediction` with momenti `1, 3, 6`
- WHEN `get_predictions()` is called
- THEN the result is a list of 3 `Prediction`s in the same momento order

#### Scenario: Out-of-range momento is rejected

- GIVEN `save_prediction(momento=7, content="x")`
- WHEN called
- THEN a `ValueError` is raised by the `Prediction` model validator

### Requirement: Mode-Agnostic Behavior

`MatchStateManager` MUST work identically in mock and live modes — it consumes the same `MatchState` model from either data source. The mocking boundary is `create_data_source()`, not this class. Tests MAY construct the manager directly with `MatchState` instances; no env, no factory.
