"""git_ignore.py — Ask git which untracked files under a directory are ignored.

Runs `git -C <root> ls-files --others --ignored --exclude-standard --directory -z`
once and returns the result as a `GitIgnored` set. Tracked files are never
reported (as git does). When git is missing, `<root>` is not in a work tree or
the call fails, `GitIgnore.ignored_paths` returns `None` (nothing ignored).
"""

from __future__ import annotations

import subprocess  # nosec B404 - fixed `git` binary, list-form args, no shell
from pathlib import Path

GIT_COMMAND = [
    "ls-files",
    "--others",
    "--ignored",
    "--exclude-standard",
    "--directory",
    "-z",
]


class GitIgnored:
    """The set of paths git ignores: individual files plus directory prefixes."""

    def __init__(self, files: set[Path], dirs: list[Path]):
        """Store absolute ignored `files` and ignored directory prefixes `dirs`."""
        self.files = files
        self.dirs = dirs

    def contains(self, path: Path) -> bool:
        """Return `True` when `path` is an ignored file or lies under an ignored directory."""
        if path in self.files:
            return True
        return any(path.is_relative_to(directory) for directory in self.dirs)


class GitIgnore:
    """Query git for the ignored, untracked files under a directory."""

    @staticmethod
    def ignored_paths(root: Path) -> GitIgnored | None:
        """Return the paths git ignores under `root`, or `None` when git can't tell."""
        try:
            result = subprocess.run(  # nosec B603, B607 - fixed binary, list-form args, no shell
                ["git", "-C", str(root), *GIT_COMMAND],
                capture_output=True,
                check=False,
            )
        except OSError:
            return None
        if result.returncode != 0:
            return None
        return GitIgnore.parse(root, result.stdout)

    @staticmethod
    def parse(root: Path, output: bytes) -> GitIgnored:
        """Parse NUL-separated `ls-files` output; entries ending in `/` are directories."""
        files: set[Path] = set()
        dirs: list[Path] = []
        for entry in output.decode("utf-8", errors="surrogateescape").split("\0"):
            if not entry:
                continue
            if entry.endswith("/"):
                dirs.append(root / entry.rstrip("/"))
            else:
                files.add(root / entry)
        return GitIgnored(files, dirs)
