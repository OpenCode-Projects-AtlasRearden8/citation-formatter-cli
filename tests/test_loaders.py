"""Loader tests: real YAML fixtures, malformed files, graceful skips."""

import pytest

from citation_formatter.loaders import LoaderError, load_sources_yaml


def test_sample_yaml_loads(tmp_path):
    path = tmp_path / "sample.yaml"
    path.write_text(
        """
sources:
  - type: book
    title: Deep Work
    authors: ["Newport, Cal"]
    year: 2016
    publisher: Grand Central Publishing
  - title: Noteless Entry
""",
        encoding="utf-8",
    )
    sources = load_sources_yaml(str(path))
    assert len(sources) == 2
    assert sources[0].authors == ["Newport, Cal"]
    assert sources[1].year is None


def test_top_level_list_is_accepted(tmp_path):
    path = tmp_path / "list.yaml"
    path.write_text(
        """
- title: One
- title: Two
""",
        encoding="utf-8",
    )
    sources = load_sources_yaml(str(path))
    assert [s.title for s in sources] == ["One", "Two"]


def test_missing_file_raises_loader_error():
    with pytest.raises(LoaderError):
        load_sources_yaml("/nonexistent/path/definitely-missing.yaml")


def test_invalid_yaml_raises_loader_error(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("sources: [oops\n  - unclosed", encoding="utf-8")
    with pytest.raises(LoaderError):
        load_sources_yaml(str(path))


def test_empty_file_raises(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")
    with pytest.raises(LoaderError):
        load_sources_yaml(str(path))


def test_no_sources_key_raises(tmp_path):
    path = tmp_path / "wrong.yaml"
    path.write_text("books: []\n", encoding="utf-8")
    with pytest.raises(LoaderError):
        load_sources_yaml(str(path))


def test_unusable_entry_skipped_with_warning(tmp_path, capsys):
    path = tmp_path / "partial.yaml"
    path.write_text(
        """
sources:
  - just_a_string
  - title: Real Entry
""",
        encoding="utf-8",
    )
    sources = load_sources_yaml(str(path))
    assert len(sources) == 1
    assert sources[0].title == "Real Entry"
    assert "skipping" in capsys.readouterr().out


def test_repo_example_file_loads():
    sources = load_sources_yaml("examples/sample_sources.yaml")
    assert len(sources) == 6
    kinds = {s.kind for s in sources}
    assert "book" in kinds and "article" in kinds and "webpage" in kinds
