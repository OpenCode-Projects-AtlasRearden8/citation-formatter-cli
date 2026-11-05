"""APA, MLA, Chicago, and IEEE formatters.

Every formatter degrades gracefully: missing authors fall back to the title,
missing years fall back to "n.d.", and empty fields are dropped from the entry.
All output is plain text so it pastes cleanly into Word, Google Docs, or a
KDP manuscript (italics are intentionally not attempted; they are lost or
mangled by most plain-text editors anyway).

Author-name convention: give authors as ``"Last, First"`` (e.g. ``Newport, Cal``).
Without a comma, ``"Cal Newport"`` is assumed First Last. APA and IEEE always
invert, so either spelling works there; MLA and Chicago keep ``Last, First``
exactly when the user wrote it that way, which mirrors real style guides.
"""

from __future__ import annotations

from typing import Callable

from .models import Source, initials, parse_name, sort_key

NA = "n.d."  # "no date" placeholder when a year is missing

ARTICLE_LIKE = ("article", "paper", "webpage")


def _bare_doi(doi: str) -> str:
    for prefix in ("https://doi.org/", "http://doi.org/", "doi.org/", "doi:"):
        if doi.startswith(prefix):
            return doi[len(prefix):]
    return doi


def _clean(text: str) -> str:
    """Collapse doubled separators and stray commas left by missing fields."""
    text = text.replace("  ", " ")
    while " ," in text or ", ," in text or ",," in text:
        text = text.replace(" ,", ",").replace(", ,", "").replace(",,", ",")
    while " ." in text:
        text = text.replace(" .", ".")
    while ".." in text:
        text = text.replace("..", ".")
    while ", ." in text:
        text = text.replace(", .", ".")
    return text.strip()


def _end(text: str) -> str:
    text = _clean(text)
    if text and not text.endswith("."):
        text += "."
    return text


# --------------------------------------------------------------------------- #
# Author-name helpers
# --------------------------------------------------------------------------- #

def _apa_segment(name: str) -> str:
    last, first = parse_name(name)
    return last if not first else f"{last}, {initials(first)}"


def _ieee_segment(name: str) -> str:
    last, first = parse_name(name)
    return last if not first else f"{initials(first)} {last}"


def _full_segment(name: str) -> str:
    last, first = parse_name(name)
    if not first:
        return last
    return f"{first} {last}"


def _keep_inversion(name: str) -> str:
    """MLA/Chicago: keep ``Last, First`` if the user used a comma."""
    name = name.strip()
    return name if "," in name else _full_segment(name)


def _apa_names(names: list[str]) -> str:
    segs = [_apa_segment(n) for n in names]
    if len(segs) == 1:
        return segs[0]
    if len(segs) == 2:
        return f"{segs[0]}, & {segs[1]}"
    return ", ".join(segs[:-1]) + f", & {segs[-1]}"


def _prose_names(names: list[str]) -> str:
    """MLA/Chicago joining: invert first name, natural order after."""
    first = _keep_inversion(names[0])
    if len(names) == 1:
        return first
    if len(names) == 2:
        return f"{first}, and {_full_segment(names[1])}"
    return f"{first}, et al."


def _ieee_names(names: list[str]) -> str:
    segs = [_ieee_segment(n) for n in names]
    if len(segs) == 1:
        return segs[0]
    return ", ".join(segs[:-1]) + f", and {segs[-1]}"


def _apa_names_with_role(source: Source) -> str:
    if source.authors:
        return _apa_names(source.authors)
    if source.editors:
        edit_label = ", Eds." if len(source.editors) > 1 else ", Ed."
        return _apa_names(source.editors) + edit_label
    return ""


def _prose_names_with_role(source: Source) -> str:
    if source.authors:
        return _prose_names(source.authors)
    if source.editors:
        names = [_keep_inversion(n) for n in source.editors]
        base = names[0] if len(names) == 1 else (
            ", ".join(names[:-1]) + f", and {names[-1]}"
        )
        return f"{base}, editors."
    return ""


def _ieee_names_with_role(source: Source) -> str:
    if source.authors:
        return _ieee_names(source.authors)
    if source.editors:
        edit_label = ", Eds." if len(source.editors) > 1 else ", Ed."
        return _ieee_names(source.editors) + edit_label
    return ""


def _lead(text: str) -> str:
    return f"{text.rstrip('. ')}. " if text else ""


# --------------------------------------------------------------------------- #
# APA (7th ed.)
# --------------------------------------------------------------------------- #

def _apa_book(source: Source) -> str:
    authors = _apa_names_with_role(source)
    year = source.year or NA
    title = source.display_title
    edition = f" ({source.edition} ed.)" if source.edition else ""
    publisher = source.publisher or ""
    if authors:
        lead = f"{authors} ({year}). "
        return _end(_clean(f"{lead}{title}{edition}. {publisher}"))
    # APA: no author -> the title takes the author position, then (Year)
    return _end(f"{title}{edition} ({year}). {publisher}")


def _apa_article_like(source: Source) -> str:
    authors = _apa_names_with_role(source)
    year = source.year or NA
    lead = (
        f"{authors} ({year}). {source.display_title}."
        if authors
        else f"{source.display_title} ({year})."
    )
    text = lead
    if source.journal:
        journal_bit = source.journal
        if source.volume:
            journal_bit += f", {source.volume}"
            if source.issue:
                journal_bit += f"({source.issue})"
        if source.pages:
            journal_bit += f", {source.pages}"
        text += f" {journal_bit}."
    if source.doi:
        text += f" https://doi.org/{_bare_doi(source.doi)}"
    elif source.url:
        text += f" Retrieved from {source.url}"
    return _end(text)


# --------------------------------------------------------------------------- #
# MLA (9th ed., Works Cited)
# --------------------------------------------------------------------------- #

def _mla_book(source: Source) -> str:
    head = _lead(_prose_names_with_role(source))
    edition = f" {source.edition} ed.," if source.edition else ""
    if source.publisher or source.year:
        tail = ", ".join(b for b in (source.publisher, source.year or NA) if b)
        return _end(f"{head}{source.display_title}.{edition} {tail}")
    return _end(f"{head}{source.display_title}.{edition} {NA}")


def _mla_article_like(source: Source) -> str:
    head = _lead(_prose_names_with_role(source))
    title_bit = f"\"{source.display_title}.\""
    if source.journal:
        extras = []
        if source.volume:
            extras.append(f"vol. {source.volume}")
        if source.issue:
            extras.append(f"no. {source.issue}")
        extras.append(source.year or NA)
        mid = f"{source.journal}, {', '.join(extras)}"
        if source.pages:
            mid += f", pp. {source.pages}"
        return _end(f"{head}{title_bit} {mid}")
    text = f"{head}{title_bit} {source.year or NA}."
    if source.doi:
        text += f" doi: {_bare_doi(source.doi)}."
    elif source.url:
        text += f" Available at {source.url}."
    return _end(text)


# --------------------------------------------------------------------------- #
# Chicago (17th ed., bibliography entries)
# --------------------------------------------------------------------------- #

def _chicago_book(source: Source) -> str:
    head = _lead(_prose_names_with_role(source))
    edition = f" {source.edition} ed." if source.edition else ""
    if source.publisher or source.city:
        place = f"{source.city}: " if source.city else ""
        publisher = (source.publisher or "").rstrip(", ")
        tail = f"{place}{publisher}, {source.year or NA}."
    else:
        tail = f"{source.year or NA}."
    text = f"{head}{source.display_title}{edition}. {tail}"
    if source.url:
        text += f" {source.url}."
    return _end(text)


def _chicago_article_like(source: Source) -> str:
    head = _lead(_prose_names_with_role(source))
    title_bit = f"\"{source.display_title}.\""
    if source.journal:
        mid = source.journal
        if source.volume:
            mid += f" {source.volume}"
            if source.issue:
                mid += f", no. {source.issue}"
        year_bit = f" ({source.year or NA})"
        mid += f"{year_bit}: {source.pages}." if source.pages else f"{year_bit}."
        text = f"{head}{title_bit} {mid}"
        if source.doi:
            text += f" https://doi.org/{_bare_doi(source.doi)}"
        elif source.url:
            text += f" {source.url}"
        return text  # Chicago: no trailing period after a DOI/URL, per CMOS 17
    text = f"{head}{title_bit} {source.year or NA}."
    if source.url:
        text += f" {source.url}."
    elif source.doi:
        text += f" https://doi.org/{_bare_doi(source.doi)}."
    return _end(text)


# --------------------------------------------------------------------------- #
# IEEE (references)
# --------------------------------------------------------------------------- #

def _ieee_book(source: Source) -> str:
    head = f"{_ieee_names_with_role(source)}, " if (source.authors or source.editors) else ""
    edition = f" {source.edition} ed." if source.edition else ""
    if source.publisher or source.city:
        place = f"{source.city}: " if source.city else ""
        publisher = (source.publisher or "").rstrip(", ")
        tail = f"{place}{publisher}, {source.year or NA}."
    else:
        tail = f"{source.year or NA}."
    return _end(f"{head}{source.display_title}{edition}. {tail}")


def _ieee_article_like(source: Source) -> str:
    head = f"{_ieee_names_with_role(source)}, " if (source.authors or source.editors) else ""
    title_bit = f"\"{source.display_title},\""
    if source.journal:
        bits = []
        if source.volume:
            bits.append(f"vol. {source.volume}")
        if source.issue:
            bits.append(f"no. {source.issue}")
        if source.pages:
            bits.append(f"pp. {source.pages}")
        bits.append(source.year or NA)
        text = f"{head}{title_bit} {source.journal}, {', '.join(bits)}."
        if source.doi:
            text += f" doi: {_bare_doi(source.doi)}."
    elif source.url:
        tail = f" Available: {source.url}"
        if source.doi:
            tail += f", doi: {_bare_doi(source.doi)}"
        text = f"{head}{title_bit} {source.year or NA}.{tail}"
    else:
        text = f"{head}{title_bit} {source.year or NA}."
        if source.doi:
            text += f" doi: {_bare_doi(source.doi)}."
    return _end(text)


FORMATTERS: dict[str, dict[str, Callable[[Source], str]]] = {
    "APA": {"book": _apa_book, "article": _apa_article_like, "paper": _apa_article_like, "webpage": _apa_article_like},
    "MLA": {"book": _mla_book, "article": _mla_article_like, "paper": _mla_article_like, "webpage": _mla_article_like},
    "Chicago": {"book": _chicago_book, "article": _chicago_article_like, "paper": _chicago_article_like, "webpage": _chicago_article_like},
    "IEEE": {"book": _ieee_book, "article": _ieee_article_like, "paper": _ieee_article_like, "webpage": _ieee_article_like},
}

STYLES = tuple(FORMATTERS)

HEADINGS = {
    "APA": "References",
    "MLA": "Works Cited",
    "Chicago": "Bibliography",
    "IEEE": "References",
}


def _resolve_style(style: str) -> str:
    """Case-insensitive style lookup ('apa', 'APA', 'chicago' all work)."""
    lowered = style.strip().lower()
    for key in FORMATTERS:
        if key.lower() == lowered:
            return key
    raise ValueError(f"Unknown style {style!r}; choose from {', '.join(STYLES)}")


def canonical_style(style: str) -> str:
    """Public-friendly version of the case-insensitive lookup ('ieee' -> 'IEEE')."""
    return _resolve_style(style)


def format_citation(source: Source, style: str) -> str:
    """Format one source in the requested style (any letter casing works)."""
    style_key = _resolve_style(style)
    kind = source.kind if source.kind in ARTICLE_LIKE else "book"
    return FORMATTERS[style_key][kind](source)


def format_bibliography(sources: list[Source], style: str) -> str:
    """Return a paste-ready, alphabetized bibliography.

    IEEE entries are numbered [1], [2], ... IEEE reference lists are numbered
    in reading order; alphabetical numbering keeps offline output stable and
    predictable, and the CLI documents this choice.
    """
    style_key = _resolve_style(style)
    ordered = sorted(sources, key=sort_key)
    entries = [format_citation(s, style_key) for s in ordered]
    if style_key == "IEEE":
        body = "\n".join(f"[{i}] {e}" for i, e in enumerate(entries, start=1))
    else:
        body = "\n".join(entries)
    return f"{HEADINGS[style_key]}\n\n{body}\n"
