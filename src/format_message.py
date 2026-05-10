"""Format coffee locations as text for Telegram."""

from __future__ import annotations

from src.location_hints import get_location_details, profile_building_level_text, profile_hints


def greeting_for(name: str | None) -> str:
    """Create a short greeting."""
    if name:
        return f"Good morning {name}"

    return "Good morning"


def same_hint(left: str, right: str) -> bool:
    """Compare hints while ignoring punctuation and case."""
    clean_left = "".join(char.lower() for char in left if char.isalnum())
    clean_right = "".join(char.lower() for char in right if char.isalnum())
    return clean_left == clean_right


def cleaned_name(profile: dict[str, str]) -> str:
    """Return the common name without repeating the class ID."""
    class_id = profile["class_id"]
    name = profile["name"].strip()

    if not name:
        return ""

    compact_class_id = "".join(char.lower() for char in class_id if char.isalnum())
    compact_name = "".join(char.lower() for char in name if char.isalnum())

    if compact_name == compact_class_id or compact_name.startswith(compact_class_id):
        return ""

    return name


def location_line(classroom: str, repeat_count: int = 0) -> str:
    """Create one compact location line."""
    profile = get_location_details(classroom)

    if profile is None:
        return f"- {classroom}"

    parts = [classroom]

    name = cleaned_name(profile)
    if name:
        parts.append(name)

    building_level = profile_building_level_text(profile)
    if building_level:
        parts.append(building_level)

    hints = profile_hints(profile, repeat_count)
    if hints:
        parts.append(hints[0])

    return "- " + " — ".join(parts)


def location_summary(classroom: str) -> str:
    """Create a natural one-line summary for one location."""
    profile = get_location_details(classroom)

    if profile is None:
        return classroom

    name = cleaned_name(profile) or classroom
    building = profile_building_level_text(profile)
    hint = profile_hints(profile)[0] if profile_hints(profile) else ""

    parts = [name]

    if building:
        parts.append(building)

    if hint and not same_hint(hint, building):
        parts.append(hint)

    return " — ".join(parts)


def onboarding_location_value(classroom: str) -> str:
    """Create the compact location value used in onboarding flows."""
    profile = get_location_details(classroom)

    if profile is None:
        return classroom

    name = cleaned_name(profile)
    parts = [profile["class_id"]]

    if name:
        parts.append(name)

    parts.extend([f"Building {profile['building']}", f"Level {profile['level']}"])

    return ", ".join(part for part in parts if part)


def onboarding_location_bullet(classroom: str) -> str:
    """Create one bullet for the all-locations onboarding answer."""
    profile = get_location_details(classroom)

    if profile is None:
        return f"- {classroom}"

    hint = f" ({profile['hint_1']})" if profile["hint_1"] else ""
    name = cleaned_name(profile)
    label = profile["class_id"]
    if name:
        label = f"{label}: {name}"

    return f"- {label} Building {profile['building']} Level {profile['level']}{hint}"


def format_onboarding_recommendation(classroom: str) -> str:
    """Create the one-location onboarding recommendation."""
    location_value = onboarding_location_value(classroom)

    return "\n".join(
        [
            f"You can grab your free coffee here in {location_value} ☕",
            "Recommended timing: 9:15am onwards.",
            "",
            "Tap “Where is this?” if you want help finding the room.",
        ]
    )


def format_onboarding_location_list(coffee_classes: list[str]) -> str:
    """Create the all-locations onboarding answer."""
    if not coffee_classes:
        return "No free coffee locations found for today. ☕"

    return "\n\n".join(onboarding_location_bullet(classroom) for classroom in coffee_classes)


def format_daily_prompt(name: str | None = None) -> str:
    """Create the 8:15 daily yes/no prompt."""
    if name:
        return f"Good morning {name}, do you want me to check for free coffee today?"

    return "Good morning, do you want me to check for free coffee today?"


def format_daily_no_message() -> str:
    """Create the daily opt-out answer."""
    return "Alright, have a good day!"


def format_direction_complete_message() -> str:
    """Create the final text after direction photos are sent."""
    return "Enjoy your Free Coffee,\nCoffree. ☕"


def format_location_details(classroom: str) -> str:
    """Create a helpful follow-up for one location."""
    profile = get_location_details(classroom)

    if profile is None:
        return f"{classroom}\nI do not have extra directions for this room yet. ☕"

    lines = [f"Here is how to find {classroom}. ☕"]

    name = cleaned_name(profile)
    if name:
        lines.append(name)

    building_level = profile_building_level_text(profile)
    if building_level:
        lines.append(building_level)

    for hint in profile_hints(profile, repeat_count=1):
        lines.append(f"- {hint}")

    return "\n".join(lines)


def format_other_locations(coffee_classes: list[str], coffee_label: str = "today") -> str:
    """Create a follow-up list of other coffee locations."""
    if not coffee_classes:
        return f"No other coffee locations found for {coffee_label}. ☕"

    lines = [f"Other coffee spots {coffee_label} ☕"]

    for classroom in coffee_classes:
        lines.append(location_line(classroom))

    return "\n".join(lines)


def format_coffee_message(
    date_text: str,
    coffee_classes: list[str],
    name: str | None = None,
    repeat_count: int = 0,
) -> str:
    """Create the message students will see."""
    if not coffee_classes:
        return f"Hi{name and ' ' + name or ''}! No free coffee locations found for {date_text}. ☕"

    if len(coffee_classes) == 1 and repeat_count == 0:
        classroom = coffee_classes[0]
        return "\n".join(
            [
                f"{greeting_for(name)}! Craving coffee right now? I got you. ☕",
                f"Head to {location_summary(classroom)}.",
                "Recommended timing: 9:15am onwards.",
                "Tap “Where is this?” if you want help finding the room.",
            ]
        )

    if repeat_count > 0:
        lines = [f"Hey{name and ' ' + name or ''}, coffee update for {date_text}: ☕"]
    else:
        lines = [
            f"{greeting_for(name)}, your fresh free coffee update is here for {date_text}. ☕",
            "Recommended timing: 9:15am onwards.",
        ]

    for classroom in coffee_classes:
        lines.append(location_line(classroom, repeat_count))

    lines.append("Ask me for more details if you need help finding the room.")

    return "\n".join(lines)


def format_recommendation_message(
    recommended_location: str,
    destination_text: str,
    name: str | None = None,
    coffee_label: str = "today",
) -> str:
    """Create the main route-aware recommendation."""
    return "\n".join(
        [
            f"{greeting_for(name)}! For {coffee_label}, since you’re heading to {destination_text}, I’d grab coffee here. ☕",
            f"{location_summary(recommended_location)}.",
            "Recommended timing: 9:15am onwards.",
            "Tap “Where is this?” if you want help finding the room.",
        ]
    )


def format_unknown_destination_message(
    name: str | None = None,
    coffee_classes: list[str] | None = None,
    coffee_label: str = "today",
) -> str:
    """Help the student recover when their destination is unclear."""
    greeting = f"Hey {name}" if name else "Hey"
    lines = [
        f"{greeting}, I’m not sure where that class is yet. ☕",
    ]

    if coffee_classes:
        lines.append(f"Free coffee {coffee_label} starts here:")
        lines.extend(location_line(classroom) for classroom in coffee_classes)
    else:
        lines.append(f"I do not see any free coffee locations for {coffee_label} yet.")

    lines.extend(
        [
            "",
            "You can ask: where can I get free coffee today?",
            "If you want the best stop before class, tell me your building and level like B1 L4.",
            "SUTD locations should be Building 1-5 and Level 1-7.",
        ]
    )

    return "\n".join(lines)
