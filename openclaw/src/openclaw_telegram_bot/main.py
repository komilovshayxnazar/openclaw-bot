"""Console entrypoint for the OpenClaw Telegram bot."""

from __future__ import annotations

import asyncio
import logging

from openclaw_telegram_bot.bot import OpenClawTelegramBot
from openclaw_telegram_bot.config import load_config
from openclaw_telegram_bot.openclaw_service import OpenClawService
from openclaw_telegram_bot.telegram_client import TelegramClient
from openclaw_telegram_bot.user_repository import JsonUserRepository


def main() -> None:
    """Start the OpenClaw Telegram bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    config = load_config()
    bot = OpenClawTelegramBot(
        telegram_client=TelegramClient(config.telegram_bot_token),
        openclaw_service=OpenClawService(
            command=config.openclaw_command,
            agent_id=config.openclaw_agent_id,
        ),
        user_repository=JsonUserRepository(config.user_repository_path),
        poll_timeout_seconds=config.poll_timeout_seconds,
    )
    asyncio.run(bot.run_forever())
