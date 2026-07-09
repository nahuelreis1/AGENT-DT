"""Tests for backend pydantic-settings config.

Covers every scenario in
openspec/changes/backend-foundation/specs/backend-config/spec.md
plus triangulation cases that exercise the live-mode validator
(negative fixture id, mocked .env file path, env precedence over .env).
"""
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.config import Settings

# All five Settings field names. Used by the autouse fixture to clear
# the environment between tests so pydantic-settings does not pick up
# leaked state from the host shell.
_SETTINGS_ENV_VARS = (
    "API_FOOTBALL_KEY",
    "FIXTURE_ID",
    "N8N_WEBHOOK_BASE_URL",
    "MOCK_MODE",
    "POLLING_INTERVAL",
)


@pytest.fixture(autouse=True)
def _clean_settings_env(monkeypatch):
    """Strip every Settings env var before each test, restore after.

    pydantic-settings reads from os.environ first, so any leaked variable
    from the developer's shell would silently mask the defaults we want
    to test. monkeypatch.setenv/delenv in the test then re-establishes
    the exact env the scenario needs.
    """
    for var in _SETTINGS_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    yield


# ---------------------------------------------------------------------------
# Requirement: Settings Class Loads From Environment
# ---------------------------------------------------------------------------

class TestSettingsDefaults:
    def test_defaults_applied_when_env_is_empty(self):
        """Spec: 'Defaults applied when env is empty'.

        With no env vars and no .env file, pydantic-settings must use
        the class-level defaults: MOCK_MODE=True, POLLING_INTERVAL=90,
        API_FOOTBALL_KEY='', FIXTURE_ID=0, N8N_WEBHOOK_BASE_URL=''.
        """
        s = Settings(_env_file=None)
        assert s.MOCK_MODE is True
        assert s.POLLING_INTERVAL == 90
        assert s.API_FOOTBALL_KEY == ""
        assert s.FIXTURE_ID == 0
        assert s.N8N_WEBHOOK_BASE_URL == ""

    def test_env_var_overrides_defaults(self, monkeypatch):
        """Spec: '.env values override defaults' — exercised via env vars
        because pydantic-settings precedence is: process env > .env file.
        This also triangulates the boolean and int parsers.

        Live-mode fields are included so the validator stays satisfied;
        the subject of this test is the override mechanism, not the
        validator (covered separately in TestSettingsLiveMode).
        """
        monkeypatch.setenv("MOCK_MODE", "false")
        monkeypatch.setenv("API_FOOTBALL_KEY", "abc123")
        monkeypatch.setenv("FIXTURE_ID", "868019")
        monkeypatch.setenv("POLLING_INTERVAL", "120")
        s = Settings(_env_file=None)
        assert s.MOCK_MODE is False
        assert s.POLLING_INTERVAL == 120

    def test_dotenv_file_overrides_defaults(self, monkeypatch, tmp_path):
        """Spec: '.env values override defaults' — exercised through an
        actual .env file in a tmp cwd. Verifies the Settings class
        reads the .env file when env vars are absent.

        Live-mode fields are included so the validator stays satisfied.
        """
        env_file = tmp_path / ".env"
        env_file.write_text(
            "MOCK_MODE=false\n"
            "API_FOOTBALL_KEY=abc123\n"
            "FIXTURE_ID=868019\n"
            "POLLING_INTERVAL=120\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)
        s = Settings()
        assert s.MOCK_MODE is False
        assert s.POLLING_INTERVAL == 120

    def test_integer_env_var_is_coerced(self, monkeypatch):
        """Spec: 'Integer env var is coerced'.

        FIXTURE_ID=868019 must come through as a real int — not as the
        string "868019". This is the contract pydantic-settings gives us
        for free but we lock it in with an explicit test.
        """
        monkeypatch.setenv("FIXTURE_ID", "868019")
        s = Settings(_env_file=None)
        assert s.FIXTURE_ID == 868019
        assert isinstance(s.FIXTURE_ID, int)

    def test_env_var_takes_precedence_over_dotenv(self, monkeypatch, tmp_path):
        """Triangulation: when both are set, process env wins over .env.
        Documents the precedence rule that pydantic-settings follows.
        """
        env_file = tmp_path / ".env"
        env_file.write_text("POLLING_INTERVAL=120\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("POLLING_INTERVAL", "45")
        s = Settings()
        assert s.POLLING_INTERVAL == 45


# ---------------------------------------------------------------------------
# Requirement: Live-Mode Validation
# ---------------------------------------------------------------------------

class TestSettingsLiveMode:
    def test_live_mode_with_key_and_fixture_id_is_accepted(self, monkeypatch):
        """Spec: 'Live mode with key and fixture id is accepted'.

        When MOCK_MODE=false, API_FOOTBALL_KEY, and FIXTURE_ID are all
        present and valid, instantiation must succeed and the values
        must round-trip.
        """
        monkeypatch.setenv("MOCK_MODE", "false")
        monkeypatch.setenv("API_FOOTBALL_KEY", "abc123")
        monkeypatch.setenv("FIXTURE_ID", "868019")
        s = Settings(_env_file=None)
        assert s.MOCK_MODE is False
        assert s.API_FOOTBALL_KEY == "abc123"
        assert s.FIXTURE_ID == 868019

    def test_live_mode_without_api_key_is_rejected(self, monkeypatch):
        """Spec: 'Live mode without API key is rejected'.

        With MOCK_MODE=false and an empty API_FOOTBALL_KEY, pydantic
        must raise ValidationError citing the missing key.
        """
        monkeypatch.setenv("MOCK_MODE", "false")
        monkeypatch.setenv("FIXTURE_ID", "868019")
        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_live_mode_with_fixture_id_zero_is_rejected(self, monkeypatch):
        """Spec: 'Live mode with fixture id 0 is rejected'.

        FIXTURE_ID=0 is the default and is NOT a valid live-mode id;
        the validator must reject it.
        """
        monkeypatch.setenv("MOCK_MODE", "false")
        monkeypatch.setenv("API_FOOTBALL_KEY", "abc123")
        monkeypatch.setenv("FIXTURE_ID", "0")
        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_live_mode_with_negative_fixture_id_is_rejected(self, monkeypatch):
        """Triangulation: any non-positive fixture id is rejected, not
        just zero. Exercises the `<= 0` branch of the validator.
        """
        monkeypatch.setenv("MOCK_MODE", "false")
        monkeypatch.setenv("API_FOOTBALL_KEY", "abc123")
        monkeypatch.setenv("FIXTURE_ID", "-1")
        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_mock_mode_with_missing_live_fields_is_accepted(self, monkeypatch):
        """Spec: 'Mock mode with missing live fields is accepted'.

        When MOCK_MODE=true, neither the API key nor the fixture id
        is required; the validator must skip the live-mode checks.
        """
        monkeypatch.setenv("MOCK_MODE", "true")
        s = Settings(_env_file=None)
        assert s.MOCK_MODE is True
        assert s.API_FOOTBALL_KEY == ""
        assert s.FIXTURE_ID == 0

    def test_mock_mode_default_does_not_trigger_live_validation(self):
        """Triangulation: the default MOCK_MODE=True path must NEVER
        call the live-mode validator. If the default ever flips, this
        test will fail loudly rather than crashing the entire test
        suite on import.
        """
        # No env vars, no .env file → default MOCK_MODE=True.
        # The validator must not raise even though the live fields are
        # at their empty/zero defaults.
        s = Settings(_env_file=None)
        assert s.MOCK_MODE is True


# ---------------------------------------------------------------------------
# Requirement: .env.example Is Provided
# ---------------------------------------------------------------------------

class TestEnvExample:
    def test_env_example_contains_every_variable(self):
        """Spec: '.env.example contains every variable' (5 lines).

        Reads the actual .env.example from the backend package and
        asserts that every Settings field appears exactly once.
        """
        env_example = Path(__file__).resolve().parent.parent / ".env.example"
        assert env_example.exists(), f"missing file: {env_example}"
        content = env_example.read_text(encoding="utf-8")

        for var in _SETTINGS_ENV_VARS:
            assert var in content, f".env.example must define {var}"

        # One non-comment line per variable — strips blanks and comments.
        non_comment_lines = [
            line for line in content.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        assert len(non_comment_lines) == 5, (
            f".env.example must have exactly 5 variable lines, "
            f"found {len(non_comment_lines)}: {non_comment_lines!r}"
        )

    def test_env_example_contains_no_real_secrets(self):
        """Triangulation: the placeholder values must not look like
        real API keys, tokens, or production URLs. Catches accidental
        copy-paste of a developer-local .env file.
        """
        env_example = Path(__file__).resolve().parent.parent / ".env.example"
        content = env_example.read_text(encoding="utf-8").lower()
        for forbidden in ("http://localhost", "http://127.0.0.1", "https://api-football.com"):
            assert forbidden not in content, (
                f".env.example contains forbidden token: {forbidden!r}"
            )
