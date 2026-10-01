"""completion.py — Bash-completion candidate resolution for code_check.

`commands.sh` invokes `main.py complete "${COMP_WORDS[@]:2}"`: the raw words
after `code_check`, including a possibly-empty trailing element for the word
being typed. The hub filters candidates by prefix itself, so this module
returns the *full* candidate set for the cursor position and never filters.

The result is either a word list or exactly `["__tingle_files__"]` (the hub's
file/folder sentinel), never both. Committed words are scanned by position
without `argparse`.

Only argv and each subcommand's `flags.FLAGS` (`code_check.file_size.flags`,
`code_check.rubycritic.flags`) are inspected: no config read, no `git` call, no filesystem walk and no network, so every keystroke
stays fast and side-effect-free.
"""

from __future__ import annotations

from code_check.file_size.flags import FLAGS as FILE_SIZE_FLAG_DEFS
from code_check.rubycritic.flags import FLAGS as RUBYCRITIC_FLAG_DEFS
from code_check.subcommands import SUBCOMMAND_NAMES

FILES_SENTINEL = "__tingle_files__"
HELP_FLAGS = ("-h", "--help")

# Value-free actions: the flag never consumes the next word.
_NO_VALUE_ACTIONS = ("store_true", "store_false", "count", "help", "version")


def flag_tables(flags: list[dict]) -> tuple[list[str], dict[str, list[str]]]:
    """Build `(flag_names, value_flags)` from a FLAGS list.

    `flag_names` lists every option name, in order. `value_flags` maps each
    value-taking option to its `choices` (empty list when free-form).
    """
    names = [f["name"] for f in flags if f["name"].startswith("-")]
    value_flags = {
        f["name"]: list(f.get("choices") or [])
        for f in flags
        if f["name"].startswith("-") and f.get("action") not in _NO_VALUE_ACTIONS
    }
    return names, value_flags


# Subcommand name → (flag names, value-taking flag → choices).
SUBCOMMAND_FLAGS: dict[str, tuple[list[str], dict[str, list[str]]]] = {
    "file_size": flag_tables(FILE_SIZE_FLAG_DEFS),
    "rubycritic": flag_tables(RUBYCRITIC_FLAG_DEFS),
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
    tables = SUBCOMMAND_FLAGS.get(committed[0])
    if tables is None:
        return []
    return _complete_subcommand(tables, committed[1:], current)


def _complete_subcommand(
    tables: tuple[list[str], dict[str, list[str]]], committed: list[str], current: str
) -> list[str]:
    """Candidates for `code_check <subcommand> <committed...> <current>`."""
    flag_names, value_flags = tables
    has_path, pending = _scan(committed, value_flags)
    if pending is not None:
        return list(value_flags[pending])
    if current.startswith("-") or has_path:
        return list(flag_names)
    return [FILES_SENTINEL]


def _scan(tokens: list[str], value_flags: dict[str, list[str]]) -> tuple[bool, str | None]:
    """Scan `tokens` by position.

    Returns `(has_path, pending_flag)`: whether the positional path was given,
    and the value-taking flag still waiting for its value (or None).
    """
    has_path = False
    pending: str | None = None
    for token in tokens:
        if pending is not None:
            pending = None
        elif token in value_flags:
            pending = token
        elif not token.startswith("-"):
            has_path = True
    return has_path, pending
