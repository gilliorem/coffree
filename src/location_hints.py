"""Look up simple class profiles for SUTD coffee locations."""

from __future__ import annotations

import json
import re
from pathlib import Path


LOCATION_DATABASE = Path("data/location-hints.json")
PROFILE_FIELDS = {"class_id", "name", "building", "level", "hint_1", "photo_folder"}

_PROFILE_CACHE: dict[str, tuple[float, list[dict[str, str]]]] = {}


def clean_key(value: str) -> str:
    """Normalize a user/location value for matching."""
    return " ".join(value.strip().upper().split())


def normalize_profile(profile: dict[str, object]) -> dict[str, str]:
    """Convert one JSON profile into the app's string-based profile shape."""
    return {
        "class_id": str(profile.get("class_id", "")).strip(),
        "name": str(profile.get("name", "")).strip(),
        "building": str(profile.get("building", "")).strip(),
        "level": str(profile.get("level", "")).strip(),
        "hint_1": str(profile.get("hint_1", "")).strip(),
        "photo_folder": str(profile.get("photo_folder", "")).strip(),
    }


def read_class_profiles(
    database_file: Path | str = LOCATION_DATABASE,
) -> list[dict[str, str]]:
    """Read every class profile from the JSON location database."""
    path = Path(database_file)
    key = str(path)
    mtime = path.stat().st_mtime

    cached = _PROFILE_CACHE.get(key)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    with path.open(encoding="utf-8") as file:
        profiles = json.load(file)

    normalized = [normalize_profile(profile) for profile in profiles]
    _PROFILE_CACHE[key] = (mtime, normalized)
    return normalized


def profile_keys(profile: dict[str, str]) -> list[str]:
    """Return searchable names for one class profile."""
    keys = [profile["class_id"]]

    if profile["name"]:
        keys.append(profile["name"])

    return [clean_key(key) for key in keys]


def find_class_profile(raw_location: str) -> dict[str, str] | None:
    """Find a class profile by schedule class ID or common name."""
    wanted_key = clean_key(raw_location)

    for profile in read_class_profiles():
        if wanted_key in profile_keys(profile):
            return profile

    return explain_room_number(raw_location)


def explain_room_number(raw_location: str) -> dict[str, str] | None:
    """Create a simple profile for a room number like 2.612A."""
    match = re.fullmatch(r"(\d)\.(\d)\d{2}[A-Z]?", raw_location.strip())

    if match is None:
        return None

    building = match.group(1)
    level = match.group(2)

    return {
        "class_id": raw_location,
        "name": "",
        "building": building,
        "level": level,
        "hint_1": "",
        "photo_folder": "",
    }


def get_location_details(raw_location: str) -> dict[str, str] | None:
    """Compatibility wrapper used by formatting code."""
    return find_class_profile(raw_location)


def profile_building_level(profile: dict[str, str]) -> tuple[str, str]:
    """Return building and level from a profile."""
    return profile["building"], profile["level"]


def profile_building_level_text(profile: dict[str, str]) -> str:
    """Return a readable building/level label."""
    building, level = profile_building_level(profile)

    if not building or not level:
        return ""

    return f"Building {building}, Level {level}"


def profile_hints(profile: dict[str, str], repeat_count: int = 0) -> list[str]:
    """Return location hints for one profile."""
    return [profile["hint_1"]] if profile["hint_1"] else []


def profile_photo_limit(repeat_count: int = 0) -> int:
    """Return how many photos to show for this request level."""
    if repeat_count > 0:
        return 4

    return 2


def direction_photos(profile: dict[str, str]) -> list[str]:
    """Return all direction photo paths in walking order."""
    if not profile["photo_folder"]:
        return []

    folder = Path(profile["photo_folder"])
    if not folder.exists():
        return []

    photos = sorted(
        path
        for path in folder.iterdir()
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )

    buffet_photos = [path for path in photos if path.name.lower() == "buffet.png"]
    route_photos = [path for path in photos if path.name.lower() != "buffet.png"]

    if profile["building"] == "1":
        first_photos = [path for path in route_photos if path.name == "IMG_2300.JPG"]
        route_photos = first_photos + [path for path in route_photos if path.name != "IMG_2300.JPG"]

    return [str(path) for path in route_photos + buffet_photos]


def profile_photos(profile: dict[str, str], repeat_count: int = 0) -> list[str]:
    """Return a limited set of direction photo paths for preview use."""
    photos = direction_photos(profile)
    return photos[: profile_photo_limit(repeat_count)]


def first_profile_photo(profile: dict[str, str]) -> str | None:
    """Return the first direction photo for a class profile."""
    photos = profile_photos(profile)

    if not photos:
        return None

    return photos[0]


def describe_location(raw_location: str) -> str:
    """Return a short readable location description for AI context."""
    profile = find_class_profile(raw_location)

    if profile is None:
        return raw_location

    parts = [raw_location]

    if profile["name"] and profile["name"] != raw_location:
        parts.append(profile["name"])

    building_level = profile_building_level_text(profile)
    if building_level:
        parts.append(building_level)

    hints = profile_hints(profile)
    if hints:
        parts.append(hints[0])

    return " - ".join(parts)
