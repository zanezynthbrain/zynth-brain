"""Centralized runtime configuration for the ZYNTH agent backend.

All values are sourced from environment variables (or a local ``.env`` file)
so that no secrets are ever hard-coded. Use :func:`get_settings` to obtain a
cached, validated :class:`Settings` instance anywhere in the codebase.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM provider ---------------------------------------------------
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    model_name: str = Field(default="claude-sonnet-4-6", alias="ZYNTH_MODEL_NAME")
    fallback_model_name: str = Field(default="claude-haiku-4-5-20251001", alias="ZYNTH_FALLBACK_MODEL_NAME")

    # --- Token / cost governance ----------------------------------------
    max_tokens_per_call: int = Field(default=4096, alias="ZYNTH_MAX_TOKENS_PER_CALL")
    max_tokens_per_workflow: int = Field(default=60_000, alias="ZYNTH_MAX_TOKENS_PER_WORKFLOW")
    max_llm_retries: int = Field(default=3, alias="ZYNTH_MAX_LLM_RETRIES")
    max_json_repair_attempts: int = Field(default=2, alias="ZYNTH_MAX_JSON_REPAIR_ATTEMPTS")
    request_timeout_seconds: float = Field(default=60.0, alias="ZYNTH_REQUEST_TIMEOUT_SECONDS")

    # --- Orchestrator QA gate -------------------------------------------
    max_agent_retries: int = Field(default=2, alias="ZYNTH_MAX_AGENT_RETRIES")
    qa_min_pass_score: float = Field(default=0.7, alias="ZYNTH_QA_MIN_PASS_SCORE")

    # --- Third-party research/SEO tooling -------------------------------
    serper_api_key: str = Field(default="", alias="SERPER_API_KEY")
    semrush_api_key: str = Field(default="", alias="SEMRUSH_API_KEY")
    jina_api_key: str = Field(default="", alias="JINA_API_KEY")
    allow_network: bool = Field(default=False, alias="ZYNTH_ALLOW_NETWORK")

    # --- Misc -------------------------------------------------------------
    log_level: str = Field(default="INFO", alias="ZYNTH_LOG_LEVEL")
    output_dir: str = Field(default="outputs", alias="ZYNTH_OUTPUT_DIR")

    @property
    def has_llm_credentials(self) -> bool:
        """Whether a real Anthropic API key is configured.

        When this is False, the LLM client transparently falls back to a
        deterministic mock mode so the framework remains runnable (and
        testable) without network access or secrets.
        """
        return bool(self.anthropic_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a process-wide cached settings instance."""
    return Settings()
