"""Daily Telegram automation for Coffree."""

from __future__ import annotations

import os
from datetime import timedelta, time, tzinfo

from src.find_coffee_classes import find_coffee_classes_for_date
from src.format_message import format_daily_prompt
from src.schedule_dates import today_as_schedule_date
from src.subscribers import load_subscribers


DAILY_YES = "daily:yes"
DAILY_NO = "daily:no"


class SingaporeTime(tzinfo):
    """Fixed Singapore timezone used by the Telegram daily job."""

    def utcoffset(self, dt):
        return timedelta(hours=8)

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "Asia/Singapore"


SINGAPORE_TIME = SingaporeTime()


WEEKDAYS = (0, 1, 2, 3, 4)


def daily_update_time() -> time:
    """Return the configured daily send time."""
    raw_time = os.getenv("COFFREE_DAILY_TIME", "08:30").strip()
    hour_text, minute_text = raw_time.split(":", 1)

    return time(
        hour=int(hour_text),
        minute=int(minute_text),
        tzinfo=SINGAPORE_TIME,
    )

def daily_prompt_buttons():
    """Create Telegram YES/NO buttons for the daily prompt."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("YES", callback_data=DAILY_YES)],
            [InlineKeyboardButton("NO", callback_data=DAILY_NO)],
        ]
    )


async def send_daily_coffee_update(context) -> None:
    """Ask every subscribed chat whether Coffree should check today."""
    if not find_coffee_classes_for_date(today_as_schedule_date()):
        return

    for subscriber in load_subscribers():
        chat_id = int(subscriber["chat_id"])
        first_name = subscriber.get("first_name") or None
        await context.bot.send_message(
            chat_id=chat_id,
            text=format_daily_prompt(first_name),
            reply_markup=daily_prompt_buttons(),
        )


def install_daily_job(application) -> None:
    """Register the weekday coffee automation on the Telegram app."""
    if application.job_queue is None:
        raise RuntimeError(
            "Daily automation needs python-telegram-bot[job-queue]. "
            "Run: pip install -r requirements.txt"
        )

    application.job_queue.run_daily(
        send_daily_coffee_update,
        time=daily_update_time(),
        days=WEEKDAYS,
        name="daily-coffee-update",
    )
