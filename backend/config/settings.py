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
    # Generous timeout: a 4k-token structured proposal batch takes 1-3 min
    request_timeout_seconds: float = Field(default=240.0, alias="ZYNTH_REQUEST_TIMEOUT_SECONDS")

    # --- Orchestrator QA gate -------------------------------------------
    max_agent_retries: int = Field(default=2, alias="ZYNTH_MAX_AGENT_RETRIES")
    qa_min_pass_score: float = Field(default=0.7, alias="ZYNTH_QA_MIN_PASS_SCORE")

    # --- Voice transcription (free Gemini key: aistudio.google.com) ------
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    transcribe_model_name: str = Field(default="gemini-2.5-flash", alias="ZYNTH_TRANSCRIBE_MODEL")

    # --- Third-party research/SEO tooling -------------------------------
    serper_api_key: str = Field(default="", alias="SERPER_API_KEY")
    semrush_api_key: str = Field(default="", alias="SEMRUSH_API_KEY")
    jina_api_key: str = Field(default="", alias="JINA_API_KEY")
    allow_network: bool = Field(default=False, alias="ZYNTH_ALLOW_NETWORK")

    # --- Telegram bot (ZYNTH MD / @zynth_md_approval_bot) ----------------
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    # Your personal chat ID — receives CEO briefs and is your command center
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")
    # Department group chat IDs — bot posts dept-specific content here
    telegram_bd_chat_id: str = Field(default="", alias="TELEGRAM_BD_CHAT_ID")
    telegram_creative_chat_id: str = Field(default="", alias="TELEGRAM_CREATIVE_CHAT_ID")
    telegram_marketing_chat_id: str = Field(default="", alias="TELEGRAM_MARKETING_CHAT_ID")
    telegram_gm_chat_id: str = Field(default="", alias="TELEGRAM_GM_CHAT_ID")

    # --- Scheduler / timezone --------------------------------------------
    # Yangon is UTC+6:30 (Asia/Rangoon)
    scheduler_timezone: str = Field(default="Asia/Rangoon", alias="ZYNTH_TIMEZONE")
    # 05:30 Yangon = 07:00 Singapore — morning brief lands at 7am SGT
    daily_brief_hour: int = Field(default=5, alias="ZYNTH_BRIEF_HOUR")
    daily_brief_minute: int = Field(default=30, alias="ZYNTH_BRIEF_MINUTE")
    eod_report_hour: int = Field(default=18, alias="ZYNTH_EOD_HOUR")

    # --- Storage ---------------------------------------------------------
    google_drive_folder_id: str = Field(default="", alias="ZYNTH_GDRIVE_FOLDER_ID")

    # --- Cost governance -------------------------------------------------
    # Hard daily API spend cap in Singapore dollars. Bot halts LLM calls and
    # alerts via Telegram when this is reached. Alert fires at 80%.
    daily_budget_sgd: float = Field(default=5.0, alias="ZYNTH_DAILY_BUDGET_SGD")

    # --- Business events -------------------------------------------------
    # ISO date (YYYY-MM-DD) for the next major ZYNTH event (e.g. IGNITE).
    # Shown as a countdown in every CEO morning brief.
    ignite_date: str = Field(default="2026-11-14", alias="ZYNTH_IGNITE_DATE")
    ignite_name: str = Field(default="IGNITE Summit", alias="ZYNTH_IGNITE_NAME")

    # --- Misc -------------------------------------------------------------
    log_level: str = Field(default="INFO", alias="ZYNTH_LOG_LEVEL")
    output_dir: str = Field(default="outputs", alias="ZYNTH_OUTPUT_DIR")
    agency_name: str = Field(default="ZYNTH", alias="ZYNTH_AGENCY_NAME")

    @property
    def has_telegram(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)

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
