"""Unit tests for code_check.excludes."""

from __future__ import annotations

import pytest

from code_check.excludes import parse_excludes, resolve_excludes


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" a , ,b,, c ", ["a", "b", "c"]),
        ("", []),
        (None, []),
        ("single", ["single"]),
    ],
)
def test_parse_excludes(raw, expected):
    assert parse_excludes(raw) == expected


@pytest.mark.parametrize(
    ("extra", "no_defaults", "expected"),
    [
        ([], False, ["x", "y"]),
        (["z"], False, ["x", "y", "z"]),
        (["y", "z", "z"], False, ["x", "y", "z"]),
        (["z"], True, ["z"]),
        ([], True, []),
    ],
)
def test_resolve_excludes(extra, no_defaults, expected):
    assert resolve_excludes(["x", "y"], extra, no_defaults) == expected


def test_resolve_excludes_does_not_mutate_inputs():
    defaults = ["x"]
    extra = ["y"]

    resolve_excludes(defaults, extra, False)

    assert defaults == ["x"]
    assert extra == ["y"]


def test_resolve_excludes_accepts_tuples():
    assert resolve_excludes(("x",), ["y"], False) == ["x", "y"]
