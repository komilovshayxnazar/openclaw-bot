"""Repository for Telegram users known to the bot."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class TelegramUser:
    """Telegram chat recipient stored for admin broadcasts."""

    chat_id: int
    username: str | None = None
    first_name: str | None = None


class JsonUserRepository:
    """Persist Telegram users in a JSON file."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def upsert(self, user: TelegramUser) -> None:
        """Insert or update a Telegram user by chat ID."""
        users = {stored_user.chat_id: stored_user for stored_user in self.list_all()}
        users[user.chat_id] = user
        self._write_users(list(users.values()))

    def list_all(self) -> list[TelegramUser]:
        """Return all known Telegram users."""
        if not self.path.exists():
            return []

        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise RuntimeError(f"Invalid user repository payload: {self.path}")

        users: list[TelegramUser] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            chat_id = item.get("chat_id")
            if not isinstance(chat_id, int):
                continue
            users.append(
                TelegramUser(
                    chat_id=chat_id,
                    username=_optional_str(item.get("username")),
                    first_name=_optional_str(item.get("first_name")),
                )
            )
        return users

    def _write_users(self, users: list[TelegramUser]) -> None:
        """Write known users atomically enough for this single-process bot."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "chat_id": user.chat_id,
                "username": user.username,
                "first_name": user.first_name,
            }
            for user in sorted(users, key=lambda item: item.chat_id)
        ]
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _optional_str(value: object) -> str | None:
    """Return a stripped string or None."""
    if not isinstance(value, str):
        return None
    stripped_value = value.strip()
    return stripped_value or None
