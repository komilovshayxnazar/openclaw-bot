"""Configuration loading for the OpenClaw Telegram bot."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = PROJECT_ROOT.parent / ".env"


@dataclass(frozen=True, slots=True)
class BotConfig:
    """Runtime settings required by the Telegram bot."""

    telegram_bot_token: str
    user_repository_path: Path
    openclaw_command: str = "openclaw"
    openclaw_agent_id: str = "main"
    poll_timeout_seconds: int = 30


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a simple dotenv file without requiring third-party packages."""
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key:
            values[key] = value

    return values


def load_config(env_file: Path = DEFAULT_ENV_FILE) -> BotConfig:
    """Load bot configuration from environment variables and dotenv values."""
    dotenv_values = parse_env_file(env_file)

    def read_value(name: str, default: str | None = None) -> str | None:
        return os.environ.get(name) or dotenv_values.get(name) or default

    token = read_value("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            f"TELEGRAM_BOT_TOKEN is required in the environment or {env_file}"
        )

    timeout = read_value("OPENCLAW_POLL_TIMEOUT", "30")
    if timeout is None or not timeout.isdigit():
        raise RuntimeError("OPENCLAW_POLL_TIMEOUT must be a positive integer")

    return BotConfig(
        telegram_bot_token=token,
        user_repository_path=Path(
            read_value(
                "TELEGRAM_USER_REPOSITORY_PATH",
                str(PROJECT_ROOT / "data" / "users.json"),
            )
            or PROJECT_ROOT / "data" / "users.json"
        ),
        openclaw_command=read_value("OPENCLAW_COMMAND", "openclaw") or "openclaw",
        openclaw_agent_id=read_value("OPENCLAW_AGENT_ID", "main") or "main",
        poll_timeout_seconds=int(timeout),
    )
