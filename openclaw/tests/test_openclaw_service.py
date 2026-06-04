"""Tests for OpenClaw response extraction."""

from __future__ import annotations

import unittest

from openclaw_telegram_bot.openclaw_service import extract_openclaw_reply


class OpenClawServiceTests(unittest.TestCase):
    """Verify OpenClaw CLI output parsing."""

    def test_extract_reply_from_json(self) -> None:
        """The parser should handle common JSON response fields."""
        reply = extract_openclaw_reply('{"reply": "Hello from OpenClaw"}')

        self.assertEqual(reply, "Hello from OpenClaw")

    def test_extract_nested_text_from_json(self) -> None:
        """Nested payloads should still produce a user-facing reply."""
        reply = extract_openclaw_reply('{"result": {"message": "Nested answer"}}')

        self.assertEqual(reply, "Nested answer")

    def test_plain_text_passthrough(self) -> None:
        """Non-JSON OpenClaw output should be returned unchanged."""
        reply = extract_openclaw_reply("Plain answer")

        self.assertEqual(reply, "Plain answer")


if __name__ == "__main__":
    unittest.main()
