"""Tests for bot configuration loading."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from openclaw_telegram_bot.config import load_config, parse_env_file


class ConfigTests(unittest.TestCase):
    """Verify dotenv parsing and config validation."""

    def test_parse_env_file_handles_spaces_and_quotes(self) -> None:
        """Dotenv parser should support the existing token style."""
        with TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "TELEGRAM_BOT_TOKEN = 'abc:123'\nOPENCLAW_AGENT_ID=main\n",
                encoding="utf-8",
            )

            values = parse_env_file(env_path)

        self.assertEqual(values["TELEGRAM_BOT_TOKEN"], "abc:123")
        self.assertEqual(values["OPENCLAW_AGENT_ID"], "main")

    def test_load_config_requires_token(self) -> None:
        """Missing Telegram tokens should fail fast on startup."""
        with TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"

            with self.assertRaises(RuntimeError):
                load_config(env_path)


if __name__ == "__main__":
    unittest.main()
