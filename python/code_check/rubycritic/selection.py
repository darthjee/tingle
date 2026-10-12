"""selection.py — Select the Ruby files sent to the RubyCritic container.

A `Selection` holds the mount root, the lines sent on the container's stdin
(paths relative to the root, POSIX separators, sorted) and the warnings for
the files whose name cannot be sent (a newline, or not valid UTF-8).

Files are collected with `file_size`'s `FileCollector` (default and extra
excludes, `.gitignore`, `--ignore`/`--include` globs, the fixed `.rb` filter),
without its binary check and with symlink confinement: a file that resolves
outside the mount root (or a dangling symlink) is dropped. A kept symlink is
sent as its target's path, and a symlink and its target count once.

The logic lives in `code_check.docker_check.selection`; `select_files` here
binds the Ruby extension and default excludes.
"""

from __future__ import annotations

from pathlib import Path

from code_check.docker_check import selection as docker_check_selection
from code_check.docker_check.selection import Selection, build_selection, unsendable_reason
from code_check.rubycritic.constants import Constants

__all__ = ["Selection", "build_selection", "select_files", "unsendable_reason"]


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
    return docker_check_selection.select_files(
        target,
        root,
        extensions=Constants.EXTENSIONS,
        excludes=Constants.DEFAULT_EXCLUDES if excludes is None else excludes,
        ignore=ignore,
        include=include,
        gitignore=gitignore,
    )
