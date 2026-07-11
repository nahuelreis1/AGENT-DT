# polling-loop Specification

## Purpose

Background polling mechanism for live mode. `poll_once` performs a single fetch-update-check cycle; `polling_loop` repeats it on an interval with per-iteration error containment; the FastAPI lifespan wires startup/shutdown of the polling task and resource cleanup.

## Requirements

### Requirement: poll_once Function

`poll_once(data_source, match_state, milestone_detector)` MUST execute the sequence `get_fixture` → `update_fixture` → `check_and_push` in order. If `get_fixture` raises, the error MUST be logged and the iteration MUST complete without crashing. If `check_and_push` raises, the error MUST be logged and the iteration MUST complete without crashing.

#### Scenario: Successful single poll iteration

- GIVEN a data source, initialized manager, and milestone detector
- WHEN `poll_once(data_source, match_state, detector)` is called
- THEN `get_fixture`, `update_fixture`, and `check_and_push` are called in that order

#### Scenario: get_fixture failure is contained

- GIVEN `data_source.get_fixture` raises an exception
- WHEN `poll_once(...)` is called
- THEN the error is logged and no exception propagates to the caller

#### Scenario: check_and_push failure is contained

- GIVEN `update_fixture` succeeds but `check_and_push` raises
- WHEN `poll_once(...)` is called
- THEN the error is logged and no exception propagates to the caller

### Requirement: polling_loop Function

`polling_loop` MUST call `poll_once` every `POLLING_INTERVAL` seconds (default 90). The loop MUST catch all exceptions per iteration (log at error level, then continue). The loop MUST be cancellable via `asyncio.Task.cancel()`.

#### Scenario: Polls on the configured interval

- GIVEN `POLLING_INTERVAL=90` and live mode
- WHEN `polling_loop` runs
- THEN `poll_once` is invoked, followed by a 90-second wait, repeatedly

#### Scenario: Per-iteration exception does not stop the loop

- GIVEN `poll_once` raises on one iteration
- WHEN `polling_loop` is running
- THEN the error is logged and the loop continues to the next interval

#### Scenario: Loop stops on cancellation

- GIVEN `polling_loop` running as an `asyncio.Task`
- WHEN `task.cancel()` is called
- THEN the loop stops and the task completes

### Requirement: Lifespan Startup and Shutdown

On startup the lifespan MUST create `Settings`, create the data source, create `MatchStateManager`, initialize it with the first fixture, and create the `MilestoneDetector`. In live mode it MUST start the polling task; in mock mode it MUST NOT start a polling task. On shutdown it MUST cancel the polling task first, then `aclose` the milestone detector, then `aclose` the API client (only in live mode). The shutdown order MUST be: cancel task → await task → aclose detector → aclose client.

#### Scenario: Live-mode startup starts polling

- GIVEN `MOCK_MODE=false`
- WHEN the app lifespan starts
- THEN services are created, the manager is initialized, and the polling task is running

#### Scenario: Mock-mode startup starts no polling

- GIVEN `MOCK_MODE=true`
- WHEN the app lifespan starts
- THEN services are created and the manager is initialized, but no polling task exists

#### Scenario: Shutdown cancels task then closes resources in order

- GIVEN a running app with an active polling task (live mode)
- WHEN the app lifespan shuts down
- THEN the polling task is cancelled and awaited
- AND THEN the milestone detector is closed
- AND THEN the API client is closed

#### Scenario: Mock-mode shutdown closes detector only

- GIVEN a running app in mock mode (no polling task)
- WHEN the app lifespan shuts down
- THEN the milestone detector is closed and no API client close is required
