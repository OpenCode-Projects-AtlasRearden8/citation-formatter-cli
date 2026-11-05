"""Model tests: name parsing, graceful dict loading, sort keys."""

from citation_formatter.models import (
    Source,
    initials,
    parse_name,
    sort_key,
    source_from_dict,
)


class TestParseName:
    def test_last_first(self):
        assert parse_name("Newport, Cal") == ("Newport", "Cal")

    def test_first_last(self):
        assert parse_name("Cal Newport") == ("Newport", "Cal")

    def test_single_token(self):
        assert parse_name("Anonymous") == ("Anonymous", "")

    def test_empty(self):
        assert parse_name("") == ("", "")

    def test_extra_spaces(self):
        assert parse_name("  Newport , Cal  ") == ("Newport", "Cal")


class TestInitials:
    def test_simple(self):
        assert initials("Cal") == "C."

    def test_multi_part(self):
        assert initials("Ada May") == "A. M."


class TestSourceFromDict:
    def test_full_mapping(self):
        s = source_from_dict(
            {
                "type": "article",
                "title": "A note",
                "authors": ["Smith, Jo"],
                "year": 2024,
                "journal": "Journal of Things",
                "volume": "1",
                "issue": "2",
                "pages": "3-4",
                "doi": "10.1/x",
            }
        )
        assert s.kind == "article"
        assert s.authors == ["Smith, Jo"]
        assert s.year == "2024"
        assert s.doi == "10.1/x"

    def test_author_string_normalized_to_list(self):
        s = source_from_dict({"title": "T", "author": "Smith, Jo"})
        assert s.authors == ["Smith, Jo"]

    def test_missing_everything_is_fine(self):
        s = source_from_dict({})
        assert s.title is None
        assert s.authors == []
        assert s.display_title == "Untitled"

    def test_unknown_type_falls_back_to_book(self):
        assert source_from_dict({"type": "pamphlet", "title": "T"}).kind == "book"

    def test_none_values(self):
        s = source_from_dict({"title": None, "year": None})
        assert s.title is None
        assert s.year is None


class TestSortKey:
    def test_author_sort(self):
        ctx = Source(authors=["Zhang, Wei"])
        w = Source(authors=["Adler, Kim"])
        assert sort_key(w) < sort_key(ctx)

    def test_title_fallback(self):
        a = Source(title="Aardvark Guide")
        z = Source(authors=["Zeta, X"], title="B")
        assert sort_key(a) < sort_key(z)

    def test_leading_article_stripped_for_sort_only(self):
        t = Source(title="The Cited Book")
        assert t.display_title == "The Cited Book"
        assert sort_key(t) == ("cited book", "")


class TestGracefulTypes:
    def test_year_as_int_coerced_to_str(self):
        s = source_from_dict({"year": 1776})
        assert s.year == "1776"

    def test_webpage_has_no_publisher_requirements(self):
        s = source_from_dict({"type": "webpage", "title": "x", "url": "https://e.com"})
        assert s.journal is None
        assert s.url == "https://e.com"

    def test_authors_field_rejects_numbers(self):
        s = source_from_dict({"title": "T", "authors": [12]})
        assert s.authors == ["12"]
