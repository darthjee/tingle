"""selection.py — Select the Ruby files sent to the RubyCritic container.

A `Selection` holds the mount root, the lines sent on the container's stdin
(paths relative to the root, POSIX separators, sorted) and the warnings for
the files whose name cannot be sent (a newline, or not valid UTF-8).

Files are collected with `file_size`'s `FileCollector` (default and extra
excludes, `.gitignore`, `--ignore`/`--include` globs, the fixed `.rb` filter),
without its binary check and with symlink confinement: a file that resolves
outside the mount root (or a dangling symlink) is dropped. A kept symlink is
sent as its target's path, and a symlink and its target count once.
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
    """Turn collected `files` into stdin lines relative to `root`, dropping unsendable names.

    Each file is resolved first, so a symlink becomes its target's path
    (`root` must be resolved too), and files resolving to the same path are
    kept once.
    """
    selection = Selection(root)
    seen: set[Path] = set()
    for path in files:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        rel = resolved.relative_to(root).as_posix()
        reason = unsendable_reason(rel)
        if reason is None:
            selection.lines.append(rel)
        else:
            selection.skipped.append(reason)
    selection.lines.sort()
    return selection


def select_files(
    target: Path,
    root: Path,
    *,
    excludes: list[str] | None = None,
    ignore: list[str] | None = None,
    include: list[str] | None = None,
    gitignore: bool = True,
) -> Selection:
    """Collect the `.rb` files under `target` (or `target` itself) for the mount `root`.

    `excludes` are directory names (default: `Constants.DEFAULT_EXCLUDES`; not
    applied to a single file), `ignore`/`include` are globs relative to
    `target` and `gitignore` skips the untracked files git ignores. There is
    no binary check, so non-UTF-8 Ruby files still reach the image, and files
    resolving outside the mount root are dropped.
    """
    collector = FileCollector(
        Constants.DEFAULT_EXCLUDES if excludes is None else excludes,
        Constants.EXTENSIONS,
        ignore=ignore,
        include=include,
        gitignore=gitignore,
        binary_check=False,
        outside_symlinks=False,
    )
    return build_selection(root, collector.collect(target))
