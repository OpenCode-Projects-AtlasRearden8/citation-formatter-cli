"""citation-formatter-cli: offline citation formatting for books, articles, and papers.

Turns source metadata (or a simple YAML list) into APA, MLA, Chicago, and IEEE
citations, a paste-ready bibliography, and KDP-style back-matter
"About the Sources" text. No network access, no API keys.

Copyright (c) 2026 Asdale Dynamics, LLC. MIT licensed.
"""

from .backmatter import build_backmatter
from .formatters import STYLES, format_bibliography, format_citation
from .loaders import load_sources_yaml
from .models import Source, sort_key, source_from_dict

__all__ = [
    "STYLES",
    "Source",
    "build_backmatter",
    "format_bibliography",
    "format_citation",
    "load_sources_yaml",
    "sort_key",
    "source_from_dict",
]

__version__ = "1.0.0"
