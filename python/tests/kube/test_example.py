"""Unit tests for kube.example and `tingle kube example`."""

from __future__ import annotations

import re
from pathlib import Path

from kube.example import EXAMPLE_PATH, print_example
from kube.executor import Kube

REPO_ROOT = Path(__file__).resolve().parents[3]
RELEASE_SCRIPT = REPO_ROOT / "scripts" / "release_cli.sh"


def _release_variable(name: str) -> str:
    """Extract a `NAME="..."` / `NAME='...'` assignment from release_cli.sh."""
    text = RELEASE_SCRIPT.read_text(encoding="utf-8")
    match = re.search(rf"^{name}=([\"'])(.*?)\1\s*$", text, re.MULTILINE)
    assert match, f"{name} assignment not found in {RELEASE_SCRIPT}"
    return match.group(2)


def test_example_path_exists():
    assert EXAMPLE_PATH.is_file()


def test_example_file_is_ascii_only():
    EXAMPLE_PATH.read_bytes().decode("ascii")


def test_print_example_prints_file_verbatim(capsys):
    print_example()

    assert capsys.readouterr().out == EXAMPLE_PATH.read_text(encoding="utf-8")


def test_run_example_prints_file_verbatim(capsys):
    Kube().run(["example"])

    assert capsys.readouterr().out == EXAMPLE_PATH.read_text(encoding="utf-8")


def test_example_file_is_shipped_by_release_allowlist():
    relative = EXAMPLE_PATH.relative_to(REPO_ROOT)
    includes = _release_variable("INCLUDES").split()

    assert relative.parts[0] in includes


def test_example_file_is_not_pruned_from_release():
    relative = EXAMPLE_PATH.relative_to(REPO_ROOT).as_posix()
    prune_pattern = _release_variable("PRUNE_PATTERN")

    assert not re.search(prune_pattern, relative)
