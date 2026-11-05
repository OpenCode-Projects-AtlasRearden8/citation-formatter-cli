"""Formatter tests: exact strings checked against APA 7 / MLA 9 / Chicago 17 / IEEE."""

import pytest

from citation_formatter.formatters import format_bibliography, format_citation
from tests.fixtures import (
    EDITED_BOOK,
    FULL_ARTICLE,
    FULL_BOOK,
    MINIMAL_ARTICLE,
    MINIMAL_BOOK,
    THREE_AUTHOR_BOOK,
    TWO_AUTHOR_BOOK,
    WEBPAGE,
)


class TestFullBook:
    def test_apa(self):
        assert format_citation(FULL_BOOK, "APA") == (
            "Newport, C. (2016). Deep Work: Rules for Focused Success in a "
            "Distracted World. Grand Central Publishing."
        )

    def test_mla(self):
        assert format_citation(FULL_BOOK, "MLA") == (
            "Newport, Cal. Deep Work: Rules for Focused Success in a "
            "Distracted World. Grand Central Publishing, 2016."
        )

    def test_chicago(self):
        assert format_citation(FULL_BOOK, "Chicago") == (
            "Newport, Cal. Deep Work: Rules for Focused Success in a "
            "Distracted World. Grand Central Publishing, 2016."
        )

    def test_ieee(self):
        assert format_citation(FULL_BOOK, "IEEE") == (
            "C. Newport, Deep Work: Rules for Focused Success in a "
            "Distracted World. Grand Central Publishing, 2016."
        )


class TestAuthorCountRules:
    def test_apa_three_authors_uses_ampersand_list(self):
        assert format_citation(THREE_AUTHOR_BOOK, "APA").startswith(
            "Lutz, M., Ascher, D., & Taylor, C. (2021)."
        )

    def test_mla_three_authors_uses_et_al(self):
        assert format_citation(THREE_AUTHOR_BOOK, "MLA").startswith(
            "Lutz, Mark, et al."
        )

    def test_chicago_three_authors_uses_et_al(self):
        assert format_citation(THREE_AUTHOR_BOOK, "Chicago").startswith(
            "Lutz, Mark, et al."
        )

    def test_apa_two_authors_comma_before_ampersand(self):
        assert format_citation(TWO_AUTHOR_BOOK, "APA").startswith(
            "Fisher, A., & Moore, B. (2020)."
        )

    def test_mla_two_authors_joined_with_and(self):
        assert format_citation(TWO_AUTHOR_BOOK, "MLA").startswith(
            "Fisher, Ada, and Ben Moore."
        )

    def test_ieee_authors_joined_with_and(self):
        assert format_citation(TWO_AUTHOR_BOOK, "IEEE").startswith(
            "A. Fisher, and B. Moore,"
        )


class TestMinimalBook:
    def test_no_author_no_year_all_styles(self):
        # No exceptions, no "[None]" ghosts, and a period-stable ending.
        expected = {
            "APA": "The Untitled Project (n.d.).",
            "MLA": "The Untitled Project. n.d.",
            "Chicago": "The Untitled Project. n.d.",
            "IEEE": "The Untitled Project. n.d.",
        }
        for style, want in expected.items():
            assert format_citation(MINIMAL_BOOK, style) == want


class TestArticles:
    def test_apa_full_article(self):
        assert format_citation(FULL_ARTICLE, "APA") == (
            "Rivera, A., Okafor, C., & Zhang, W. (2024). Prompt engineering in "
            "plain english. Journal of Practical AI, 12(3), 44-58. "
            "https://doi.org/10.1234/practical.2024.001."
        )

    def test_mla_full_article(self):
        assert format_citation(FULL_ARTICLE, "MLA") == (
            "Rivera, Ana, et al. \"Prompt engineering in plain english.\" "
            "Journal of Practical AI, vol. 12, no. 3, 2024, pp. 44-58."
        )

    def test_chicago_full_article(self):
        assert format_citation(FULL_ARTICLE, "Chicago") == (
            "Rivera, Ana, et al. \"Prompt engineering in plain english.\" "
            "Journal of Practical AI 12, no. 3 (2024): 44-58. "
            "https://doi.org/10.1234/practical.2024.001"
        )

    def test_ieee_full_article(self):
        assert format_citation(FULL_ARTICLE, "IEEE") == (
            "A. Rivera, C. Okafor, and W. Zhang, \"Prompt engineering in plain "
            "english,\" Journal of Practical AI, vol. 12, no. 3, pp. 44-58, "
            "2024. doi: 10.1234/practical.2024.001."
        )

    def test_minimal_article_no_crash(self):
        assert format_citation(MINIMAL_ARTICLE, "APA") == (
            "Smith, J. (n.d.). A note on citations."
        )
        assert format_citation(MINIMAL_ARTICLE, "MLA") == (
            "Smith, Jo. \"A note on citations.\" n.d."
        )


class TestEditors:
    def test_apa_edited_book(self):
        assert format_citation(EDITED_BOOK, "APA").startswith(
            "Nguyen, L., & Porter, S., Eds. (2025)."
        )

    def test_mla_edited_book_declares_editors(self):
        assert format_citation(EDITED_BOOK, "MLA").startswith(
            "Nguyen, Linh, and Porter, Sam, editors."
        )

    def test_ieee_edited_book(self):
        assert format_citation(EDITED_BOOK, "IEEE").startswith(
            "L. Nguyen, and S. Porter, Eds.,"
        )


class TestWebpage:
    def test_apa_webpage(self):
        assert format_citation(WEBPAGE, "APA") == (
            "Publishing your first low-content book (2025). Retrieved from "
            "https://example.com/kdp-guide."
        )

    def test_mla_webpage(self):
        assert format_citation(WEBPAGE, "MLA").endswith(
            "Available at https://example.com/kdp-guide."
        )

    def test_ieee_webpage(self):
        assert format_citation(WEBPAGE, "IEEE").endswith(
            "Available: https://example.com/kdp-guide."
        )


class TestStyleResolution:
    def test_style_lookup_is_case_insensitive(self):
        assert format_citation(FULL_BOOK, "apa") == format_citation(FULL_BOOK, "APA")

    def test_unknown_style_raises(self):
        with pytest.raises(ValueError):
            format_citation(FULL_BOOK, "turabian")


class TestBibliography:
    def test_apa_bibliography_is_sorted_and_headed(self):
        text = format_bibliography([FULL_BOOK, FULL_ARTICLE, WEBPAGE], "apa")
        assert text.startswith("References\n\n")
        entries = [line for line in text.strip().split("\n")[2:] if line]
        # Alphabetical by author last name (title-first entry sorts by title):
        # "Newport" < "Publishing..." < "Rivera, A."
        assert entries[0].startswith("Newport, C.")
        assert entries[1].startswith("Publishing your first low-content book")
        assert entries[2].startswith("Rivera, A.")

    def test_ieee_bibliography_is_numbered(self):
        text = format_bibliography([FULL_BOOK, FULL_ARTICLE], "IEEE")
        assert "[1] " in text and "[2] " in text
        index = text.index("[1]"), text.index("[2]")
        assert index[0] < index[1]

    def test_chicago_heading(self):
        assert format_bibliography([FULL_BOOK], "Chicago").startswith("Bibliography\n\n")

    def test_mla_heading(self):
        assert format_bibliography([FULL_BOOK], "MLA").startswith("Works Cited\n\n")

    def test_leading_articles_ignored_in_sort(self):
        text = format_bibliography([FULL_BOOK, MINIMAL_BOOK], "apa")
        entries = [line for line in text.strip().split("\n")[2:] if line]
        # "Untitled Project" sorts as U ("The" ignored), which comes after
        # Newport; the citation itself still keeps the "The".
        assert entries[0].startswith("Newport, C.")
        assert entries[1].startswith("The Untitled Project")

    def test_empty_bibliography(self):
        assert format_bibliography([], "APA") == "References\n\n\n"
