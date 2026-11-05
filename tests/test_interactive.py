"""Interactive-mode helpers: author input parsing must not split 'Last, First'."""

from citation_formatter.cli import split_authors_input


def test_last_first_preserved():
    assert split_authors_input("Newport, Cal") == ["Newport, Cal"]


def test_multiple_authors_with_and():
    assert split_authors_input("Newport, Cal and Fisher, Ada") == [
        "Newport, Cal",
        "Fisher, Ada",
    ]


def test_multiple_authors_with_semicolon():
    assert split_authors_input("Rivera, Ana; Okafor, Chidi") == [
        "Rivera, Ana",
        "Okafor, Chidi",
    ]


def test_plain_first_last_falls_back_to_split():
    assert split_authors_input("Cal Newport and Ada Fisher") == [
        "Cal Newport",
        "Ada Fisher",
    ]


def test_blank_input_is_empty_list():
    assert split_authors_input("") == []
    assert split_authors_input("   ") == []
