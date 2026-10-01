"""subcommands.py — Names of the `tingle code_check` subcommands.

Kept import-light so `code_check.completion` can read the names without
importing any subcommand implementation. `CodeCheck.SUBCOMMANDS` in
`code_check.executor` uses exactly these keys, in this order.
"""

from __future__ import annotations

SUBCOMMAND_NAMES: tuple[str, ...] = ("file_size", "rubycritic")
