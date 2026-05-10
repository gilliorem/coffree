from src.format_message import (
    format_daily_no_message,
    format_daily_prompt,
    format_direction_complete_message,
    format_coffee_message,
    format_location_details,
    format_onboarding_location_list,
    format_onboarding_recommendation,
    format_other_locations,
    format_unknown_destination_message,
)


def test_formats_coffee_locations():
    message = format_coffee_message("today", ["TT19", "TT24/25"], name="Remi")

    assert message == "\n".join(
        [
            "Good morning Remi, your fresh free coffee update is here for today. ☕",
            "Recommended timing: 9:15am onwards.",
            "- TT19 — Think Tank 19 — Building 2, Level 3",
            "- TT24/25 — Building 2, Level 5 — Above the drone area",
            "Ask me for more details if you need help finding the room.",
        ]
    )


def test_formats_empty_result():
    message = format_coffee_message("today", [], name="Remi")

    assert message == "Hi Remi! No free coffee locations found for today. ☕"


def test_formats_single_location_like_a_recommendation():
    message = format_coffee_message("today", ["TT24/25"], name="Remi")

    assert message == "\n".join(
        [
            "Good morning Remi! Craving coffee right now? I got you. ☕",
            "Head to TT24/25 — Building 2, Level 5 — Above the drone area.",
            "Recommended timing: 9:15am onwards.",
            "Tap “Where is this?” if you want help finding the room.",
        ]
    )


def test_formats_location_details_follow_up():
    message = format_location_details("TT24/25")

    assert "Here is how to find TT24/25. ☕" in message
    assert "TT24-25: 2.503 & 2.504" not in message
    assert "- Above the drone area" in message


def test_formats_other_locations_follow_up():
    message = format_other_locations(["TT20"])

    assert message.startswith("Other coffee spots today ☕")
    assert "TT20" in message


def test_formats_unknown_destination_message():
    message = format_unknown_destination_message("Remi")

    assert "I’m not sure where that class is yet" in message
    assert "B1 L4" in message


def test_formats_onboarding_recommendation():
    message = format_onboarding_recommendation("TT24/25")

    assert "You can grab your free coffee here in TT24/25, Building 2, Level 5" in message
    assert "data/class-direction-photo" not in message
    assert "Recommended timing: 9:15am onwards." in message
    assert "Tap “Where is this?”" in message


def test_formats_onboarding_location_list_with_spacing():
    message = format_onboarding_location_list(["TT19", "TT24/25"])

    assert message == "\n\n".join(
        [
            "- TT19: Think Tank 19 Building 2 Level 3",
            "- TT24/25 Building 2 Level 5 (Above the drone area)",
        ]
    )


def test_formats_daily_prompt_and_closing_messages():
    assert format_daily_prompt("Remi") == "Good morning Remi, do you want me to check for free coffee today?"
    assert format_daily_no_message() == "Alright, have a good day!"
    assert format_direction_complete_message() == "Enjoy your Free Coffee,\nCoffree. ☕"
