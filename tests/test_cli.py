"""CLI end-to-end tests: YAML input, flags, file output, error handling."""

import io

from citation_formatter.cli import main

EXAMPLE = "examples/sample_sources.yaml"


def noninteracting_stdin(monkeypatch):
    """Not a tty: every interactive prompt returns '' (graceful skip)."""
    monkeypatch.setattr("sys.stdin", io.StringIO())


def test_yaml_input_apa(monkeypatch, capsys):
    noninteracting_stdin(monkeypatch)
    code = main(["--file", EXAMPLE, "--style", "apa", "--quiet"])
    assert code == 0
    out = capsys.readouterr().out
    assert out.startswith("References\n\n")
    assert "Newport, C. (2016)" in out
    assert "About the Sources" in out
    assert "A book by" in out  # back-matter speaks in plain English


def test_yaml_input_ieee_numbered_no_backmatter(monkeypatch, capsys):
    noninteracting_stdin(monkeypatch)
    code = main(["--file", EXAMPLE, "--style", "IEEE", "--bibliography-only", "--quiet"])
    assert code == 0
    out = capsys.readouterr().out
    assert "[1]" in out and "[6]" in out
    assert "About the Sources" not in out


def test_backmatter_only(monkeypatch, capsys):
    noninteracting_stdin(monkeypatch)
    code = main(["--file", EXAMPLE, "--backmatter-only", "--quiet"])
    assert code == 0
    out = capsys.readouterr().out
    assert "About the Sources" in out
    assert "References" not in out.split("\n")[0]


def test_single_source_flags(monkeypatch, capsys):
    noninteracting_stdin(monkeypatch)
    code = main([
        "--title", "Deep Work",
        "--author", "Newport, Cal",
        "--year", "2016",
        "--publisher", "Grand Central Publishing",
        "--style", "mla", "--quiet",
    ])
    assert code == 0
    out = capsys.readouterr().out
    assert "Newport, Cal. Deep Work. Grand Central Publishing, 2016." in out


def test_single_source_flags_article(monkeypatch, capsys):
    noninteracting_stdin(monkeypatch)
    code = main([
        "--type", "article",
        "--title", "Attention is all you need",
        "--author", "Vaswani, Ashish",
        "--year", "2017",
        "--journal", "arXiv preprint",
        "--doi", "10.48550/arXiv.1706.03762",
        "--style", "ieee", "--quiet",
    ])
    assert code == 0
    out = capsys.readouterr().out
    assert 'A. Vaswani, "Attention is all you need,"' in out
    assert "doi: 10.48550/arXiv.1706.03762" in out


def test_out_file_written(tmp_path, monkeypatch, capsys):
    noninteracting_stdin(monkeypatch)
    out_path = tmp_path / "citations.txt"
    code = main(["--file", EXAMPLE, "-o", str(out_path)])
    assert code == 0
    text = out_path.read_text(encoding="utf-8")
    assert "References" in text
    assert "About the Sources" in text
    assert "Wrote" in capsys.readouterr().out


def test_missing_file_error(monkeypatch, capsys):
    noninteracting_stdin(monkeypatch)
    code = main(["--file", "nope-missing.yaml", "--quiet"])
    assert code == 1
    assert "error:" in capsys.readouterr().err


def test_conflicting_flags_rejected(monkeypatch, capsys):
    noninteracting_stdin(monkeypatch)
    code = main(["--file", EXAMPLE, "--bibliography-only", "--backmatter-only", "--quiet"])
    assert code == 2


def test_interactive_mode_off_tty_skips_prompts(monkeypatch, capsys):
    # No --file, no flags, stdin not a tty: prompts return "" and defaults apply.
    noninteracting_stdin(monkeypatch)
    code = main(["--style", "apa", "--quiet"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Untitled" in out  # graceful fallback instead of a crash


def test_console_script_entrypoint():
    """`python -m citation_formatter` runs end-to-end as a subprocess."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "citation_formatter", "--file", EXAMPLE,
         "--style", "chicago", "--quiet"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    assert "Bibliography" in result.stdout
