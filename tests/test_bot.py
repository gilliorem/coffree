from src.bot import build_locations_message, parse_schedule_date, schedule_date_from_date


def test_build_locations_message_lists_locations():
    message = build_locations_message("8-May-26", "data/PM_Schedule.csv")

    assert message == "\n".join(
        [
            "Free coffee locations for 8-May-26:",
            "- TT19",
            "- TT24/25",
            "- TT20",
        ]
    )


def test_build_locations_message_handles_no_locations():
    assert (
        build_locations_message("7-May-23", "data/PM_Schedule.csv")
        == "No free coffee locations found for 7-May-23."
    )


def test_parse_schedule_date_accepts_iso_date():
    assert parse_schedule_date("2026-05-08") == "8-May-26"


def test_parse_schedule_date_preserves_schedule_format():
    assert parse_schedule_date("8-May-26") == "8-May-26"
