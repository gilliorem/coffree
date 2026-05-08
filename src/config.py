"""Runtime configuration for the Telegram bot."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    schedule_path: Path = Path("data/PM_Schedule.csv")


def load_settings() -> Settings:
    """Load required settings from environment variables."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    schedule_path = Path(os.getenv("SCHEDULE_PATH", "data/PM_Schedule.csv"))
    return Settings(telegram_bot_token=token, schedule_path=schedule_path)
