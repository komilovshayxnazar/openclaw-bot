"""Admin prompt broadcast command.

This command sends an admin prompt to OpenClaw and broadcasts OpenClaw's output
to every Telegram user known by the bot.
"""

from __future__ import annotations

import argparse
import asyncio
import logging

from openclaw_telegram_bot.broadcast import broadcast_openclaw_output
from openclaw_telegram_bot.config import load_config
from openclaw_telegram_bot.openclaw_service import OpenClawService
from openclaw_telegram_bot.telegram_client import TelegramClient
from openclaw_telegram_bot.user_repository import JsonUserRepository


def main() -> None:
    """Run an OpenClaw-generated Telegram broadcast from the command line."""
    parser = argparse.ArgumentParser(
        description="Ask OpenClaw and broadcast its output to all known bot users."
    )
    parser.add_argument("prompt", help="Prompt to send to OpenClaw.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    config = load_config()
    result = asyncio.run(
        broadcast_openclaw_output(
            prompt=args.prompt,
            telegram_client=TelegramClient(config.telegram_bot_token),
            user_repository=JsonUserRepository(config.user_repository_path),
            openclaw_service=OpenClawService(
                command=config.openclaw_command,
                agent_id=config.openclaw_agent_id,
            ),
        )
    )
    print(
        "OpenClaw prompt broadcast complete: "
        f"total={result.total_users}, "
        f"delivered={result.delivered}, "
        f"failed={result.failed}"
    )


if __name__ == "__main__":
    main()
