# OpenClaw Telegram Bot

Async Telegram long-polling bot that forwards user messages to OpenClaw and sends OpenClaw responses back to Telegram.

## Configuration

The bot reads `TELEGRAM_BOT_TOKEN` from `../.env` by default:

```env
TELEGRAM_BOT_TOKEN=123456:telegram-token
```

Optional environment variables:

```env
OPENCLAW_AGENT_ID=main
OPENCLAW_COMMAND=openclaw
OPENCLAW_POLL_TIMEOUT=30
TELEGRAM_USER_REPOSITORY_PATH=./data/users.json
```

## Run

From this directory:

```bash
python3 -m openclaw_telegram_bot
```

If running directly from source, include `src` on `PYTHONPATH`:

```bash
PYTHONPATH=src python3 -m openclaw_telegram_bot
```

## Admin Broadcast

The bot stores each Telegram chat that messages it in `data/users.json`. From the OpenClaw dashboard or local terminal, an admin can send a message to every known user:

```bash
python3 run_broadcast.py "Admin announcement"
```

To ask OpenClaw for the message first and broadcast OpenClaw's output to all known users:

```bash
python3 run_prompt_broadcast.py "Write a short product update for all users"
```

Telegram only allows the bot to message users who have already started or messaged the bot.

## Test

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
