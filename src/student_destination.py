"""Parse where a student is heading next."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.location_hints import find_class_profile, profile_building_level, profile_keys, read_class_profiles


MAX_BUILDING = 5
MAX_LEVEL = 7


@dataclass(frozen=True)
class Destination:
    """Simple destination information used for ranking coffee stops."""

    raw_text: str
    building: str
    level: str


def valid_building_level(building: str, level: str) -> bool:
    """Return True when a building/level pair can exist in SUTD."""
    if building and (not building.isdigit() or not 1 <= int(building) <= MAX_BUILDING):
        return False

    if level and level != "B" and (not level.isdigit() or not 1 <= int(level) <= MAX_LEVEL):
        return False

    return bool(building or level)


def clean_building_level(building: str, level: str) -> tuple[str, str]:
    """Drop building/level values outside the SUTD range."""
    building = building.strip()
    level = level.strip().upper()

    if not valid_building_level(building, level):
        return "", ""

    return building, level


def parse_building_level(text: str) -> tuple[str, str]:
    """Find building and level words in user text."""
    lower_text = text.lower()
    building = ""
    level = ""

    compact_match = re.fullmatch(
        r"\s*(?:building|b)?\s*([1-9])\s*(?:level|lvl|floor|l)?\s*([1-9])\s*",
        lower_text,
    )
    if compact_match:
        return clean_building_level(compact_match.group(1), compact_match.group(2))

    level_only_match = re.fullmatch(
        r"\s*([1-9])\s*(?:level|lvl|floor|l)\s*([1-9])\s*",
        lower_text,
    )
    if level_only_match:
        return clean_building_level(level_only_match.group(1), level_only_match.group(2))

    building_match = re.search(r"\b(?:building|b)\s*([1-9])", lower_text)
    if building_match:
        building = building_match.group(1)

    level_match = re.search(r"\b(?:level|lvl|l|floor)\s*([b]?\d|b)\b", lower_text)
    if level_match:
        level = level_match.group(1).upper()

    floor_match = re.search(r"\b([1-9])(?:st|nd|rd|th)\s+floor\b", lower_text)
    if floor_match:
        level = floor_match.group(1)

    return clean_building_level(building, level)


def parse_room_number(text: str) -> tuple[str, str]:
    """Parse a room number like 2.612A into building 2 and level 6."""
    match = re.search(r"\b([1-9])\.([0-9])\d{2}[A-Z]?\b", text.upper())

    if match is None:
        return "", ""

    return clean_building_level(match.group(1), match.group(2))


def parse_profile_location(text: str) -> tuple[str, str]:
    """Use the location database when the user types a class ID or common name."""
    profile = find_class_profile(text)

    if profile is None:
        return "", ""

    return profile_building_level(profile)


def normalize_sentence(text: str) -> str:
    """Normalize text so known locations can be matched inside longer sentences."""
    return " ".join(re.sub(r"[^A-Za-z0-9.]+", " ", text.upper()).split())


def extract_known_destination(user_text: str) -> str:
    """Find the best known class/location phrase inside a full sentence."""
    normalized_text = f" {normalize_sentence(user_text)} "
    candidates: list[str] = []

    for profile in read_class_profiles():
        candidates.extend(profile_keys(profile))

    candidates = sorted(set(candidates), key=len, reverse=True)

    for candidate in candidates:
        normalized_candidate = normalize_sentence(candidate)
        if f" {normalized_candidate} " in normalized_text:
            return candidate

    room_match = re.search(r"\b[1-9]\.[0-9]\d{2}[A-Z]?\b", user_text.upper())
    if room_match:
        return room_match.group(0)

    return user_text


def parse_destination(user_text: str) -> Destination:
    """Convert a student's answer into a destination."""
    destination_text = extract_known_destination(user_text)
    building, level = parse_room_number(destination_text)

    if not building and not level:
        building, level = parse_profile_location(destination_text)

    if not building and not level:
        building, level = parse_building_level(destination_text)

    return Destination(raw_text=destination_text.strip(), building=building, level=level)


def has_destination(destination: Destination) -> bool:
    """Return True when we know enough to rank coffee locations."""
    return bool(destination.building or destination.level)
