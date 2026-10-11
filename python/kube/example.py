"""example.py — Print the kube end-to-end walkthrough.

Backs `tingle kube example`: reads `examples/kube/end_to_end.txt` (shipped
at the repository / release root) and writes it to stdout unchanged. Never
loads or creates the kube config and never calls `aws`, `kubectx`, or
`kubectl`.

Usage:
    tingle kube example
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

EXAMPLE_PATH = Path(__file__).resolve().parents[2] / "examples" / "kube" / "end_to_end.txt"


def print_example() -> None:
    """Write the end-to-end walkthrough to stdout, verbatim.

    Exits quietly when stdout is closed early (e.g. `tingle kube example |
    head`), redirecting stdout to devnull so the interpreter's final flush
    does not raise again.
    """
    text = EXAMPLE_PATH.read_text(encoding="utf-8")
    try:
        sys.stdout.write(text)
        sys.stdout.flush()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(devnull, sys.stdout.fileno())
        except (OSError, ValueError, AttributeError):
            pass
        finally:
            os.close(devnull)
        sys.exit(1)  # Python's documented exit status on EPIPE
