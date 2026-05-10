from src.recommend_coffee import recommend_location, score_location
from src.student_destination import parse_destination


def test_recommend_location_prefers_same_building_and_level():
    destination = parse_destination("Building 2 Level 5")

    assert recommend_location(["TT19", "TT24/25", "2.612A"], destination) == "TT24/25"


def test_score_location_rewards_same_building():
    destination = parse_destination("Building 2 Level 5")

    assert score_location("TT24/25", destination) > score_location("TT19", destination)
