"""Command-line interface: metadata or YAML -> citations + bibliography + back-matter.

Usage overview:

    citation-formatter --file sources.yaml --style apa
    citation-formatter --file sources.yaml --style ieee --no-backmatter
    citation-formatter --title "Deep Work" --author "Newport, Cal" --year 2016 \
        --publisher "Grand Central Publishing" --style mla
    citation-formatter            # interactive: prompts for missing fields

Missing fields never crash anything: the formatters use "n.d." / "Untitled"
placeholders, and interactive mode prompts gracefully so a beginner can just
press Enter to skip a field they do not have.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from .backmatter import build_backmatter
from .formatters import format_bibliography
from .loaders import LoaderError, load_sources_yaml
from .models import Source, source_from_dict

BIBLIOTYPE_CHOICES = ("book", "article", "paper", "webpage")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="citation-formatter",
        description=(
            "Offline citation builder: turn book/article metadata or a simple "
            "YAML list into APA, MLA, Chicago, and IEEE citations, a "
            "paste-ready bibliography, and KDP-style 'About the Sources' "
            "back-matter. No network, no API keys."
        ),
    )
    parser.add_argument(
        "-t", "--style",
        default="apa",
        type=str.lower,
        choices=["apa", "mla", "chicago", "ieee"],
        help="citation style (default: apa)",
    )
    parser.add_argument("-f", "--file", help="YAML file containing a 'sources:' list")
    parser.add_argument("-o", "--out", help="write output to this file instead of stdout")
    parser.add_argument(
        "--bibliography-only", action="store_true",
        help="skip the back-matter section entirely",
    )
    parser.add_argument(
        "--backmatter-only", action="store_true",
        help="print only the 'About the Sources' section",
    )
    parser.add_argument("--type", dest="kind", choices=BIBLIOTYPE_CHOICES, help="single-source mode: source type")
    parser.add_argument("--title")
    parser.add_argument("--author", action="append", default=[], help='author as "Last, First" or "First Last"; repeatable')
    parser.add_argument("--editor", action="append", default=[], help="editor; repeatable")
    parser.add_argument("--year")
    parser.add_argument("--publisher")
    parser.add_argument("--city")
    parser.add_argument("--edition")
    parser.add_argument("--journal", help="journal or publication name (articles)")
    parser.add_argument("--volume")
    parser.add_argument("--issue")
    parser.add_argument("--pages")
    parser.add_argument("--doi")
    parser.add_argument("--url")
    parser.add_argument("--note", help="plain-English note shown in the back-matter")
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="suppress warnings",
    )
    return parser


def _ask(prompt: str, quiet: bool) -> str:
    if not sys.stdin.isatty():
        return ""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        if not quiet:
            print()
        return ""


def split_authors_input(raw: str) -> list[str]:
    """Parse freeform author input like "Newport, Cal and Fisher, Ada".

    Semicolons or the word 'and' separate authors; a single comma inside a
    name means "Last, First" and is preserved.
    """
    raw = raw.replace(";", "; ").replace(" and ", "; ")
    return [p.strip() for p in raw.split(";") if p.strip()]


def interactive_source(quiet: bool) -> Source:
    """Prompt for one source; every prompt accepts Enter to skip."""
    print("Add a source (press Enter to skip anything you don't have):")
    kind = (_ask("  Type [book/article/paper/webpage] (default: book): ", quiet) or "book").lower()
    if kind not in BIBLIOTYPE_CHOICES:
        kind = "book"
    title = _ask("  Title: ", quiet) or None
    raw_authors = _ask("  Authors as 'Last, First' (separate multiple with ';' or 'and'): ", quiet)
    authors = split_authors_input(raw_authors)
    year = _ask("  Year: ", quiet)
    data: dict = {"type": kind, "title": title, "authors": authors, "year": year or None}
    if kind in ("article", "paper"):
        data["journal"] = _ask("  Journal: ", quiet)
        data["volume"] = _ask("  Volume: ", quiet)
        data["issue"] = _ask("  Issue: ", quiet)
        data["pages"] = _ask("  Pages: ", quiet)
    else:
        data["publisher"] = _ask("  Publisher: ", quiet)
        data["city"] = _ask("  City of publication: ", quiet)
        data["edition"] = _ask("  Edition (e.g. 2nd): ", quiet)
    data["doi"] = _ask("  DOI (optional): ", quiet)
    data["url"] = _ask("  URL (optional): ", quiet)
    data["note"] = _ask("  Plain-English note for back-matter (optional): ", quiet) or None
    return source_from_dict(data)


def _collect(args: argparse.Namespace) -> list[Source]:
    if args.file:
        return load_sources_yaml(args.file)
    single_source_keys = {
        "kind", "title", "author", "editor", "year", "publisher", "city",
        "edition", "journal", "volume", "issue", "pages", "doi", "url", "note",
    }
    if any(bool(args.__dict__[key]) for key in single_source_keys):
        data = {k: v for k, v in vars(args).items() if k in {
            "kind", "title", "year", "publisher", "city", "edition", "journal",
            "volume", "issue", "pages", "doi", "url", "note",
        }}
        data["authors"] = args.author
        data["editors"] = args.editor
        return [source_from_dict(data)]
    return [interactive_source(args.quiet)]


def run(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.bibliography_only and args.backmatter_only:
        print("error: --bibliography-only and --backmatter-only cannot be combined", file=sys.stderr)
        return 2

    try:
        sources = _collect(args)
    except LoaderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not args.quiet and not sources:
        print("warning: no sources were provided", file=sys.stderr)
        return 1

    style = (args.style or "apa").strip().lower()
    out_text = ""
    if not args.backmatter_only:
        out_text += format_bibliography(sources, style)
    if not args.bibliography_only:
        out_text += "\n" + build_backmatter(sources, style)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(out_text)
        if not args.quiet:
            print(f"Wrote {args.out}")
    else:
        sys.stdout.write(out_text)
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    try:
        return run(argv)
    except BrokenPipeError:  # e.g. `citation-formatter | head` on POSIX
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
