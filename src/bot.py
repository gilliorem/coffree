"""Telegram bot interface for daily free-coffee locations."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from src.config import load_settings
from src.parser import get_locations_for_date


DATE_FORMAT = "%-d-%b-%y"
FALLBACK_DATE_FORMAT = "%#d-%b-%y"


def schedule_date_from_date(value: date) -> str:
    """Format a date like the schedule CSV, for example '8-May-26'."""
    try:
        return value.strftime(DATE_FORMAT)
    except ValueError:
        return value.strftime(FALLBACK_DATE_FORMAT)


def parse_schedule_date(raw_value: str) -> str:
    """Normalize supported user date inputs into the CSV date format."""
    value = raw_value.strip()
    if not value:
        return schedule_date_from_date(date.today())

    for date_format in ("%d-%b-%y", "%d-%b-%Y", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(value, date_format).date()
            return schedule_date_from_date(parsed)
        except ValueError:
            continue

    return value


def build_locations_message(target_date: str, schedule_path: Path | str) -> str:
    """Build the user-facing Telegram message for one schedule date."""
    locations = get_locations_for_date(target_date, schedule_path)
    if not locations:
        return f"No free coffee locations found for {target_date}."

    lines = [f"Free coffee locations for {target_date}:"]
    lines.extend(f"- {location}" for location in locations)
    return "\n".join(lines)


async def start(update, context) -> None:
    await update.message.reply_text(
        "Use /today for today's free coffee locations, or /date 8-May-26 for a specific date."
    )


async def today(update, context) -> None:
    settings = context.bot_data["settings"]
    target_date = schedule_date_from_date(date.today())
    await update.message.reply_text(build_locations_message(target_date, settings.schedule_path))


async def date_command(update, context) -> None:
    settings = context.bot_data["settings"]
    target_date = parse_schedule_date(" ".join(context.args))
    await update.message.reply_text(build_locations_message(target_date, settings.schedule_path))


def run_bot() -> None:
    """Start the Telegram bot."""
    from telegram.ext import Application, CommandHandler

    settings = load_settings()
    application = Application.builder().token(settings.telegram_bot_token).build()
    application.bot_data["settings"] = settings
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("date", date_command))
    application.run_polling()


if __name__ == "__main__":
    run_bot()
