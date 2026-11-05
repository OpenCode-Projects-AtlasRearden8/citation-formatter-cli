# STATUS.md — citation-formatter-cli

Build date: 2026-11-05 · Maintainer: Asdale Dynamics, LLC · License: MIT

## What was built

An offline Python CLI that turns book/article/paper metadata (single-source
flags, interactive prompts, or a simple YAML list) into:

- Formatted citations in **APA 7** (References), **MLA 9** (Works Cited),
  **Chicago 17** (Bibliography), and **IEEE** (numbered References)
- A **paste-ready, alphabetized bibliography** (IEEE entries numbered `[1]…`)
- KDP-style back-matter: an "**About the Sources**" section that pairs a
  plain-English description of each source (`--note` supplies the "why")
  with its formal citation, closing with an honest disclaimer

No network access, no API keys, no user data collected. Missing fields are
handled gracefully everywhere: `n.d.` placeholders for missing years,
title-first entries when an author is unknown, and Enter-to-skip interactive
prompts. Malformed YAML entries are skipped with a warning instead of failing
the whole run.

Layout:

- `citation_formatter/models.py` — loose `Source` model, name parsing, sort keys
- `citation_formatter/formatters.py` — the four style engines
- `citation_formatter/backmatter.py` — "About the Sources" builder
- `citation_formatter/loaders.py` — PyYAML loading with graceful skips
- `citation_formatter/cli.py` — argparse CLI + interactive mode
- `examples/sample_sources.yaml` — runnable demo list
- `tests/` — pytest suite (fixtures: `tests/fixtures.py`)

## How to run it

```bash
pip install .                    # or: pip install -e .[dev] for tests
citation-formatter --file examples/sample_sources.yaml --style apa
# or without installing:
python -m citation_formatter --file examples/sample_sources.yaml --style ieee
# single source:
python -m citation_formatter --title "Deep Work" --author "Newport, Cal" \
    --year 2016 --publisher "Grand Central Publishing" --style mla
# interactive:
python -m citation_formatter
```

Options worth knowing: `-t/--style {apa,mla,chicago,ieee}` (case-insensitive),
`-o` to write to a file, `--bibliography-only`, `--backmatter-only`,
`--note` for back-matter text, `-q` to suppress warnings.

## Verification results (2026-11-05)

- `python3 -m pytest` — **78 passed, 0 failed, 0 skipped** (3.13 interpreter)
  - Exact-string fixtures hand-verified against APA 7 / MLA 9 / Chicago 17 /
    IEEE conventions: full book, two- and three-author rules
    (`et al.` for MLA/Chicago, `&` chains for APA), minimal no-author/no-year
    book, minimal article, editors-only book, webpage, DOI/bare-DOI handling
  - Bibliography tests: alphabetical sort ignoring leading articles, IEEE
    numbering, per-style headings
  - Loader tests: valid YAML, top-level list, missing file, invalid YAML,
    empty file, wrong top-level key, unusable-entry skip with warning
  - CLI tests: YAML input, flags, backmatter-only/bibliography-only, output
    file, missing-file error path, conflicting-flag rejection, non-TTY
    interactive fallback, `python -m` subprocess run
- Console script verified installed and running from a clean venv:
  `/tmp venv` `pip install .` then `citation-formatter --file ... --style apa`
- Interactive mode verified against a real pty: all prompts fire, Enter skips
  safely, article path asks for journal/volume/issue/pages

## Bugs found and fixed during this pass

1. Author-name index swap broke APA/IEEE initials (`N. Cal` instead of
   `C. Newport`) after an unpacking-order mistake
2. Interactive author parsing split `Last, First` on the comma; now only `;`
   and ` and ` separate authors
3. Missing space before DOIs; Chicago `no. 3 (2024)` spacing; doubled periods
   after `et al.`; orphaned `, n.d.` when publisher was absent; missing DOI in
   IEEE journal entries; missing trailing periods on minimal entries
4. APA two-author entries now use the correct `A., & B.` form
5. `--style IEEE` was rejected by argparse choice matching; styles are now
   case-insensitive end to end

## Known gaps

- **Italics/caps styling**: output is intentionally plain text; apply italics
  in your word processor. APA titles keep the case you type (safe for proper
  nouns, but you should sentence-case APA titles yourself).
- **Chicago notes (footnote) format** not generated — bibliography entries only.
- **IEEE numbering is alphabetical**, not reading-order: stable and
  predictable offline, but in-text `[1]` numbers will not match manuscript
  order until you renumber (documented in README).
- **No .ris/.bib/txt import** besides the YAML subset; no TSV/JSON export.
- **Edition-only web sources** (no author/journal) render minimal but valid
  entries without accessed-date support.
- Single-source mode and interactive mode cover one source per run; use YAML
  for lists.
