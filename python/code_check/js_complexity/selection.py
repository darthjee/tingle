"""selection.py — Select the JavaScript/TypeScript files sent to the FTA container.

A `Selection` holds the mount root, the lines sent on the container's stdin
(paths relative to the root, POSIX separators, sorted) and the warnings for
the files whose name cannot be sent (a newline, or not valid UTF-8).

Files are collected with `file_size`'s `FileCollector` (default excludes, the
fixed extension filter, matched case-insensitively), without its binary check
and with symlink confinement: a file that resolves outside the mount root (or
a dangling symlink) is dropped. The filter holds the core extensions and the
.vue, .svelte and .astro single-file components (their <script> blocks and
Astro frontmatter only); no skip rule applies to the components. Declaration
files (`.d.ts`, `.d.mts`, `.d.cts`) are always dropped silently; minified
bundles (`.min.js`, `.min.mjs`, `.min.cjs`) are dropped silently too unless
`skip_minified` is false (`--no-default-excludes`).

The logic lives in `code_check.docker_check.selection`; `select_files` here
binds the extensions (core and SFC), the default excludes, the
declaration-file skip and the minified-bundle skip.
"""

from __future__ import annotations

from pathlib import Path

from code_check.docker_check import selection as docker_check_selection
from code_check.docker_check.selection import Selection, build_selection, unsendable_reason
from code_check.js_complexity.constants import Constants

__all__ = [
    "Selection",
    "build_selection",
    "is_declaration",
    "is_minified",
    "select_files",
    "unsendable_reason",
]


def is_declaration(path: Path) -> bool:
    """Return True for a TypeScript declaration file (by name, case-insensitively)."""
    return path.name.lower().endswith(Constants.DECLARATION_SUFFIXES)


def is_minified(path: Path) -> bool:
    """Return True for a minified bundle (by name, case-insensitively)."""
    return path.name.lower().endswith(Constants.MINIFIED_SUFFIXES)


def select_files(
    target: Path,
    root: Path,
    *,
    excludes: list[str] | None = None,
    ignore: list[str] | None = None,
    include: list[str] | None = None,
    gitignore: bool = False,
    skip_minified: bool = True,
) -> Selection:
    """Collect the JS/TS and SFC files under `target` (or `target` itself) for the mount `root`.

    `excludes` are directory names (default: `Constants.DEFAULT_EXCLUDES`; not
    applied to a single file), `ignore`/`include` are globs relative to
    `target` and `gitignore` skips the untracked files git ignores (off
    here; the executor always passes it, on unless `--no-gitignore`). There
    is no binary check, so non-UTF-8 files still reach the image, and files
    resolving outside the mount root are dropped. Declaration files are
    always skipped; minified bundles are skipped when `skip_minified` is
    true (the default), for a directory and a single-file `target` alike,
    and `include` never brings them back.
    """

    def skip(path: Path) -> bool:
        if is_declaration(path):
            return True
        return skip_minified and is_minified(path)

    return docker_check_selection.select_files(
        target,
        root,
        extensions=[*Constants.EXTENSIONS, *Constants.SFC_EXTENSIONS],
        excludes=Constants.DEFAULT_EXCLUDES if excludes is None else excludes,
        ignore=ignore,
        include=include,
        gitignore=gitignore,
        skip=skip,
    )
