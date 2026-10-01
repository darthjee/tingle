"""selection.py — Select the Ruby files sent to the RubyCritic container.

A `Selection` holds the mount root, the lines sent on the container's stdin
(paths relative to the root, POSIX separators, sorted) and the warnings for
the files whose name cannot be sent (a newline, or not valid UTF-8).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from code_check.file_size.file_collector import FileCollector
from code_check.rubycritic.constants import Constants


@dataclass
class Selection:
    """The files to analyse: mount `root`, stdin `lines` and `skipped` warnings."""

    root: Path
    lines: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


def unsendable_reason(rel: str) -> str | None:
    """Return the warning for a relative path that cannot be sent on stdin, else None."""
    if "\n" in rel:
        return f"skipping file with a newline in its name: {rel!r}"
    try:
        rel.encode("utf-8")
    except UnicodeEncodeError:
        return f"skipping file whose name is not valid UTF-8: {rel!r}"
    return None


def build_selection(root: Path, files: Iterable[Path]) -> Selection:
    """Turn collected `files` into stdin lines relative to `root`, dropping unsendable names."""
    selection = Selection(root)
    for path in files:
        rel = path.relative_to(root).as_posix()
        reason = unsendable_reason(rel)
        if reason is None:
            selection.lines.append(rel)
        else:
            selection.skipped.append(reason)
    selection.lines.sort()
    return selection


def select_files(target: Path, root: Path) -> Selection:
    """Collect the `.rb` files under `target` (or `target` itself) for the mount `root`.

    Uses the default excludes (not applied to a single file), no gitignore and
    no binary check, so non-UTF-8 Ruby files still reach the image.
    """
    collector = FileCollector(
        Constants.DEFAULT_EXCLUDES,
        Constants.EXTENSIONS,
        gitignore=False,
        binary_check=False,
    )
    return build_selection(root, collector.collect(target))
