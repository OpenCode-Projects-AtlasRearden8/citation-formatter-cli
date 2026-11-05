"""KDP-style back-matter: a readable "About the Sources" section.

Unlike the citation formatters (which produce rigorously correct academic
strings), back-matter speaks "like a friend would": each source gets a short,
plain-English description readers can actually use.

Shape note: the bibliography says *what* the source is; back-matter says *why
you read it* and *who should check it out*. That split is what makes this tool
distinct from a pure citation engine, and it is the part reviewers of an
AI-authored book care about most.
"""

from __future__ import annotations

from .formatters import canonical_style, format_citation
from .models import TYPE_LABELS, Source, sort_key

ABOUT_HEADING = "About the Sources"

INTRO = (
    "Everything in this book that leans on someone else's work points back to "
    "the sources below. Each one is described in plain terms so you can decide "
    "whether it is worth your time."
)


def _describe(source: Source) -> str:
    """One friendly sentence about the source."""
    kind = TYPE_LABELS.get(source.kind, "a source")
    who = ", ".join(source.authors) if source.authors else "an unsigned piece"
    when = f", {source.year}" if source.year else ""
    venue = source.journal or source.publisher
    venue_bit = f", from {venue}" if venue else ""
    text = f"{_cap(kind)} by {who}{when}{venue_bit}"
    if source.note:
        return text + f". {source.note}"
    return text + ". Cited as background for the ideas discussed in the text."


def _cap(text: str) -> str:
    return text[0].upper() + text[1:] if text else text


def build_backmatter(sources: list[Source], style: str = "APA") -> str:
    """Return the full "About the Sources" section as plain text.

    Each entry pairs a friendly one-line description with the formal citation,
    so readers get the plain-English version first and the scholarly version
    right underneath.
    """
    ordered = sorted(sources, key=sort_key)
    style_name = canonical_style(style)
    lines = [ABOUT_HEADING, "", "", INTRO, "", ""]
    for i, source in enumerate(ordered, start=1):
        lines.append(f"{i}. {_describe(source)}")
        lines.append("")
        lines.append(f"   Citation ({style_name}): {format_citation(source, style_name)}")
        lines.append("")
    lines.append(
        "Listing a source here means it shaped the thinking in this book; it "
        "does not mean the source endorses this book or its author."
    )
    lines.append("")
    return "\n".join(lines)
