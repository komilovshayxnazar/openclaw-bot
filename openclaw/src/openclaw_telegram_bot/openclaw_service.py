"""Service integration for calling OpenClaw from Telegram messages."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpenClawService:
    """Thin async wrapper around the OpenClaw CLI agent command."""

    command: str
    agent_id: str

    async def ask(self, chat_id: int, message: str) -> str:
        """Send a message to OpenClaw and return the assistant response."""
        return await self.ask_with_session(
            session_key=f"telegram-{chat_id}",
            message=message,
        )

    async def ask_with_session(self, session_key: str, message: str) -> str:
        """Send a message to OpenClaw using an explicit session key."""
        process = await asyncio.create_subprocess_exec(
            self.command,
            "agent",
            "--agent",
            self.agent_id,
            "--session-key",
            session_key,
            "--message",
            message,
            "--json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        stdout_text = stdout.decode("utf-8", errors="replace").strip()
        stderr_text = stderr.decode("utf-8", errors="replace").strip()
        if process.returncode != 0:
            detail = stderr_text or stdout_text or "unknown OpenClaw CLI failure"
            raise RuntimeError(f"OpenClaw command failed: {detail}")

        return extract_openclaw_reply(stdout_text)


def extract_openclaw_reply(output: str) -> str:
    """Extract a useful reply string from OpenClaw JSON or plain text output."""
    if not output:
        return "OpenClaw returned an empty response."

    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        return output

    found = _find_text_value(payload, ("reply", "response", "message", "text", "output"))
    if found:
        return found

    return json.dumps(payload, ensure_ascii=False, indent=2)


def _find_text_value(value: object, keys: tuple[str, ...]) -> str | None:
    """Recursively find the first non-empty text field in a JSON-like object."""
    if isinstance(value, dict):
        for key in keys:
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()

        for nested_value in value.values():
            found = _find_text_value(nested_value, keys)
            if found:
                return found

    if isinstance(value, list):
        for item in value:
            found = _find_text_value(item, keys)
            if found:
                return found

    return None
