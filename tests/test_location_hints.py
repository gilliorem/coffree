from src.location_hints import (
    describe_location,
    direction_photos,
    explain_room_number,
    find_class_profile,
    first_profile_photo,
    profile_building_level_text,
    profile_hints,
    profile_photos,
    read_class_profiles,
)


EXPECTED_FIELDS = {"class_id", "name", "building", "level", "hint_1", "photo_folder"}


def test_finds_profile_by_schedule_class_id():
    profile = find_class_profile("TT24/25")

    assert profile is not None
    assert profile["class_id"] == "TT24/25"
    assert profile["name"] == "TT24-25: 2.503 & 2.504"
    assert profile["building"] == "2"
    assert profile["level"] == "5"
    assert profile_building_level_text(profile) == "Building 2, Level 5"


def test_finds_profile_by_common_name():
    profile = find_class_profile("TT24-25: 2.503 & 2.504")

    assert profile is not None
    assert profile["class_id"] == "TT24/25"


def test_first_request_returns_first_hint_only():
    profile = find_class_profile("TT24/25")

    assert profile_hints(profile) == ["Above the drone area"]


def test_repeat_request_does_not_invent_extra_hints():
    profile = find_class_profile("TT24/25")

    assert profile_hints(profile, repeat_count=1) == ["Above the drone area"]


def test_first_request_returns_two_direction_photos():
    profile = find_class_profile("TT24/25")
    photos = profile_photos(profile)

    assert len(photos) == 2
    assert photos[0].startswith("data/class-direction-photo/b2-l5-tt24-tt25-ep-class/")


def test_first_profile_photo_returns_first_direction_photo():
    profile = find_class_profile("TT24/25")

    assert first_profile_photo(profile).startswith(
        "data/class-direction-photo/b2-l5-tt24-tt25-ep-class/"
    )


def test_repeat_request_returns_more_direction_photos():
    profile = find_class_profile("TT24/25")

    assert len(profile_photos(profile, repeat_count=1)) == 4


def test_direction_photos_for_building_1_start_at_2300_and_end_at_buffet():
    profile = find_class_profile("1.311A")
    photos = direction_photos(profile)

    assert photos[0].endswith("IMG_2300.JPG")
    assert photos[-1].endswith("buffet.png")


def test_direction_photos_for_building_2_end_at_buffet():
    profile = find_class_profile("TT24/25")
    photos = direction_photos(profile)

    assert photos[0].endswith("IMG_2276.PNG")
    assert photos[-1].endswith("buffet.png")


def test_unknown_location_returns_raw_location():
    assert describe_location("Unknown Room") == "Unknown Room"


def test_explains_simple_room_number():
    assert explain_room_number("2.612A") == {
        "class_id": "2.612A",
        "name": "",
        "building": "2",
        "level": "6",
        "hint_1": "",
        "photo_folder": "",
    }


def test_describes_simple_room_number():
    assert describe_location("3.205") == "3.205 - Building 3, Level 2"


def test_location_hint_data_uses_simplified_schema():
    for profile in read_class_profiles():
        assert set(profile) == EXPECTED_FIELDS
        assert profile["class_id"]
        assert profile["name"]
        assert profile["building"] in {"1", "2"}
        assert profile["level"] in {"1", "2", "3", "4", "5", "6", "7"}
        assert not profile["photo_folder"] or profile["photo_folder"].startswith(
            "data/class-direction-photo/"
        )
