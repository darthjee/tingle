"""selection.py — Select the JavaScript/TypeScript files sent to the FTA container.

A `Selection` holds the mount root, the lines sent on the container's stdin
(paths relative to the root, POSIX separators, sorted) and the warnings for
the files whose name cannot be sent (a newline, or not valid UTF-8).

Files are collected with `file_size`'s `FileCollector` (default excludes, the
fixed core extension filter, matched case-insensitively), without its binary
check and with symlink confinement: a file that resolves outside the mount
root (or a dangling symlink) is dropped. Declaration files (`.d.ts`,
`.d.mts`, `.d.cts`) are always dropped silently.

The logic lives in `code_check.docker_check.selection`; `select_files` here
binds the extensions, the default excludes and the declaration-file skip.
"""

from __future__ import annotations

from pathlib import Path

from code_check.docker_check import selection as docker_check_selection
from code_check.docker_check.selection import Selection, build_selection, unsendable_reason
from code_check.js_complexity.constants import Constants

__all__ = ["Selection", "build_selection", "is_declaration", "select_files", "unsendable_reason"]


def is_declaration(path: Path) -> bool:
    """Return True for a TypeScript declaration file (by name, case-insensitively)."""
    return path.name.lower().endswith(Constants.DECLARATION_SUFFIXES)


def select_files(
    target: Path,
    root: Path,
    *,
    excludes: list[str] | None = None,
    ignore: list[str] | None = None,
    include: list[str] | None = None,
    gitignore: bool = False,
) -> Selection:
    """Collect the JS/TS files under `target` (or `target` itself) for the mount `root`.

    `excludes` are directory names (default: `Constants.DEFAULT_EXCLUDES`; not
    applied to a single file), `ignore`/`include` are globs relative to
    `target` and `gitignore` skips the untracked files git ignores (off
    here; the executor always passes it, on unless `--no-gitignore`). There
    is no binary check, so non-UTF-8 files still reach the image, and files
    resolving outside the mount root are dropped. Declaration files are
    always skipped.
    """
    return docker_check_selection.select_files(
        target,
        root,
        extensions=Constants.EXTENSIONS,
        excludes=Constants.DEFAULT_EXCLUDES if excludes is None else excludes,
        ignore=ignore,
        include=include,
        gitignore=gitignore,
        skip=is_declaration,
    )
