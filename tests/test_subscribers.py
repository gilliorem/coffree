import os
from tempfile import TemporaryDirectory

from src.subscribers import load_subscribers, subscribe_chat, unsubscribe_chat


def test_subscribe_chat_stores_and_updates_one_chat():
    old_value = os.environ.get("COFFREE_SUBSCRIBERS_FILE")

    try:
        with TemporaryDirectory() as temp_dir:
            os.environ["COFFREE_SUBSCRIBERS_FILE"] = f"{temp_dir}/subscribers.json"
            subscribe_chat(123, "Remi")
            subscribe_chat(123, "Remi Updated")

            assert load_subscribers() == [{"chat_id": 123, "first_name": "Remi Updated"}]
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_SUBSCRIBERS_FILE", None)
        else:
            os.environ["COFFREE_SUBSCRIBERS_FILE"] = old_value


def test_unsubscribe_chat_removes_chat():
    old_value = os.environ.get("COFFREE_SUBSCRIBERS_FILE")

    try:
        with TemporaryDirectory() as temp_dir:
            os.environ["COFFREE_SUBSCRIBERS_FILE"] = f"{temp_dir}/subscribers.json"
            subscribe_chat(123, "Remi")
            unsubscribe_chat(123)

            assert load_subscribers() == []
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_SUBSCRIBERS_FILE", None)
        else:
            os.environ["COFFREE_SUBSCRIBERS_FILE"] = old_value
