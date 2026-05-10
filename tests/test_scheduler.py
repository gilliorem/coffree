import os

from src.scheduler import daily_update_time


def test_daily_update_time_uses_env_override():
    old_value = os.environ.get("COFFREE_DAILY_TIME")
    os.environ["COFFREE_DAILY_TIME"] = "09:05"

    try:
        update_time = daily_update_time()
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_DAILY_TIME", None)
        else:
            os.environ["COFFREE_DAILY_TIME"] = old_value

    assert update_time.hour == 9
    assert update_time.minute == 5
    assert update_time.tzinfo.tzname(None) == "Asia/Singapore"


def test_daily_update_time_defaults_to_onboarding_time():
    old_value = os.environ.get("COFFREE_DAILY_TIME")
    os.environ.pop("COFFREE_DAILY_TIME", None)

    try:
        update_time = daily_update_time()
    finally:
        if old_value is not None:
            os.environ["COFFREE_DAILY_TIME"] = old_value

    assert update_time.hour == 8
    assert update_time.minute == 30
