# citation-formatter-cli

Turn book, article, and paper metadata (or a simple YAML list) into formatted
APA, MLA, Chicago, and IEEE citations, a paste-ready bibliography, and
KDP-style back-matter — "About the Sources" written like a friend explaining
your book's sources.

**Fully offline. No network, no API keys, no accounts.** Missing fields are
handled gracefully: the formatters use `n.d.` / `Untitled` placeholders, and
interactive mode lets you press Enter to skip anything you don't have.

Built by [Asdale Dynamics, LLC](https://dylanasdale.github.io) — Dylan Asdale's
beginner-first toolkit for AI authors. It pairs naturally with the
`back-matter-builder-cli` project: that one polishes the whole back-matter of a
book; this one turns *your source list* into correct citations and a friendly
"About the Sources" section you can paste straight into a manuscript.

## The problem this solves

Citation generators online want an account, phone home, or bury you in ads.
This one runs from your terminal, reads what you already have (even a rough
YAML list), and hands back text you can paste into Word, Google Docs, or a KDP
upload — plus back-matter most citation tools never think about.

## Install

Requires Python 3.9+. PyYAML is the only dependency.

```bash
# from this folder
pip install .            # installs the `citation-formatter` command
# ...or without installing:
python -m citation_formatter --help
```

## Quick start

### 1. Format a whole source list from YAML

```yaml
# sources.yaml
sources:
  - type: book
    title: Deep Work
    authors: ["Newport, Cal"]        # "Last, First" (or "First Last")
    year: 2016
    publisher: Grand Central Publishing
  - type: article
    title: Attention is all you need
    authors: ["Vaswani, Ashish", "Shazeer, Noam"]
    year: 2017
    journal: arXiv preprint
    volume: "1706"
    pages: "03762"
    doi: 10.48550/arXiv.1706.03762
  - type: webpage
    title: Publishing your first low-content book
    year: 2025
    url: https://example.com/kdp-guide
    note: A practical walkthrough of the KDP upload process.
```

```bash
citation-formatter --file sources.yaml --style apa
```

```text
References

Newport, C. (2016). Deep Work. Grand Central Publishing.
...

About the Sources

Everything in this book that leans on someone else's work points back to the
sources below...

1. A book by Newport, Cal, 2016, from Grand Central Publishing. Background for
   the focused-work chapter...

   Citation (APA): Newport, C. (2016). Deep Work. Grand Central Publishing.
```

A runnable sample lives at [`examples/sample_sources.yaml`](examples/sample_sources.yaml):

```bash
citation-formatter --file examples/sample_sources.yaml --style ieee
```

### 2. Cite a single source with flags

```bash
citation-formatter \
  --title "Deep Work" \
  --author "Newport, Cal" \
  --year 2016 \
  --publisher "Grand Central Publishing" \
  --style mla
```

Articles use `--type article --journal ... --volume ... --issue ... --pages ...`
(`--type paper` and `webpage` are also supported).

### 3. Run it interactively

```bash
citation-formatter
```

It asks for each field with friendly prompts, one at a time, and **pressing
Enter always skips** — missing fields are handled gracefully in every style
(`n.d.` for missing years, title-first entries when an author is unknown).

## Supported styles

| Style   | Heading in output | Notes |
|---------|-------------------|-------|
| APA     | References        | APA 7 bibliography entries |
| MLA     | Works Cited       | MLA 9 |
| Chicago | Bibliography      | Chicago 17 bibliography (note) entries |
| IEEE    | References        | Numbered `[1] ...`, doi lines included |

Style names are case-insensitive: `--style APA`, `--style apa`, and
`--style ieee` all work.

## CLI reference

```text
citation-formatter [-h] [-t {apa,mla,chicago,ieee}] [-f FILE] [-o OUT]
                   [--bibliography-only | --backmatter-only]
                   [--type {book,article,paper,webpage}] [--title TITLE]
                   [--author AUTHOR] [--editor EDITOR] [--year YEAR]
                   [--publisher PUBLISHER] [--city CITY] [--edition EDITION]
                   [--journal JOURNAL] [--volume VOLUME] [--issue ISSUE]
                   [--pages PAGES] [--doi DOI] [--url URL] [--note NOTE]
                   [-q]
```

| Flag | What it does |
|------|----------------|
| `-f/--file` | YAML file with a `sources:` list (or a bare YAML list) |
| `-t/--style` | `apa` (default), `mla`, `chicago`, `ieee` |
| `-o/--out` | Write the output to a file instead of the terminal |
| `--bibliography-only` | Skip the "About the Sources" section |
| `--backmatter-only` | Print only the "About the Sources" section |
| `--note` | Plain-English reason a source is cited (feeds back-matter) |
| `-q/--quiet` | Suppress warnings (e.g. skipped broken YAML entries) |
| `-h/--help` | Full help |

Single-source flags: `--type, --title, --author (repeatable), --editor
(repeatable), --year, --publisher, --city, --edition, --journal, --volume,
--issue, --pages, --doi, --url, --note`.

## The names parts

- Give authors as `"Last, First"` when you can (`"Newport, Cal"`). Plain
  `"Cal Newport"` also works: APA and IEEE invert either way; MLA and Chicago
  keep `Last, First` exactly when you wrote it that way.
- Multiple authors: a YAML list, repeated `--author` flags, or in interactive
  mode separate with `;` or ` and ` (so the comma inside `Last, First` is safe).
- Anything optional may be omitted. Nothing crashes; nothing prints `[None]`.

## The back-matter ("About the Sources")

Academic bibliographies tell readers *what* a source is; KDP back-matter
should also tell readers *why you read it*. Each source gets a short
plain-English line — use the optional `note` field (or `--note`) to supply
your own:

```yaml
  - title: Deep Work
    note: Background for the chapter on focused, low-distraction work sessions.
```

The section closes with the honest disclaimer that a listing means the source
shaped the thinking, not that the source endorses the book.

## Testing

pytest, against hand-checked citation fixtures:

```bash
pip install -e .[dev]
pytest
```

Exact-string fixtures cover every style with full, minimal (no author/year),
article, editors-only, and webpage sources; sorted/numbered bibliographies;
malformed YAML handling; and the CLI end-to-end.

## Design notes

- **Offline by design.** No requests, no telemetry, no keys. Works on a plane.
- **Plain text output.** Italics/caps styling is intentionally left to your
  word processor; the output pastes cleanly everywhere.
- **APA titles keep the case you type.** APA asks for sentence case in titles;
  type them that way and nothing mangles your proper nouns.
- **Chicago does not place a period after a DOI/URL**, per CMOS 17.
- Distinct from `back-matter-builder-cli` (whole-book back-matter arcs);
  this tool is citation-first and source-list-driven.

## Repository layout

```text
citation_formatter/     the package (models, formatters, backmatter, CLI)
examples/               sample_sources.yaml — runnable demo input
tests/                  pytest suite with citation fixtures + fixtures.py
```

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.

More friendly, plain-English AI guides at
[dylanasdale.github.io](https://dylanasdale.github.io).
