import os
import asyncio
import sys
from types import ModuleType

from src.telegram_bot import (
    ONBOARD_ALL,
    ONBOARD_BUILDING_1,
    ONBOARD_BUILDING_2,
    ONBOARD_LEVEL_4_PLUS,
    action_button_specs,
    all_location_button_specs,
    build_coffee_locations_message,
    build_recommendation_message,
    build_location_details_reply,
    choose_location_for_onboarding,
    daily_yes_button_specs,
    choose_coffee_date,
    format_welcome_message,
    first_known_location,
    first_photo_for_locations,
    location_action_button_specs,
    onboarding_button_specs,
    send_direction_sequence,
    last_recommended_location,
    next_detail_count,
    remember_recommendation,
    remembered_other_locations,
    today_as_schedule_date,
    wants_coffee_locations,
    wants_directions,
)


def test_first_photo_for_locations_returns_known_location_photo():
    photo = first_photo_for_locations(["TT24/25"])

    assert photo is not None
    assert photo.startswith("data/class-direction-photo/b2-l5-tt24-tt25-ep-class/")


def test_first_photo_for_locations_skips_unknown_locations():
    photo = first_photo_for_locations(["Unknown Room"])

    assert photo is None


def test_first_known_location_skips_unknown_locations():
    assert first_known_location(["Unknown Room", "TT24/25"]) == "TT24/25"


def test_action_button_specs_include_where_and_other_locations():
    assert action_button_specs(["TT24/25", "TT20"]) == [
        ("Where is this?", "where:TT24/25"),
        ("Other locations", "others"),
    ]


def test_format_welcome_message_matches_onboarding_intro():
    message = format_welcome_message("Remi")

    assert message == "\n".join(
        [
            "Hey Remi, I’m Coffree. ☕",
            "I help you find the best free coffee stop before your next class.",
            "",
            "Where are you heading next?",
        ]
    )


def test_onboarding_button_specs_match_first_choices():
    assert onboarding_button_specs() == [
        ("Building 1", ONBOARD_BUILDING_1),
        ("Building 2", ONBOARD_BUILDING_2),
        ("Level 4 and above", ONBOARD_LEVEL_4_PLUS),
        ("Just give me the coffee location already!", ONBOARD_ALL),
    ]


def test_choose_location_for_onboarding_filters_today_locations():
    coffee_classes = ["TT19", "Comp Lab 1.611", "TT24/25"]

    assert choose_location_for_onboarding(ONBOARD_BUILDING_1, coffee_classes) == "Comp Lab 1.611"
    assert choose_location_for_onboarding(ONBOARD_BUILDING_2, coffee_classes) == "TT19"
    assert choose_location_for_onboarding(ONBOARD_LEVEL_4_PLUS, coffee_classes) == "Comp Lab 1.611"


def test_location_action_buttons_offer_directions_and_all_locations():
    assert location_action_button_specs("TT24/25") == [
        ("Get directions to this class", "directions:TT24/25"),
        ("Get all coffee locations", ONBOARD_ALL),
    ]


def test_all_location_buttons_use_known_locations_only():
    assert all_location_button_specs(["Unknown", "TT24/25"]) == [
        ("Need directions details for TT24/25", "directions:TT24/25")
    ]


def test_daily_yes_buttons_include_two_directions_and_more_locations():
    assert daily_yes_button_specs(["TT19", "TT24/25", "2.612A"]) == [
        ("Direction to TT19", "directions:TT19"),
        ("Direction to TT24/25", "directions:TT24/25"),
        ("More coffee locations", ONBOARD_ALL),
    ]


def test_today_as_schedule_date_can_use_demo_override():
    old_value = os.environ.get("COFFREE_DATE")
    os.environ["COFFREE_DATE"] = "8-May-26"

    try:
        assert today_as_schedule_date() == "8-May-26"
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_DATE", None)
        else:
            os.environ["COFFREE_DATE"] = old_value


def test_choose_coffee_date_defaults_to_today():
    old_value = os.environ.get("COFFREE_DATE")
    os.environ["COFFREE_DATE"] = "11-May-26"

    try:
        assert choose_coffee_date("I am going to TT24/25") == ("11-May-26", "today")
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_DATE", None)
        else:
            os.environ["COFFREE_DATE"] = old_value


def test_choose_coffee_date_accepts_tomorrow():
    old_value = os.environ.get("COFFREE_DATE")
    os.environ["COFFREE_DATE"] = "11-May-26"

    try:
        assert choose_coffee_date("tomorrow i have class in TT24/25") == ("12-May-26", "tomorrow")
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_DATE", None)
        else:
            os.environ["COFFREE_DATE"] = old_value


def test_build_recommendation_message_ranks_for_destination():
    old_value = os.environ.get("COFFREE_DATE")
    os.environ["COFFREE_DATE"] = "11-May-26"

    try:
        message, photo, ordered_locations, understood = build_recommendation_message("Building 2 Level 5", "Remi")
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_DATE", None)
        else:
            os.environ["COFFREE_DATE"] = old_value

    assert ordered_locations[0] == "TT24/25"
    assert "For today, since you’re heading to Building 2 Level 5" in message
    assert photo is not None
    assert understood


def test_build_recommendation_message_accepts_tomorrow_sentence():
    old_value = os.environ.get("COFFREE_DATE")
    os.environ["COFFREE_DATE"] = "11-May-26"

    try:
        message, photo, ordered_locations, understood = build_recommendation_message(
            "tomorrow i have design ai class in tt24/25 at 9:15",
            "Remi",
        )
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_DATE", None)
        else:
            os.environ["COFFREE_DATE"] = old_value

    assert ordered_locations[0] == "TT24/25"
    assert "For tomorrow, since you’re heading to TT24/25" in message
    assert photo is not None
    assert understood


def test_build_recommendation_message_can_reuse_destination_with_tomorrow_hint():
    old_value = os.environ.get("COFFREE_DATE")
    os.environ["COFFREE_DATE"] = "11-May-26"

    try:
        message, photo, ordered_locations, understood = build_recommendation_message(
            "Building 2 Level 5",
            "Remi",
            "tomorrow",
        )
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_DATE", None)
        else:
            os.environ["COFFREE_DATE"] = old_value

    assert ordered_locations[0] == "TT24/25"
    assert "For tomorrow, since you’re heading to Building 2 Level 5" in message
    assert photo is not None
    assert understood


def test_build_recommendation_message_asks_for_exact_format_when_unknown():
    old_value = os.environ.get("COFFREE_DATE")
    os.environ["COFFREE_DATE"] = "9-May-26"

    try:
        message, photo, ordered_locations, understood = build_recommendation_message(
            "random unknown class",
            "Remi",
        )
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_DATE", None)
        else:
            os.environ["COFFREE_DATE"] = old_value

    assert not understood
    assert "Free coffee today starts here:" in message
    assert "TT19" in message
    assert "where can I get free coffee today?" in message
    assert "B1 L4" in message
    assert "Building 1-5 and Level 1-7" in message
    assert photo is None
    assert ordered_locations == ["TT19", "Comp Lab 1.611"]


def test_build_coffee_locations_message_accepts_loose_question():
    old_value = os.environ.get("COFFREE_DATE")
    os.environ["COFFREE_DATE"] = "9-May-26"

    try:
        message, photo, coffee_classes, coffee_label = build_coffee_locations_message(
            "where is the coffee at",
            "Remi",
        )
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_DATE", None)
        else:
            os.environ["COFFREE_DATE"] = old_value

    assert coffee_label == "today"
    assert coffee_classes == ["TT19", "Comp Lab 1.611"]
    assert "TT19" in message
    assert photo is not None


def test_build_coffee_locations_message_accepts_tomorrow_question():
    old_value = os.environ.get("COFFREE_DATE")
    os.environ["COFFREE_DATE"] = "9-May-26"

    try:
        message, photo, coffee_classes, coffee_label = build_coffee_locations_message(
            "where can i get free coffee tomorrow",
            "Remi",
        )
    finally:
        if old_value is None:
            os.environ.pop("COFFREE_DATE", None)
        else:
            os.environ["COFFREE_DATE"] = old_value

    assert coffee_label == "tomorrow"
    assert coffee_classes == ["TT24/25", "2.612A"]
    assert "TT24/25" in message
    assert photo is not None


def test_wants_coffee_locations_accepts_many_phrasings():
    phrases = [
        "where is the coffee at",
        "where is coffee",
        "where coffee",
        "where can i get free coffee today?",
        "where can I get coffee",
        "where can i grab coffee",
        "where can i find coffee",
        "where can i find free coffee",
        "where is the free coffee",
        "free coffee today",
        "coffee location",
        "coffee locations",
        "coffee spot",
        "coffee spots",
        "coffee place",
        "coffee places",
        "any coffee today?",
        "got coffee?",
        "have coffee?",
        "need coffee",
        "coffee now",
    ]

    for phrase in phrases:
        assert wants_coffee_locations(phrase)


def test_wants_coffee_locations_rejects_destination_answer():
    assert not wants_coffee_locations("Building 2 Level 5")


def test_remember_recommendation_stores_last_destination_and_location():
    user_data = {}

    remember_recommendation(
        user_data,
        "Building 2 Level 5",
        "TT24/25",
        "tomorrow",
        ["TT24/25", "CC16"],
    )

    assert user_data["last_destination"] == "Building 2 Level 5"
    assert last_recommended_location(user_data) == "TT24/25"
    assert user_data["last_coffee_label"] == "tomorrow"
    assert remembered_other_locations(user_data) == ["CC16"]
    assert user_data["location_detail_count"] == 0


def test_next_detail_count_increments_per_user():
    user_data = {}

    assert next_detail_count(user_data) == 1
    assert next_detail_count(user_data) == 2


def test_wants_directions_accepts_loose_phrases():
    phrases = [
        "where",
        "where is this",
        "whr?",
        "how go there",
        "how to get there",
        "send map pls",
        "directions",
        "help me find the room",
        "which way",
    ]

    for phrase in phrases:
        assert wants_directions(phrase)


def test_wants_directions_rejects_destination_answer():
    assert not wants_directions("Building 2 Level 5")


def test_build_location_details_reply_uses_memory_counter():
    user_data = {"location_detail_count": 0}

    message, photo = build_location_details_reply(user_data, "TT24/25")

    assert "Here is how to find TT24/25" in message
    assert photo is not None
    assert user_data["location_detail_count"] == 1


def test_send_direction_sequence_uses_media_group_for_multiple_photos():
    class FakeInputMediaPhoto:
        def __init__(self, media):
            self.media = media

    class FakeTarget:
        def __init__(self):
            self.media_groups = []
            self.texts = []

        async def reply_media_group(self, media):
            self.media_groups.append(media)

        async def reply_text(self, text):
            self.texts.append(text)

    fake_telegram = ModuleType("telegram")
    fake_telegram.InputMediaPhoto = FakeInputMediaPhoto
    old_telegram = sys.modules.get("telegram")
    sys.modules["telegram"] = fake_telegram

    try:
        target = FakeTarget()
        asyncio.run(send_direction_sequence(target, "TT24/25"))
    finally:
        if old_telegram is None:
            sys.modules.pop("telegram", None)
        else:
            sys.modules["telegram"] = old_telegram

    assert len(target.media_groups) == 1
    assert len(target.media_groups[0]) == 4
    assert target.texts == ["Enjoy your Free Coffee,\nCoffree. ☕"]
