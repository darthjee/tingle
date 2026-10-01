"""excludes.py — Parse and resolve directory-name excludes for code_check subcommands.

Shared by `file_size` and `rubycritic`: `parse_excludes` splits the
comma-separated `--exclude` value and `resolve_excludes` merges it with a
subcommand's default excludes.

Dependencies: standard library only.
"""

from __future__ import annotations

from collections.abc import Iterable


def parse_excludes(raw: str | None) -> list[str]:
    """Split a comma-separated exclude list, dropping blank entries (`None`: empty)."""
    return [e.strip() for e in (raw or "").split(",") if e.strip()]


def resolve_excludes(
    defaults: Iterable[str], extra: list[str], no_default_excludes: bool
) -> list[str]:
    """Merge `defaults` with the `extra` names, deduplicated, defaults first.

    The defaults are dropped when `no_default_excludes` is set. `defaults` is
    never mutated.
    """
    base = [] if no_default_excludes else list(defaults)
    return list(dict.fromkeys(base + list(extra)))
