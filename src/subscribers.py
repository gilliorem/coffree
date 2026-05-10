"""Store Telegram chats that should receive daily coffee updates."""

from __future__ import annotations

import json
import os
from pathlib import Path


def subscribers_file() -> Path:
    """Return the local JSON file used for subscriber storage."""
    return Path(os.getenv("COFFREE_SUBSCRIBERS_FILE", "data/subscribers.json"))


def load_subscribers() -> list[dict]:
    """Read subscribed Telegram chats from disk."""
    path = subscribers_file()

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict) and item.get("chat_id")]


def save_subscribers(subscribers: list[dict]) -> None:
    """Write subscribed Telegram chats to disk."""
    path = subscribers_file()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(subscribers, file, indent=2, sort_keys=True)


def subscribe_chat(chat_id: int, first_name: str | None = None) -> None:
    """Remember one Telegram chat for daily updates."""
    subscribers = load_subscribers()

    for subscriber in subscribers:
        if int(subscriber["chat_id"]) == chat_id:
            subscriber["first_name"] = first_name or subscriber.get("first_name", "")
            save_subscribers(subscribers)
            return

    subscribers.append({"chat_id": chat_id, "first_name": first_name or ""})
    save_subscribers(subscribers)


def unsubscribe_chat(chat_id: int) -> None:
    """Remove one Telegram chat from daily updates."""
    subscribers = [
        subscriber
        for subscriber in load_subscribers()
        if int(subscriber["chat_id"]) != chat_id
    ]
    save_subscribers(subscribers)
