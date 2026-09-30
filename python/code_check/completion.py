"""completion.py — Bash-completion candidate resolution for code_check.

`commands.sh` invokes `main.py complete "${COMP_WORDS[@]:2}"`: the raw words
after `code_check`, including a possibly-empty trailing element for the word
being typed. The hub filters candidates by prefix itself, so this module
returns the *full* candidate set for the cursor position and never filters.

The result is either a word list or exactly `["__tingle_files__"]` (the hub's
file/folder sentinel), never both. Committed words are scanned by position
without `argparse`.

Only argv and `code_check.file_size.flags.FLAGS` are inspected: no config
read, no `git` call, no filesystem walk and no network, so every keystroke
stays fast and side-effect-free.
"""

from __future__ import annotations

from code_check.file_size.flags import FLAGS
from code_check.subcommands import SUBCOMMAND_NAMES

FILES_SENTINEL = "__tingle_files__"
HELP_FLAGS = ("-h", "--help")

# Value-free actions: the flag never consumes the next word.
_NO_VALUE_ACTIONS = ("store_true", "store_false", "count", "help", "version")

FILE_SIZE_FLAGS: list[str] = [f["name"] for f in FLAGS if f["name"].startswith("-")]
# Flag name → its `choices` (empty list when the value is free-form).
FILE_SIZE_VALUE_FLAGS: dict[str, list[str]] = {
    f["name"]: list(f.get("choices") or [])
    for f in FLAGS
    if f["name"].startswith("-") and f.get("action") not in _NO_VALUE_ACTIONS
}


def complete(argv: list[str]) -> list[str]:
    """Return the full candidate set for the cursor position implied by `argv`."""
    committed = argv[:-1] if argv else []
    current = argv[-1] if argv else ""

    if committed and committed[0] in HELP_FLAGS:
        # `-h <sub> ...` is forwarded as `<sub> -h ...`.
        committed = committed[1:]
    if not committed:
        return list(SUBCOMMAND_NAMES)
    if committed[0] == "file_size":
        return _complete_file_size(committed[1:], current)
    return []


def _complete_file_size(committed: list[str], current: str) -> list[str]:
    """Candidates for `code_check file_size <committed...> <current>`."""
    has_path, pending = _scan(committed)
    if pending is not None:
        return list(FILE_SIZE_VALUE_FLAGS[pending])
    if current.startswith("-") or has_path:
        return list(FILE_SIZE_FLAGS)
    return [FILES_SENTINEL]


def _scan(tokens: list[str]) -> tuple[bool, str | None]:
    """Scan `tokens` by position.

    Returns `(has_path, pending_flag)`: whether the positional path was given,
    and the value-taking flag still waiting for its value (or None).
    """
    has_path = False
    pending: str | None = None
    for token in tokens:
        if pending is not None:
            pending = None
        elif token in FILE_SIZE_VALUE_FLAGS:
            pending = token
        elif not token.startswith("-"):
            has_path = True
    return has_path, pending
