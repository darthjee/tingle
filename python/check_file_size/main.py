#!/usr/bin/env python3
"""main.py — Flow-verb dispatcher entrypoint for the check_file_size alias.

`cli` invokes this file with a flow verb as the first argument
(e.g. `run`) followed by the command's own arguments. `run` forwards them
unchanged to `code_check.file_size`, so `tingle check_file_size` behaves
exactly like `tingle code_check file_size`. There is deliberately no
`complete` flow, so the alias keeps the hub's file/folder completion.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from code_check.file_size.executor import CheckFileSize


def main() -> None:
    flow = sys.argv[1]
    args = sys.argv[2:]
    if flow == "run":
        CheckFileSize().run(args)


if __name__ == "__main__":
    main()
