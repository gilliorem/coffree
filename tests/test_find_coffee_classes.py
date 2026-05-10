from src.find_coffee_classes import find_coffee_classes_for_date, is_coffee_classroom


def test_finds_classes_for_readme_example_date():
    assert find_coffee_classes_for_date("8-May-26") == [
        "TT19",
        "TT24/25",
        "TT20",
    ]


def test_ignores_remote_and_offsite_classrooms():
    assert not is_coffee_classroom("")
    assert not is_coffee_classroom("Zoom")
    assert not is_coffee_classroom("Online")
    assert not is_coffee_classroom("Offsite")


def test_keeps_simple_physical_classrooms():
    assert is_coffee_classroom("TT19")
    assert is_coffee_classroom("2.612A")
    assert is_coffee_classroom("Comp Lab 1.611")
