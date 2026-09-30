#!/usr/bin/env python3
"""main.py — Flow-verb dispatcher entrypoint for code_check.

`cli` invokes this file with a flow verb as the first argument
(e.g. `run`) followed by the command's own arguments.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from code_check.completion import complete
from code_check.executor import CodeCheck


def main() -> None:
    flow = sys.argv[1]
    args = sys.argv[2:]
    if flow == "run":
        CodeCheck().run(args)
    elif flow == "complete":
        print(" ".join(complete(args)))


if __name__ == "__main__":
    main()
