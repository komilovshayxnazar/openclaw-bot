"""Run the OpenClaw Telegram bot from the source tree."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from openclaw_telegram_bot.main import main  # noqa: E402


if __name__ == "__main__":
    main()
