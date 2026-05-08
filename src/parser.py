"""Parse coffee locations from the SUTD Academy programme schedule CSV."""

from __future__ import annotations

import csv
import re
from pathlib import Path


DEFAULT_SCHEDULE_PATH = Path("data/PM_Schedule.csv")
DATE_COLUMN = "DATE"
CLASSROOM_COLUMN = "CLASSROOM"

IGNORED_LOCATIONS = {
    "",
    "NA",
    "N/A",
    "NIL",
    "NONE",
    "OFFSITE",
    "ONLINE",
    "OVERSEAS",
    "ZOOM",
    "ZOOM (SCA)",
}

LOCATION_PATTERNS = (
    re.compile(r"^TT\s*\d+(?:\s*(?:/|-|&)\s*\d+)*$", re.IGNORECASE),
    re.compile(r"^CC\s*\d+(?:\s*/\s*\d+)?$", re.IGNORECASE),
    re.compile(r"^\d\.\d{3}[A-Z]?$", re.IGNORECASE),
    re.compile(r".*\b(?:COMP\s+LAB|TRAINING\s+ROOM|LIBRARY\s+TRAINING\s+ROOM)\b.*", re.IGNORECASE),
    re.compile(r"^LT\s*\d+$", re.IGNORECASE),
    re.compile(r"^LTR\s*(?:\+|&)\s*LL$", re.IGNORECASE),
    re.compile(r"^CAPSTONE\s+\d+\s*(?:/|&)\s*\d+$", re.IGNORECASE),
)


def classroom_column_indexes(header: list[str]) -> list[int]:
    """Return indexes for repeated CLASSROOM columns only."""
    return [
        index
        for index, column_name in enumerate(header)
        if column_name.strip().upper() == CLASSROOM_COLUMN
    ]


def normalize_location(value: str) -> str:
    """Normalize spacing in a classroom value while preserving readable labels."""
    return " ".join(value.strip().split())


def is_valid_location(value: str) -> bool:
    """Return whether a classroom cell should be treated as a coffee location."""
    normalized = normalize_location(value)
    if normalized.upper() in IGNORED_LOCATIONS:
        return False
    return any(pattern.match(normalized) for pattern in LOCATION_PATTERNS)


def extract_locations_from_row(row: list[str], classroom_indexes: list[int]) -> list[str]:
    """Extract unique valid classroom locations from one schedule row."""
    locations: list[str] = []
    seen: set[str] = set()

    for index in classroom_indexes:
        if index >= len(row):
            continue

        location = normalize_location(row[index])
        key = location.upper()
        if is_valid_location(location) and key not in seen:
            locations.append(location)
            seen.add(key)

    return locations


def get_locations_for_date(
    target_date: str,
    schedule_path: Path | str = DEFAULT_SCHEDULE_PATH,
) -> list[str]:
    """Return coffee locations for a date such as '8-May-26'."""
    path = Path(schedule_path)

    with path.open(newline="", encoding="utf-8-sig") as schedule_file:
        reader = csv.reader(schedule_file)
        header = next(reader)
        classroom_indexes = classroom_column_indexes(header)
        date_index = header.index(DATE_COLUMN)

        for row in reader:
            if date_index < len(row) and row[date_index].strip() == target_date:
                return extract_locations_from_row(row, classroom_indexes)

    return []


if __name__ == "__main__":
    for location in get_locations_for_date("8-May-26"):
        print(location)
