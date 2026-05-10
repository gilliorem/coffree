from src.student_destination import extract_known_destination, has_destination, parse_destination


def test_parse_building_and_level():
    destination = parse_destination("Building 2 Level 5")

    assert destination.building == "2"
    assert destination.level == "5"


def test_parse_compact_building_and_level_formats():
    examples = [
        "b1l5",
        "B1 L5",
        "Building 1 Level 5",
        "1 l5",
        "1 5",
        "15",
    ]

    for example in examples:
        destination = parse_destination(example)
        assert destination.building == "1"
        assert destination.level == "5"


def test_parse_building_and_level_rejects_impossible_sutd_values():
    assert not has_destination(parse_destination("Building 8 Level 11"))
    assert not has_destination(parse_destination("B6 L2"))
    assert not has_destination(parse_destination("B2 L9"))


def test_parse_room_number():
    destination = parse_destination("2.612A")

    assert destination.building == "2"
    assert destination.level == "6"


def test_parse_known_location_class_id():
    destination = parse_destination("Library")

    assert destination.building == "1"
    assert destination.level == "1"


def test_parse_42_classroom_id():
    destination = parse_destination("1.401")

    assert destination.building == "1"
    assert destination.level == "4"


def test_has_destination_rejects_unknown_classroom():
    assert not has_destination(parse_destination("some random class"))


def test_extract_known_destination_from_sentence():
    assert extract_known_destination("tomorrow i have design ai class in tt24/25 at 9:15") == "TT24/25"


def test_parse_destination_from_sentence_with_known_alias():
    destination = parse_destination("tomorrow i have design ai class in tt24/25 at 9:15")

    assert destination.raw_text == "TT24/25"
    assert destination.building == "2"
    assert destination.level == "5"
