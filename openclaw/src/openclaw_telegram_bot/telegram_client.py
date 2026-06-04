"""Minimal async Telegram Bot API client using the Python standard library."""

from __future__ import annotations

import asyncio
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TelegramClient:
    """Async wrapper for the Telegram Bot HTTP API."""

    bot_token: str

    @property
    def api_base_url(self) -> str:
        """Return the Telegram Bot API base URL."""
        return f"https://api.telegram.org/bot{self.bot_token}"

    async def get_updates(
        self,
        offset: int | None,
        timeout_seconds: int,
    ) -> list[dict[str, Any]]:
        """Long-poll Telegram for new updates."""
        payload: dict[str, str | int] = {
            "timeout": timeout_seconds,
            "allowed_updates": json.dumps(["message"]),
        }
        if offset is not None:
            payload["offset"] = offset

        response = await self._post("getUpdates", payload, timeout_seconds + 10)
        updates = response.get("result", [])
        if not isinstance(updates, list):
            raise RuntimeError("Telegram getUpdates returned an invalid result")
        return updates

    async def send_message(self, chat_id: int, text: str) -> None:
        """Send a text message to a Telegram chat."""
        await self._post(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text[:4096],
                "disable_web_page_preview": "true",
            },
            timeout_seconds=30,
        )

    async def send_chat_action(self, chat_id: int, action: str = "typing") -> None:
        """Send a Telegram chat action such as typing."""
        await self._post(
            "sendChatAction",
            {"chat_id": chat_id, "action": action},
            timeout_seconds=10,
        )

    async def _post(
        self,
        method: str,
        payload: dict[str, str | int],
        timeout_seconds: int,
    ) -> dict[str, Any]:
        """Execute a Telegram API POST request in a worker thread."""
        return await asyncio.to_thread(
            self._post_sync,
            method,
            payload,
            timeout_seconds,
        )

    def _post_sync(
        self,
        method: str,
        payload: dict[str, str | int],
        timeout_seconds: int,
    ) -> dict[str, Any]:
        """Execute a blocking Telegram API request."""
        encoded_payload = urllib.parse.urlencode(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.api_base_url}/{method}",
            data=encoded_payload,
            method="POST",
        )
        request.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))

        if not response_payload.get("ok"):
            raise RuntimeError(f"Telegram API error: {response_payload}")

        return response_payload
