#!/usr/bin/env python3
"""main.py — Flow-verb dispatcher entrypoint for the deprecated check_file_size alias.

`cli` invokes this file with a flow verb as the first argument
(e.g. `run`) followed by the command's own arguments. `run` prints a
deprecation warning to stderr (yellow when stderr is a TTY and `NO_COLOR` is
unset) and then forwards the arguments unchanged to `code_check.file_size`,
so `tingle check_file_size` behaves exactly like
`tingle code_check file_size`: same stdout and same exit status. The alias
will be removed in a future release.

There is deliberately no `complete` flow, so the alias keeps the hub's
file/folder completion (and completion never prints the warning).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from code_check.file_size.executor import CheckFileSize
from code_check.palette import Palette

WARNING = (
    "Warning: 'tingle check_file_size' is deprecated; "
    "use 'tingle code_check file_size'."
)


def warn_deprecated() -> None:
    """Print the deprecation warning to stderr, coloured when supported."""
    p = Palette(sys.stderr)
    print(f"{p.YELLOW}{WARNING}{p.RESET}", file=sys.stderr)


def main() -> None:
    flow = sys.argv[1]
    args = sys.argv[2:]
    if flow == "run":
        warn_deprecated()
        CheckFileSize().run(args)


if __name__ == "__main__":
    main()
