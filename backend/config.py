"""Environment-driven configuration for the AI DT backend.

Loads from process env and an optional `backend/.env` file via
pydantic-settings. A `model_validator` enforces the live-mode
preconditions: MOCK_MODE=false requires both API_FOOTBALL_KEY and a
positive FIXTURE_ID.

Spec: openspec/changes/backend-foundation/specs/backend-config/spec.md
"""
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All runtime settings for the AI DT backend.

    Field defaults match the spec: mock mode is the safe default,
    polling cadence is 90 seconds, and live credentials are empty
    until the operator provides them.
    """

    API_FOOTBALL_KEY: str = ""
    FIXTURE_ID: int = 0
    N8N_WEBHOOK_BASE_URL: str = ""
    MOCK_MODE: bool = True
    POLLING_INTERVAL: int = 90
    MOCK_DATA_DIR: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @model_validator(mode="after")
    def _validate_live_mode(self):
        """Reject live mode when key or fixture id is missing/invalid.

        Mock mode never requires live credentials, so the validator
        is a no-op whenever MOCK_MODE=True.
        """
        if not self.MOCK_MODE:
            if not self.API_FOOTBALL_KEY:
                raise ValueError("API_FOOTBALL_KEY is required when MOCK_MODE=false")
            if self.FIXTURE_ID <= 0:
                raise ValueError("FIXTURE_ID must be > 0 when MOCK_MODE=false")
        return self
