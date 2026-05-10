"""Find classroom locations that may have free coffee.

Prototype rule:
For one date, look only at columns named CLASSROOM.
If the classroom value is not remote/offsite/empty, show it to students.
"""

from __future__ import annotations

from pathlib import Path

from src.read_schedule import SCHEDULE_FILE, read_schedule


DATE_COLUMN = "DATE"
CLASSROOM_COLUMN = "CLASSROOM"

IGNORE_CLASSROOMS = {
    "",
    "NA",
    "OFFSITE",
    "OFFISTE",
    "ONLINE",
    "OVERSEAS",
    "ZOOM",
    "ZOOM (SCA)",
    "SA",
    "Offsite",
    "LTR+LL"
}


def clean_text(value: str) -> str:
    """Remove extra spaces and newlines from one CSV cell."""
    return " ".join(value.strip().split())


def is_coffee_classroom(classroom: str) -> bool:
    """Return True when a CLASSROOM cell looks useful for students."""
    return clean_text(classroom).upper() not in IGNORE_CLASSROOMS


def add_once(values: list[str], new_value: str) -> None:
    """Add a value only if it is not already in the list."""
    if new_value not in values:
        values.append(new_value)


def find_column_indexes(header: list[str], wanted_column: str) -> list[int]:
    """Find every column index with a specific header name."""
    indexes: list[int] = []

    for index, column_name in enumerate(header):
        if column_name == wanted_column:
            indexes.append(index)

    return indexes


def find_coffee_classes_for_date(
    date_text: str,
    schedule_file: Path | str = SCHEDULE_FILE,
) -> list[str]:
    """Return classroom values for one date, for example '8-May-26'."""
    header, rows = read_schedule(schedule_file)
    date_index = header.index(DATE_COLUMN)
    classroom_indexes = find_column_indexes(header, CLASSROOM_COLUMN)
    coffee_classes: list[str] = []

    for row in rows:
        if row[date_index].strip() != date_text:
            continue

        for classroom_index in classroom_indexes:
            classroom = clean_text(row[classroom_index])
            if is_coffee_classroom(classroom):
                add_once(coffee_classes, classroom)

        return coffee_classes

    return []


if __name__ == "__main__":
    for classroom in find_coffee_classes_for_date("8-May-26"):
        print(classroom)
