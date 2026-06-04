"""Telegram bot orchestration for the OpenClaw bridge."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from openclaw_telegram_bot.openclaw_service import OpenClawService
from openclaw_telegram_bot.telegram_client import TelegramClient
from openclaw_telegram_bot.user_repository import JsonUserRepository, TelegramUser


LOGGER = logging.getLogger(__name__)


class OpenClawTelegramBot:
    """Long-polling Telegram bot that forwards messages to OpenClaw."""

    def __init__(
        self,
        telegram_client: TelegramClient,
        openclaw_service: OpenClawService,
        user_repository: JsonUserRepository,
        poll_timeout_seconds: int,
    ) -> None:
        self.telegram_client = telegram_client
        self.openclaw_service = openclaw_service
        self.user_repository = user_repository
        self.poll_timeout_seconds = poll_timeout_seconds
        self._offset: int | None = None
        self._tasks: set[asyncio.Task[None]] = set()

    async def run_forever(self) -> None:
        """Poll Telegram indefinitely and process messages concurrently."""
        LOGGER.info("OpenClaw Telegram bot started")
        while True:
            try:
                updates = await self.telegram_client.get_updates(
                    offset=self._offset,
                    timeout_seconds=self.poll_timeout_seconds,
                )
            except Exception:
                LOGGER.exception("Failed to fetch Telegram updates")
                await asyncio.sleep(5)
                continue

            for update in updates:
                update_id = update.get("update_id")
                if isinstance(update_id, int):
                    self._offset = update_id + 1

                task = asyncio.create_task(self._handle_update(update))
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)

    async def _handle_update(self, update: dict[str, Any]) -> None:
        """Handle a single Telegram update."""
        message = update.get("message")
        if not isinstance(message, dict):
            return

        chat = message.get("chat")
        text = message.get("text")
        if not isinstance(chat, dict) or not isinstance(text, str):
            return

        chat_id = chat.get("id")
        if not isinstance(chat_id, int):
            return

        self.user_repository.upsert(_build_telegram_user(chat))

        if text.startswith("/start"):
            await self.telegram_client.send_message(
                chat_id,
                "Send a message and I will forward it to OpenClaw.",
            )
            return

        if text.startswith("/"):
            await self.telegram_client.send_message(chat_id, "Unsupported command.")
            return

        await self.telegram_client.send_chat_action(chat_id)
        try:
            reply = await self.openclaw_service.ask(chat_id=chat_id, message=text)
        except Exception:
            LOGGER.exception("OpenClaw failed to answer Telegram message")
            reply = "OpenClaw failed to answer this message. Check the bot logs."

        await self.telegram_client.send_message(chat_id, reply)


def _build_telegram_user(chat: dict[str, Any]) -> TelegramUser:
    """Create a stored Telegram user from a Telegram chat payload."""
    chat_id = chat["id"]
    username = chat.get("username")
    first_name = chat.get("first_name")
    return TelegramUser(
        chat_id=chat_id,
        username=username if isinstance(username, str) else None,
        first_name=first_name if isinstance(first_name, str) else None,
    )
