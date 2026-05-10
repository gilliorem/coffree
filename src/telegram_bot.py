"""Telegram entrypoint for Coffree.

Coffree does one thing: tell a student where today's free coffee is.
Any normal message gets the same useful service: today's coffee locations,
a human-friendly reply, and one location photo when available.
"""

from __future__ import annotations

import os

from src.find_coffee_classes import find_coffee_classes_for_date
from src.format_message import (
    format_daily_no_message,
    format_daily_prompt,
    format_coffee_message,
    format_direction_complete_message,
    format_location_details,
    format_onboarding_location_list,
    format_onboarding_recommendation,
    format_other_locations,
    format_recommendation_message,
    format_unknown_destination_message,
)
from src.load_env import load_local_env
from src.location_hints import direction_photos, first_profile_photo, find_class_profile, profile_photos
from src.recommend_coffee import order_locations_by_destination, recommend_location
from src.schedule_dates import choose_coffee_date, today_as_schedule_date
from src.student_destination import has_destination, parse_destination
from src.subscribers import subscribe_chat, unsubscribe_chat


ONBOARD_BUILDING_1 = "onboard:building:1"
ONBOARD_BUILDING_2 = "onboard:building:2"
ONBOARD_LEVEL_4_PLUS = "onboard:level:4plus"
ONBOARD_ALL = "onboard:all"
DAILY_YES = "daily:yes"
DAILY_NO = "daily:no"


def remove_prefix(value: str, prefix: str) -> str:
    """Return value without prefix, compatible with Python 3.8."""
    if value.startswith(prefix):
        return value[len(prefix) :]

    return value


def first_photo_for_locations(coffee_classes: list[str]) -> str | None:
    """Return the first available photo for the listed coffee locations."""
    for classroom in coffee_classes:
        profile = find_class_profile(classroom)

        if profile is None:
            continue

        photo = first_profile_photo(profile)
        if photo is not None:
            return photo

    return None


def known_locations(coffee_classes: list[str]) -> list[str]:
    """Return locations that have JSON profiles."""
    return [classroom for classroom in coffee_classes if find_class_profile(classroom) is not None]


def profile_for_location(classroom: str) -> dict[str, str] | None:
    """Return the JSON profile for one schedule location."""
    return find_class_profile(classroom)


def choose_location_for_onboarding(option: str, coffee_classes: list[str]) -> str | None:
    """Choose one coffee location from an onboarding button."""
    for classroom in coffee_classes:
        profile = profile_for_location(classroom)
        if profile is None:
            continue

        if option == ONBOARD_BUILDING_1 and profile["building"] == "1":
            return classroom

        if option == ONBOARD_BUILDING_2 and profile["building"] == "2":
            return classroom

        if option == ONBOARD_LEVEL_4_PLUS and int(profile["level"]) >= 4:
            return classroom

    return first_known_location(coffee_classes)


def onboarding_button_specs() -> list[tuple[str, str]]:
    """Return first-interaction onboarding buttons."""
    return [
        ("Building 1", ONBOARD_BUILDING_1),
        ("Building 2", ONBOARD_BUILDING_2),
        ("Level 4 and above", ONBOARD_LEVEL_4_PLUS),
        ("Just give me the coffee location already!", ONBOARD_ALL),
    ]


def location_action_button_specs(classroom: str) -> list[tuple[str, str]]:
    """Return buttons after a one-location onboarding answer."""
    return [
        ("Get directions to this class", f"directions:{classroom}"),
        ("Get all coffee locations", ONBOARD_ALL),
    ]


def all_location_button_specs(coffee_classes: list[str]) -> list[tuple[str, str]]:
    """Return direction buttons for every listed coffee location."""
    return [
        (f"Need directions details for {classroom}", f"directions:{classroom}")
        for classroom in known_locations(coffee_classes)
    ]


def daily_yes_button_specs(coffee_classes: list[str]) -> list[tuple[str, str]]:
    """Return buttons after the user accepts the daily prompt."""
    locations = known_locations(coffee_classes)[:2]
    buttons = [(f"Direction to {classroom}", f"directions:{classroom}") for classroom in locations]
    buttons.append(("More coffee locations", ONBOARD_ALL))
    return buttons


def inline_buttons(button_specs: list[tuple[str, str]]):
    """Create Telegram inline buttons."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    if not button_specs:
        return None

    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=callback_data)] for label, callback_data in button_specs]
    )


def build_coffee_locations_message(
    user_text: str,
    name: str | None = None,
) -> tuple[str, str | None, list[str], str]:
    """Build a coffee-location answer for loose user questions."""
    coffee_date, coffee_label = choose_coffee_date(user_text)
    coffee_classes = coffee_locations_for_date(coffee_date)
    message = format_coffee_message(coffee_label, coffee_classes, name)
    photo = first_photo_for_locations(coffee_classes)

    return message, photo, coffee_classes, coffee_label


def build_recommendation_message(
    destination_text: str,
    name: str | None = None,
    date_hint: str = "",
) -> tuple[str, str | None, list[str], bool]:
    """Build a destination-aware coffee recommendation."""
    destination = parse_destination(destination_text)
    if not has_destination(destination):
        coffee_date, coffee_label = choose_coffee_date(f"{date_hint} {destination_text}")
        coffee_classes = coffee_locations_for_date(coffee_date)
        return (
            format_unknown_destination_message(name, coffee_classes, coffee_label),
            None,
            coffee_classes,
            False,
        )

    coffee_date, coffee_label = choose_coffee_date(f"{date_hint} {destination_text}")
    coffee_classes = coffee_locations_for_date(coffee_date)
    ordered_locations = order_locations_by_destination(coffee_classes, destination)
    recommended = recommend_location(coffee_classes, destination)

    if recommended is None:
        return format_coffee_message(coffee_label, [], name), None, [], True

    message = format_recommendation_message(recommended, destination.raw_text, name, coffee_label)
    photo = first_photo_for_locations([recommended])
    return message, photo, ordered_locations, True


def remember_recommendation(
    user_data: dict,
    destination_text: str,
    recommended_location: str,
    coffee_label: str = "today",
    ordered_locations: list[str] | None = None,
) -> None:
    """Remember what this user asked and what Coffree recommended."""
    user_data["last_destination"] = destination_text
    user_data["last_recommended_location"] = recommended_location
    user_data["last_coffee_label"] = coffee_label
    user_data["last_ordered_locations"] = ordered_locations or [recommended_location]
    user_data["location_detail_count"] = 0


def last_recommended_location(user_data: dict) -> str | None:
    """Return the last recommended location for this user."""
    return user_data.get("last_recommended_location")


def next_detail_count(user_data: dict) -> int:
    """Increase and return how many times the user asked for directions."""
    count = int(user_data.get("location_detail_count", 0)) + 1
    user_data["location_detail_count"] = count
    return count


def normalize_intent_text(text: str) -> str:
    """Normalize loose user text for simple intent checks."""
    return "".join(char.lower() if char.isalnum() else " " for char in text)


def wants_directions(text: str) -> bool:
    """Return True when the user is probably asking how to find the room."""
    normalized = normalize_intent_text(text)
    words = normalized.split()
    compact = "".join(words)

    direction_phrases = [
        "where",
        "whereis",
        "whereisit",
        "howtogetthere",
        "howtogothere",
        "howgo",
        "howtofind",
        "showme",
        "sendmap",
        "map",
        "directions",
        "direction",
        "guide",
        "helpmefind",
        "findroom",
        "whichway",
        "whr",
        "wer",
    ]

    if any(phrase in compact for phrase in direction_phrases):
        return True

    return "room" in words and ("find" in words or "go" in words)


def wants_coffee_locations(text: str) -> bool:
    """Return True when the user is asking where free coffee is."""
    normalized = normalize_intent_text(text)
    words = normalized.split()
    compact = "".join(words)

    coffee_words = {"coffee", "coffree", "kopi", "caffeine", "drink"}
    free_words = {"free", "complimentary"}
    location_words = {
        "where",
        "whr",
        "wer",
        "which",
        "location",
        "locations",
        "spot",
        "spots",
        "place",
        "places",
        "get",
        "grab",
        "find",
        "at",
    }

    if not any(word in words for word in coffee_words):
        return False

    compact_phrases = [
        "whereisthecoffee",
        "whereiscoffee",
        "wherecoffee",
        "wherecanigetfreecoffee",
        "wherecanigetcoffee",
        "wherecanigrabcoffee",
        "wherecanifindcoffee",
        "wherecanifindfreecoffee",
        "whereisthefreecoffee",
        "freecoffeetoday",
        "coffeelocation",
        "coffeelocations",
        "coffeespot",
        "coffeespots",
        "coffeeplace",
        "coffeeplaces",
        "anycoffee",
        "gotcoffee",
        "havecoffee",
        "needcoffee",
        "wantcoffee",
        "coffeenow",
    ]

    if any(phrase in compact for phrase in compact_phrases):
        return True

    if any(word in words for word in location_words):
        return True

    return any(word in words for word in free_words)


def build_location_details_reply(user_data: dict, classroom: str) -> tuple[str, str | None]:
    """Build remembered-location directions and optional photo."""
    profile = find_class_profile(classroom)
    detail_count = next_detail_count(user_data)
    photos = profile_photos(profile, repeat_count=detail_count) if profile else []
    message = format_location_details(classroom)
    photo = photos[0] if photos else None

    return message, photo


def coffee_locations_for_date(schedule_date: str) -> list[str]:
    """Return coffee locations for a CSV schedule date."""
    return find_coffee_classes_for_date(schedule_date)


def today_locations() -> list[str]:
    """Return today's coffee locations."""
    return coffee_locations_for_date(today_as_schedule_date())


def remembered_other_locations(user_data: dict) -> list[str]:
    """Return other locations from the last recommendation."""
    ordered_locations = user_data.get("last_ordered_locations", [])

    if not ordered_locations:
        return today_locations()[1:]

    return ordered_locations[1:]


def first_known_location(coffee_classes: list[str]) -> str | None:
    """Return the first location that has a profile."""
    for classroom in coffee_classes:
        if find_class_profile(classroom) is not None:
            return classroom

    return None


def action_button_specs(coffee_classes: list[str]) -> list[tuple[str, str]]:
    """Return button labels and callback data for the main answer."""
    primary_location = first_known_location(coffee_classes)
    buttons: list[tuple[str, str]] = []

    if primary_location is not None:
        buttons.append(("Where is this?", f"where:{primary_location}"))

    if len(coffee_classes) > 1:
        buttons.append(("Other locations", "others"))

    return buttons


def action_buttons(coffee_classes: list[str]):
    """Create Telegram inline buttons for the main answer."""
    return inline_buttons(action_button_specs(coffee_classes))


async def send_coffee_message(update, message: str, photo: str | None, coffee_classes: list[str]) -> None:
    """Send text, optional photo, and action buttons."""
    buttons = action_buttons(coffee_classes)

    if photo is not None:
        with open(photo, "rb") as photo_file:
            await update.message.reply_photo(
                photo=photo_file,
                caption=message,
                reply_markup=buttons,
            )
        return

    await update.message.reply_text(message, reply_markup=buttons)


async def send_today_coffee(update, context) -> None:
    """Send today's coffee answer to the user."""
    name = update.effective_user.first_name
    coffee_classes = today_locations()
    message = format_coffee_message("today", coffee_classes, name)
    photo = first_photo_for_locations(coffee_classes)
    await send_coffee_message(update, message, photo, coffee_classes)


async def send_onboarding_prompt(update, context) -> None:
    """Send the first onboarding message with route buttons."""
    await update.message.reply_text(
        format_welcome_message(update.effective_user.first_name),
        reply_markup=inline_buttons(onboarding_button_specs()),
    )


async def send_onboarding_recommendation(query, context, option: str) -> None:
    """Send one onboarding coffee recommendation."""
    coffee_classes = today_locations()
    classroom = choose_location_for_onboarding(option, coffee_classes)

    if classroom is None:
        await query.message.reply_text("No free coffee locations found for today. ☕")
        return

    remember_recommendation(context.user_data, "", classroom, "today", coffee_classes)
    await query.message.reply_text(
        format_onboarding_recommendation(classroom),
        reply_markup=inline_buttons(location_action_button_specs(classroom)),
    )


async def send_all_onboarding_locations(target, coffee_classes: list[str] | None = None) -> None:
    """Send all coffee locations with direction buttons."""
    coffee_classes = coffee_classes or today_locations()
    await target.reply_text(
        format_onboarding_location_list(coffee_classes),
        reply_markup=inline_buttons(all_location_button_specs(coffee_classes)),
    )


async def send_direction_sequence(target, classroom: str) -> None:
    """Send all direction photos for one class, then the closing message."""
    from telegram import InputMediaPhoto

    profile = find_class_profile(classroom)
    photos = direction_photos(profile) if profile else []

    if not photos:
        await target.reply_text(format_location_details(classroom))
        await target.reply_text(format_direction_complete_message())
        return

    if len(photos) == 1:
        with open(photos[0], "rb") as photo_file:
            await target.reply_photo(photo=photo_file)
        await target.reply_text(format_direction_complete_message())
        return

    photo_files = [open(photo, "rb") for photo in photos]
    try:
        media = [InputMediaPhoto(photo_file) for photo_file in photo_files]
        await target.reply_media_group(media=media)
    finally:
        for photo_file in photo_files:
            photo_file.close()

    await target.reply_text(format_direction_complete_message())


async def send_coffee_locations_for_text(update, context, user_text: str) -> None:
    """Send coffee locations for today or tomorrow from loose text."""
    name = update.effective_user.first_name
    message, photo, coffee_classes, coffee_label = build_coffee_locations_message(user_text, name)

    if coffee_classes:
        remember_recommendation(
            context.user_data,
            "",
            coffee_classes[0],
            coffee_label,
            coffee_classes,
        )

    await send_coffee_message(update, message, photo, coffee_classes)


def format_welcome_message(name: str | None = None) -> str:
    """Introduce Coffree and ask where the student is heading."""
    greeting = f"Hey {name}" if name else "Hey"
    return "\n".join(
        [
            f"{greeting}, I’m Coffree. ☕",
            "I help you find the best free coffee stop before your next class.",
            "",
            "Where are you heading next?",
        ]
    )


async def handle_button(update, context) -> None:
    """Handle inline button taps."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data in {ONBOARD_BUILDING_1, ONBOARD_BUILDING_2, ONBOARD_LEVEL_4_PLUS}:
        await send_onboarding_recommendation(query, context, data)
        return

    if data == ONBOARD_ALL:
        await send_all_onboarding_locations(query.message)
        return

    if data == DAILY_YES:
        coffee_classes = today_locations()
        if not coffee_classes:
            await query.message.reply_text("No free coffee locations found for today. ☕")
            return

        await query.message.reply_text(
            format_onboarding_location_list(coffee_classes[:2]),
            reply_markup=inline_buttons(daily_yes_button_specs(coffee_classes)),
        )
        return

    if data == DAILY_NO:
        await query.message.reply_text(format_daily_no_message())
        return

    if data.startswith("directions:"):
        classroom = remove_prefix(data, "directions:")
        context.user_data["last_recommended_location"] = classroom
        await send_direction_sequence(query.message, classroom)
        return

    if data == "others":
        coffee_label = context.user_data.get("last_coffee_label", "today")
        await query.message.reply_text(
            format_other_locations(remembered_other_locations(context.user_data), coffee_label)
        )
        return

    if data.startswith("where:"):
        classroom = last_recommended_location(context.user_data) or remove_prefix(data, "where:")
        await send_direction_sequence(query.message, classroom)


async def start(update, context) -> None:
    """Start by asking where the student is heading."""
    subscribe_chat(update.effective_chat.id, update.effective_user.first_name)
    await send_onboarding_prompt(update, context)


async def stop(update, context) -> None:
    """Stop daily coffee updates for this chat."""
    unsubscribe_chat(update.effective_chat.id)
    await update.message.reply_text("Done, I’ll stop sending daily coffee updates. ☕")


async def today(update, context) -> None:
    """Reply to /today with today's coffee answer."""
    await send_today_coffee(update, context)


async def normal_message(update, context) -> None:
    """Use the user's message as their next destination."""
    if wants_coffee_locations(update.message.text):
        await send_coffee_locations_for_text(update, context, update.message.text)
        return

    remembered_location = last_recommended_location(context.user_data)
    if remembered_location and wants_directions(update.message.text):
        await send_direction_sequence(update.message, remembered_location)
        return

    await send_onboarding_prompt(update, context)


def run_bot() -> None:
    """Start the Telegram bot."""
    from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

    from src.scheduler import install_daily_job

    load_local_env()
    token = os.environ["TELEGRAM_BOT_TOKEN"]

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, normal_message))
    install_daily_job(app)
    app.run_polling()


if __name__ == "__main__":
    run_bot()
