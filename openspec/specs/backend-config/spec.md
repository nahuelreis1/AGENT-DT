# backend-config Specification

## Purpose

Environment-driven configuration loader for the AI DT backend. All runtime settings — API key, fixture ID, webhook URLs, polling cadence, mock-mode flag — MUST flow through a single pydantic-settings `Settings` instance so mock and live data sources are selected without code changes.

## Requirements

### Requirement: Settings Class Loads From Environment

The system MUST expose a `Settings` class built on `pydantic-settings.BaseSettings` that loads configuration from process environment variables and an optional `backend/.env` file. The class MUST declare the following fields:

| Field | Type | Default | Required |
|-------|------|---------|----------|
| `API_FOOTBALL_KEY` | `str` | `""` | Conditional (see Validation) |
| `FIXTURE_ID` | `int` | `0` | Conditional (see Validation) |
| `N8N_WEBHOOK_BASE_URL` | `str` | `""` | No |
| `MOCK_MODE` | `bool` | `True` | No |
| `POLLING_INTERVAL` | `int` | `90` | No |

#### Scenario: Defaults applied when env is empty

- GIVEN no environment variables are set and no `.env` file exists
- WHEN `Settings()` is instantiated
- THEN `MOCK_MODE` is `True`
- AND `POLLING_INTERVAL` is `90`

#### Scenario: .env values override defaults

- GIVEN a `.env` file with `MOCK_MODE=false` and `POLLING_INTERVAL=120`
- WHEN `Settings()` is instantiated
- THEN `MOCK_MODE` is `False`
- AND `POLLING_INTERVAL` is `120`

#### Scenario: Integer env var is coerced

- GIVEN env var `FIXTURE_ID=868019`
- WHEN `Settings()` is instantiated
- THEN `FIXTURE_ID == 868019` (int, not str)

### Requirement: Live-Mode Validation

The system MUST reject `Settings` instantiation when `MOCK_MODE=False` and either `API_FOOTBALL_KEY` is empty OR `FIXTURE_ID <= 0`. The validation MUST run via a pydantic `model_validator`.

#### Scenario: Live mode with key and fixture id is accepted

- GIVEN env `API_FOOTBALL_KEY=abc123`, `FIXTURE_ID=868019`, `MOCK_MODE=false`
- WHEN `Settings()` is instantiated
- THEN the call succeeds with the values loaded

#### Scenario: Live mode without API key is rejected

- GIVEN env `MOCK_MODE=false`, `FIXTURE_ID=868019`, and no `API_FOOTBALL_KEY`
- WHEN `Settings()` is instantiated
- THEN a `ValidationError` is raised citing the missing key

#### Scenario: Live mode with fixture id 0 is rejected

- GIVEN env `MOCK_MODE=false`, `API_FOOTBALL_KEY=abc123`, `FIXTURE_ID=0`
- WHEN `Settings()` is instantiated
- THEN a `ValidationError` is raised

#### Scenario: Mock mode with missing live fields is accepted

- GIVEN env `MOCK_MODE=true` and no `API_FOOTBALL_KEY` or `FIXTURE_ID`
- WHEN `Settings()` is instantiated
- THEN the call succeeds (mock mode does not require live credentials)

### Requirement: .env.example Is Provided

The system MUST include a `backend/.env.example` file that lists every `Settings` variable with an obvious placeholder value (never a real secret).

#### Scenario: .env.example contains every variable

- GIVEN the repository at baseline
- WHEN `backend/.env.example` is read
- THEN it contains one line per Settings variable (5 lines)
- AND no line contains a real API key, token, or production URL
