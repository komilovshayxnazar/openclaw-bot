"""Tests for admin broadcast behavior."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from openclaw_telegram_bot.broadcast import (
    broadcast_openclaw_output,
    broadcast_to_all_users,
)
from openclaw_telegram_bot.user_repository import JsonUserRepository, TelegramUser


class FakeTelegramClient:
    """Fake Telegram client used to verify broadcast delivery."""

    def __init__(self) -> None:
        self.sent_messages: list[tuple[int, str]] = []

    async def send_message(self, chat_id: int, text: str) -> None:
        """Record a sent message."""
        self.sent_messages.append((chat_id, text))


class FakeOpenClawService:
    """Fake OpenClaw service used to verify prompt broadcast behavior."""

    def __init__(self, output: str) -> None:
        self.output = output
        self.requests: list[tuple[str, str]] = []

    async def ask_with_session(self, session_key: str, message: str) -> str:
        """Record the prompt and return the configured output."""
        self.requests.append((session_key, message))
        return self.output


class BroadcastTests(unittest.IsolatedAsyncioTestCase):
    """Verify admin broadcast delivery to all known users."""

    async def test_broadcast_sends_to_all_users(self) -> None:
        """Broadcast should send the message to every stored chat ID."""
        with TemporaryDirectory() as temp_dir:
            repository = JsonUserRepository(Path(temp_dir) / "users.json")
            repository.upsert(TelegramUser(chat_id=10))
            repository.upsert(TelegramUser(chat_id=20))
            telegram_client = FakeTelegramClient()

            result = await broadcast_to_all_users(
                message="Maintenance notice",
                telegram_client=telegram_client,  # type: ignore[arg-type]
                user_repository=repository,
            )

        self.assertEqual(result.total_users, 2)
        self.assertEqual(result.delivered, 2)
        self.assertEqual(result.failed, 0)
        self.assertEqual(
            telegram_client.sent_messages,
            [(10, "Maintenance notice"), (20, "Maintenance notice")],
        )

    async def test_prompt_broadcast_sends_openclaw_output(self) -> None:
        """Admin prompt broadcasts should send OpenClaw output, not the prompt."""
        with TemporaryDirectory() as temp_dir:
            repository = JsonUserRepository(Path(temp_dir) / "users.json")
            repository.upsert(TelegramUser(chat_id=10))
            telegram_client = FakeTelegramClient()
            openclaw_service = FakeOpenClawService("Generated announcement")

            result = await broadcast_openclaw_output(
                prompt="Write a short announcement",
                telegram_client=telegram_client,  # type: ignore[arg-type]
                user_repository=repository,
                openclaw_service=openclaw_service,  # type: ignore[arg-type]
            )

        self.assertEqual(result.delivered, 1)
        self.assertEqual(
            openclaw_service.requests,
            [("admin-broadcast", "Write a short announcement")],
        )
        self.assertEqual(
            telegram_client.sent_messages,
            [(10, "Generated announcement")],
        )


if __name__ == "__main__":
    unittest.main()
