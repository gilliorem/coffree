"""Date helpers for the workshop schedule CSV."""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta


def today_as_schedule_date() -> str:
    """Return today's date in the CSV format, for example '8-May-26'."""
    demo_date = os.getenv("COFFREE_DATE", "").strip()
    if demo_date:
        return demo_date

    return date.today().strftime("%-d-%b-%y")


def schedule_date_to_date(schedule_date: str) -> date:
    """Parse a CSV date like '8-May-26' into a date object."""
    return datetime.strptime(schedule_date, "%d-%b-%y").date()


def date_as_schedule_date(value: date) -> str:
    """Format a date like the CSV uses."""
    return value.strftime("%-d-%b-%y")


def choose_coffee_date(user_text: str) -> tuple[str, str]:
    """Choose today or tomorrow from the user's message."""
    if "tomorrow" not in user_text.lower():
        return today_as_schedule_date(), "today"

    tomorrow = schedule_date_to_date(today_as_schedule_date()) + timedelta(days=1)
    return date_as_schedule_date(tomorrow), "tomorrow"
