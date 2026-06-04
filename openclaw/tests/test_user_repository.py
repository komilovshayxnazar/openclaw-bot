"""Tests for Telegram user persistence."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from openclaw_telegram_bot.user_repository import JsonUserRepository, TelegramUser


class UserRepositoryTests(unittest.TestCase):
    """Verify JSON-backed Telegram user storage."""

    def test_upsert_creates_and_updates_user(self) -> None:
        """Users should be stored once by chat ID."""
        with TemporaryDirectory() as temp_dir:
            repository = JsonUserRepository(Path(temp_dir) / "users.json")
            repository.upsert(TelegramUser(chat_id=1, username="old"))
            repository.upsert(TelegramUser(chat_id=1, username="new"))

            users = repository.list_all()

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].chat_id, 1)
        self.assertEqual(users[0].username, "new")


if __name__ == "__main__":
    unittest.main()
