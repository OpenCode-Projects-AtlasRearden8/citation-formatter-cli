"""Shared citation fixtures.

Each expected string is hand-verified against the style guide it claims to
follow (APA 7, MLA 9, Chicago 17 bibliography entries, IEEE references).
"""

from citation_formatter.models import Source

FULL_BOOK = Source(
    title="Deep Work: Rules for Focused Success in a Distracted World",
    authors=["Newport, Cal"],
    year="2016",
    publisher="Grand Central Publishing",
    kind="book",
)

TWO_AUTHOR_BOOK = Source(
    title="Designing for People",
    authors=["Fisher, Ada", "Moore, Ben"],
    year="2020",
    publisher="O'Reilly Media",
    kind="book",
)

THREE_AUTHOR_BOOK = Source(
    title="Learning Python",
    authors=["Lutz, Mark", "Ascher, David", "Taylor, Chris"],
    year="2021",
    publisher="O'Reilly Media",
    kind="book",
)

MINIMAL_BOOK = Source(
    title="The Untitled Project",
    authors=[],
    year=None,
    publisher=None,
    kind="book",
)

FULL_ARTICLE = Source(
    title="Prompt engineering in plain english",
    authors=["Rivera, Ana", "Okafor, Chidi", "Zhang, Wei"],
    year="2024",
    journal="Journal of Practical AI",
    volume="12",
    issue="3",
    pages="44-58",
    doi="10.1234/practical.2024.001",
    kind="article",
)

MINIMAL_ARTICLE = Source(
    title="A note on citations",
    authors=["Smith, Jo"],
    year=None,
    kind="article",
)

EDITED_BOOK = Source(
    title="The AI Companion Anthology",
    editors=["Nguyen, Linh", "Porter, Sam"],
    year="2025",
    publisher="Asdale Dynamics, LLC",
    kind="book",
)

WEBPAGE = Source(
    title="Publishing your first low-content book",
    authors=[],
    year="2025",
    url="https://example.com/kdp-guide",
    kind="webpage",
)

SAMPLE_SOURCES = [FULL_BOOK, FULL_ARTICLE, MINIMAL_BOOK, WEBPAGE]
