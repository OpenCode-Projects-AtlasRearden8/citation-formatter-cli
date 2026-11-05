"""Back-matter tests: KDP-style plain-English 'About the Sources' output."""

from citation_formatter.backmatter import ABOUT_HEADING, build_backmatter
from tests.fixtures import FULL_ARTICLE, FULL_BOOK, MINIMAL_BOOK, SAMPLE_SOURCES


def _release(text: str) -> str:
    return "\n".join(line.strip() for line in text.strip().split("\n"))


def test_heading_present():
    text = build_backmatter(SAMPLE_SOURCES, "APA")
    assert ABOUT_HEADING in text.split("\n")


def test_intro_speaks_in_plain_english():
    text = build_backmatter([MINIMAL_BOOK])
    assert "plain terms" in text
    assert "format_bibliography" not in text


def test_each_source_gets_numbered_description_and_citation():
    text = build_backmatter([FULL_BOOK, FULL_ARTICLE], "APA")
    assert "1. " in text and "2. " in text
    assert "Newport, C." in text  # formal citation paired underneath
    assert "A book by Newport, Cal, 2016" in text

def test_note_field_is_used_when_present():
    source = FULL_BOOK
    source.note = "Background for the focused-work chapter."
    text = build_backmatter([source])
    assert "Background for the focused-work chapter." in text


def test_minimal_source_gets_graceful_line():
    text = build_backmatter([MINIMAL_BOOK])
    assert "an unsigned piece" in text
    assert "Cited as background" in text


def test_disclaimer_included():
    text = build_backmatter([FULL_BOOK])
    assert "does not mean the source endorses" in text


def test_sources_sorted_by_author():
    raw = build_backmatter([FULL_ARTICLE, FULL_BOOK])
    assert raw.index("Newport") < raw.index("Rivera")
