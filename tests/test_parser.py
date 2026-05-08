from pathlib import Path

from src.parser import (
    classroom_column_indexes,
    extract_locations_from_row,
    get_locations_for_date,
    is_valid_location,
)


SCHEDULE_PATH = Path("data/PM_Schedule.csv")


def test_classroom_column_indexes_only_uses_classroom_headers():
    header = ["DATE", "EVENT 1", "CLASSROOM", "Shift 1", "EVENT 2", "CLASSROOM"]

    assert classroom_column_indexes(header) == [2, 5]


def test_extract_locations_from_row_ignores_event_and_shift_columns():
    row = [
        "8-May-26",
        "Fake event TT99",
        "TT19",
        "APM TT88",
        "Other event",
        "Zoom",
        "TT24/25",
    ]

    assert extract_locations_from_row(row, [2, 5, 6]) == ["TT19", "TT24/25"]


def test_get_locations_for_readme_example_date():
    assert get_locations_for_date("8-May-26", SCHEDULE_PATH) == [
        "TT19",
        "TT24/25",
        "TT20",
    ]


def test_get_locations_keeps_valid_room_formats():
    assert get_locations_for_date("18-May-26", SCHEDULE_PATH) == [
        "1.311A",
        "2.612A",
        "TT31 - 32",
    ]


def test_is_valid_location_filters_remote_and_offsite_values():
    assert not is_valid_location("Zoom")
    assert not is_valid_location("Online")
    assert not is_valid_location("Offsite")
    assert is_valid_location("Comp Lab 1.611")
