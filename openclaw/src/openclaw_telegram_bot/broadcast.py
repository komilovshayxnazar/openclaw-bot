"""Admin broadcast function for sending Telegram messages to all known users."""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import dataclass

from openclaw_telegram_bot.config import load_config
from openclaw_telegram_bot.openclaw_service import OpenClawService
from openclaw_telegram_bot.telegram_client import TelegramClient
from openclaw_telegram_bot.user_repository import JsonUserRepository


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class BroadcastResult:
    """Summary of an admin broadcast attempt."""

    total_users: int
    delivered: int
    failed: int


async def broadcast_to_all_users(
    message: str,
    telegram_client: TelegramClient,
    user_repository: JsonUserRepository,
) -> BroadcastResult:
    """Send a message to every Telegram user known by the bot."""
    users = user_repository.list_all()
    delivered = 0
    failed = 0

    for user in users:
        try:
            await telegram_client.send_message(user.chat_id, message)
            delivered += 1
        except Exception:
            failed += 1
            LOGGER.exception("Failed to broadcast to chat_id=%s", user.chat_id)

    return BroadcastResult(
        total_users=len(users),
        delivered=delivered,
        failed=failed,
    )


async def broadcast_openclaw_output(
    prompt: str,
    telegram_client: TelegramClient,
    user_repository: JsonUserRepository,
    openclaw_service: OpenClawService,
    session_key: str = "admin-broadcast",
) -> BroadcastResult:
    """Ask OpenClaw with an admin prompt and broadcast its output to all users."""
    openclaw_output = await openclaw_service.ask_with_session(
        session_key=session_key,
        message=prompt,
    )
    return await broadcast_to_all_users(
        message=openclaw_output,
        telegram_client=telegram_client,
        user_repository=user_repository,
    )


def main() -> None:
    """Run an admin broadcast from the command line."""
    parser = argparse.ArgumentParser(
        description="Send a raw admin message to all known Telegram bot users."
    )
    parser.add_argument("message", help="Message to send to every known user.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    config = load_config()
    result = asyncio.run(
        broadcast_to_all_users(
            message=args.message,
            telegram_client=TelegramClient(config.telegram_bot_token),
            user_repository=JsonUserRepository(config.user_repository_path),
        )
    )
    print(
        "Broadcast complete: "
        f"total={result.total_users}, "
        f"delivered={result.delivered}, "
        f"failed={result.failed}"
    )


if __name__ == "__main__":
    main()
