"""Source model shared by every formatter.

A ``Source`` is intentionally loose: any field may be missing, and every
formatter is required to degrade gracefully instead of raising. This keeps the
tool friendly for beginner users who have incomplete metadata (which is most
of us, most of the time).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Optional

# Source types we understand. Unknown types fall back to "book" formatting.
SOURCE_TYPES = ("book", "article", "webpage")

TYPE_LABELS = {
    "book": "a book",
    "article": "a journal article",
    "paper": "a conference paper",
    "webpage": "a web page",
}

ARTICLE_LIKE = ("article", "paper", "webpage")


@dataclass
class Source:
    """Metadata for one cited work."""

    title: Optional[str] = None
    authors: list[str] = field(default_factory=list)
    editors: list[str] = field(default_factory=list)
    year: Optional[str] = None
    publisher: Optional[str] = None
    city: Optional[str] = None
    edition: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    note: Optional[str] = None
    kind: str = "book"

    @property
    def is_article_like(self) -> bool:
        return self.kind in ARTICLE_LIKE

    @property
    def display_title(self) -> str:
        """Title with a friendly fallback so no citation is ever blank."""
        return (self.title or "").strip() or "Untitled"


def _as_name_list(value: Any) -> list[str]:
    """Accept a string, a single name, or a list of names; always return a list."""
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    return [str(name).strip() for name in value if str(name).strip()]


def _as_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def parse_name(raw: str) -> tuple[str, str]:
    """Split a name into (last, first) parts.

    Accepts ``"Last, First"`` (preferred) or ``"First Last"``. A single token is
    treated as a last name (often an organization), which keeps things usable
    without guessing.
    """
    raw = raw.strip()
    if "," in raw:
        last, _, first = raw.partition(",")
        return last.strip(), first.strip()
    parts = raw.split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[-1], " ".join(parts[:-1])


def initials(first: str) -> str:
    """``"Cal Newport"`` -> ``"C. N."`` (APA/IEEE style initials)."""
    return " ".join(f"{part[0]}." for part in first.split() if part)


def sort_key(source: Source) -> tuple[str, str]:
    """Alphabetical key: first author's last name, else title.

    Leading articles (A / An / The) are ignored when sorting by title, which is
    how human bibliographies are alphabetized.
    """
    if source.authors:
        last, _ = parse_name(source.authors[0])
        name = last.strip()
        if name:
            return name.lower(), ""
    return _title_key(source.display_title), ""


def _title_key(title: str) -> str:
    lowered = title.strip().lower()
    for article in ("the ", "a ", "an "):
        if lowered.startswith(article):
            lowered = lowered[len(article):]
            break
    return lowered


def source_from_dict(data: dict[str, Any]) -> Source:
    """Build a Source from a YAML/CLI mapping, ignoring unknown keys."""
    kind = str(data.get("type", data.get("kind", "book"))).strip().lower() or "book"
    if kind not in SOURCE_TYPES + ("paper",):
        kind = "book"
    return Source(
        kind=kind,
        title=_as_str(data.get("title")),
        authors=_as_name_list(data.get("authors", data.get("author"))),
        editors=_as_name_list(data.get("editors", data.get("editor"))),
        year=_as_str(data.get("year")),
        publisher=_as_str(data.get("publisher")),
        city=_as_str(data.get("city")),
        edition=_as_str(data.get("edition")),
        journal=_as_str(data.get("journal", data.get("publication"))),
        volume=_as_str(data.get("volume")),
        issue=_as_str(data.get("issue")),
        pages=_as_str(data.get("pages")),
        doi=_as_str(data.get("doi")),
        url=_as_str(data.get("url")),
        note=_as_str(data.get("note")),
    )


def sources_cycle(sources: Iterable[Source]) -> list[Source]:
    return list(sources)
