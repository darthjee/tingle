"""executor.py — Subcommand dispatcher for `tingle code_check`.

`CodeCheck.run` looks the first word up in the static `SUBCOMMANDS` table and
forwards the remaining words to that subcommand's `run`. User input is only
used as a dict key; nothing is imported or resolved dynamically.

Usage:
    tingle code_check                      # list the subcommands
    tingle code_check -h <subcommand>      # same as <subcommand> -h
    tingle code_check file_size <path> [options]

Exit status: 0 for help, 1 for an unknown or misplaced word; a subcommand's
own exit status (e.g. 2 for `file_size --fail-on`) is forwarded unchanged.
"""

from __future__ import annotations

import sys
from typing import ClassVar

from code_check.file_size.executor import CheckFileSize
from code_check.palette import Palette

HELP_FLAGS = ("-h", "--help")


class CodeCheck:
    """Dispatch `tingle code_check <subcommand> ...` to the subcommand class."""

    # Subcommand name → (class with a `run(args)` method, one-line description).
    # Keys match `code_check.subcommands.SUBCOMMAND_NAMES`, read by completion.
    SUBCOMMANDS: ClassVar[dict[str, tuple[type, str]]] = {
        "file_size": (CheckFileSize, "Token efficiency triage: file size analysis."),
    }

    def run(self, args: list[str]) -> None:
        """Dispatch `args[0]` to its subcommand, forwarding `args[1:]`."""
        if not args or (len(args) == 1 and args[0] in HELP_FLAGS):
            self._print_list(sys.stdout)
            sys.exit(0)

        if args[0] in HELP_FLAGS:
            # `-h <sub> ...` behaves as `<sub> -h ...`.
            args = [args[1], args[0], *args[2:]]

        name = args[0]
        if name.startswith("-"):
            self._fail(f"expected a subcommand before options (got '{name}')")
        if name not in self.SUBCOMMANDS:
            self._fail(f"unknown subcommand '{name}'")

        cls, _ = self.SUBCOMMANDS[name]
        cls().run(args[1:])

    @classmethod
    def _print_list(cls, stream) -> None:
        """Print the available subcommands and how to get their options."""
        print("usage: tingle code_check <subcommand> [options]", file=stream)
        print(file=stream)
        print("Subcommands:", file=stream)
        width = max(len(name) for name in cls.SUBCOMMANDS)
        for name, (_, description) in cls.SUBCOMMANDS.items():
            print(f"  {name.ljust(width)}  {description}", file=stream)
        print(file=stream)
        print("Run 'tingle code_check <subcommand> --help' for its options.", file=stream)

    @classmethod
    def _fail(cls, message: str) -> None:
        """Print `Error: <message>` in red plus the list on stderr, then exit 1."""
        err = Palette(sys.stderr)
        print(f"{err.RED}Error: {message}{err.RESET}", file=sys.stderr)
        cls._print_list(sys.stderr)
        sys.exit(1)
