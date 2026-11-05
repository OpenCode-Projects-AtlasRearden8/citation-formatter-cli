"""YAML and dict loading helpers (PyYAML only, fully offline)."""

from __future__ import annotations

from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

from .models import Source, source_from_dict


class LoaderError(Exception):
    pass


def load_sources_yaml(path: str) -> list[Source]:
    """Load a sources list from a YAML file.

    Accepted shapes:

    - a top-level ``sources:`` key holding a list
    - a top-level list directly

    Bad entries are skipped with a warning instead of aborting the whole run,
    so one malformed source does not cost you the other nine.
    """
    if yaml is None:
        raise LoaderError(
            "PyYAML is required for YAML input: pip install pyyaml"
        )
    try:
        with open(path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except OSError as exc:
        raise LoaderError(f"Could not read {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise LoaderError(f"{path} is not valid YAML: {exc}") from exc

    if data is None:
        raise LoaderError(f"{path} is empty.")
    if isinstance(data, dict):
        entries = data.get("sources")
        if entries is None:
            raise LoaderError(
                f"{path}: expected a top-level 'sources:' list, "
                f"but found keys: {', '.join(map(str, data.keys()))}"
            )
    else:
        entries = data
    if not isinstance(entries, list):
        raise LoaderError(f"{path}: 'sources' must be a list of source entries.")
    sources: list[Source] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            print(f"warning: {path}: skipping entry #{index} (not a key/value mapping)")
            continue
        parsed = source_from_dict(entry)
        if parsed.title or parsed.authors or parsed.journal or parsed.url:
            sources.append(parsed)
        else:
            print(f"warning: {path}: skipping entry #{index} (has no usable fields)")
    if not sources:
        raise LoaderError(f"{path}: no usable sources were found.")
    return sources


def sources_from_dicts(dicts: list[dict[str, Any]]) -> list[Source]:
    return [source_from_dict(d) for d in dicts]
