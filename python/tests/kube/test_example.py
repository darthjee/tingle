"""Unit tests for kube.example and `tingle kube example`."""

from __future__ import annotations

from kube.example import EXAMPLE_PATH, print_example
from kube.executor import Kube


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
