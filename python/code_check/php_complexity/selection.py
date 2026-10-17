"""selection.py — Select the PHP files sent to the PDepend container.

A `Selection` holds the mount root, the lines sent on the container's stdin
(paths relative to the root, POSIX separators, sorted) and the warnings for
the files whose name cannot be sent (a newline, or not valid UTF-8).

Files are collected with `file_size`'s `FileCollector` (default excludes, the
`.php` extension filter, matched case-insensitively), without its binary
check and with symlink confinement: a file that resolves outside the mount
root (or a dangling symlink) is dropped. Blade templates (`*.blade.php`) are
always dropped silently; files under a `bootstrap/cache` directory pair
(relative to a directory `target`) are dropped silently too unless
`skip_bootstrap_cache` is false.

The logic lives in `code_check.docker_check.selection`; `select_files` here
binds the extension, the default excludes and the skip rules.
"""

from __future__ import annotations

from pathlib import Path

from code_check.docker_check import selection as docker_check_selection
from code_check.docker_check.selection import Selection, build_selection, unsendable_reason
from code_check.php_complexity.constants import Constants

__all__ = [
    "Selection",
    "build_selection",
    "in_bootstrap_cache",
    "is_blade",
    "select_files",
    "unsendable_reason",
]


def is_blade(path: Path) -> bool:
    """Return True for a Blade template (by name, case-insensitively)."""
    return path.name.lower().endswith(Constants.BLADE_SUFFIX)


def in_bootstrap_cache(path: Path, target: Path) -> bool:
    """Return True when `path`'s directories under `target` hold `bootstrap` then `cache`.

    The comparison is case-insensitive and ignores the file name; the two
    segments must be adjacent.
    """
    try:
        parts = path.relative_to(target).parts[:-1]
    except ValueError:
        return False
    lowered = [part.lower() for part in parts]
    pair = list(Constants.BOOTSTRAP_CACHE)
    return any(lowered[i:i + 2] == pair for i in range(len(lowered) - 1))


def select_files(
    target: Path,
    root: Path,
    *,
    excludes: list[str] | None = None,
    ignore: list[str] | None = None,
    include: list[str] | None = None,
    gitignore: bool = False,
    skip_bootstrap_cache: bool = True,
) -> Selection:
    """Collect the PHP files under `target` (or `target` itself) for the mount `root`.

    `excludes` are directory names (default: `Constants.DEFAULT_EXCLUDES`; not
    applied to a single file), `ignore`/`include` are globs relative to
    `target` and `gitignore` skips the untracked files git ignores (off by
    default until the selection flags land). There is no binary check, so
    non-UTF-8 files still reach the image, and files resolving outside the
    mount root are dropped. Blade templates are always skipped; the
    `bootstrap/cache` rule applies when `skip_bootstrap_cache` is true and
    `target` is a directory.
    """
    check_cache = skip_bootstrap_cache and target.is_dir()

    def skip(path: Path) -> bool:
        if is_blade(path):
            return True
        return check_cache and in_bootstrap_cache(path, target)

    return docker_check_selection.select_files(
        target,
        root,
        extensions=Constants.EXTENSIONS,
        excludes=Constants.DEFAULT_EXCLUDES if excludes is None else excludes,
        ignore=ignore,
        include=include,
        gitignore=gitignore,
        skip=skip,
    )
