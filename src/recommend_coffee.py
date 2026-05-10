"""Recommend the best coffee location for a student's next destination."""

from __future__ import annotations

from src.location_hints import find_class_profile, first_profile_photo, profile_building_level
from src.student_destination import Destination


def score_location(classroom: str, destination: Destination) -> int:
    """Score a coffee stop relative to where the student is heading."""
    profile = find_class_profile(classroom)

    if profile is None:
        return -2

    building, level = profile_building_level(profile)
    score = 0

    if destination.building and building == destination.building:
        score += 5

    if destination.level and level == destination.level:
        score += 3

    if destination.building and destination.level and building == destination.building and level == destination.level:
        score += 5

    if first_profile_photo(profile) is not None:
        score += 1

    return score


def recommend_location(coffee_classes: list[str], destination: Destination) -> str | None:
    """Return the highest-scoring coffee location."""
    if not coffee_classes:
        return None

    return max(coffee_classes, key=lambda classroom: score_location(classroom, destination))


def order_locations_by_destination(
    coffee_classes: list[str],
    destination: Destination,
) -> list[str]:
    """Return coffee locations ordered from most useful to least useful."""
    return sorted(
        coffee_classes,
        key=lambda classroom: score_location(classroom, destination),
        reverse=True,
    )
