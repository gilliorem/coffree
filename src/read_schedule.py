"""Read the workshop schedule CSV.

This file does only one thing: open the CSV file.
It returns the header and rows exactly as they appear in the CSV.
The result is cached and only re-parsed when the file changes on disk.
"""

from __future__ import annotations

import csv
from pathlib import Path


SCHEDULE_FILE = Path("data/PM_Schedule.csv")

_CACHE: dict[str, tuple[float, list[str], list[list[str]]]] = {}


def read_schedule(schedule_file: Path | str = SCHEDULE_FILE) -> tuple[list[str], list[list[str]]]:
    """Return the CSV header and all schedule rows.

    We keep rows as lists because the CSV has many columns named CLASSROOM.
    A dictionary would lose repeated column names.
    """
    path = Path(schedule_file)
    key = str(path)
    mtime = path.stat().st_mtime

    cached = _CACHE.get(key)
    if cached is not None and cached[0] == mtime:
        return cached[1], cached[2]

    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        header = next(reader)
        rows = list(reader)

    _CACHE[key] = (mtime, header, rows)
    return header, rows
