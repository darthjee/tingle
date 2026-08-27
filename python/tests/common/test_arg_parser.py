"""Unit tests for common.arg_parser.ArgParser."""

from __future__ import annotations

import argparse

import pytest

from common.arg_parser import ArgParser


def _sample_flags() -> list[dict]:
    """Flag shapes mirroring check_file_size._flags()."""
    return [
        {
            "name": "path",
            "type": str,
            "help": "File or directory to analyze (recursive)",
        },
        {
            "name": "--warn",
            "type": int,
            "default": 300,
            "help": "Yellow threshold in lines (default: 300)",
        },
        {
            "name": "--ext",
            "type": str,
            "action": "append",
            "default": None,
            "help": "Filter by extension (can be repeated).",
        },
    ]


def test_parse_returns_dict_with_positional_and_typed_optional():
    result = ArgParser(_sample_flags()).parse(["./src", "--warn", "500"])

    assert result == {"path": "./src", "warn": 500, "ext": None}
    assert isinstance(result, dict)
    assert not isinstance(result, argparse.Namespace)


def test_parse_uses_default_when_flag_omitted():
    result = ArgParser(_sample_flags()).parse(["./src"])

    assert result["warn"] == 300


def test_parse_action_append_accumulates_repeated_flags():
    result = ArgParser(_sample_flags()).parse(["./src", "--ext", ".py", "--ext", ".js"])

    assert result["ext"] == [".py", ".js"]


def test_parse_action_append_stays_none_when_never_passed():
    result = ArgParser(_sample_flags()).parse(["./src"])

    assert result["ext"] is None


def test_parse_falls_back_to_sys_argv_when_argv_not_passed(monkeypatch):
    monkeypatch.setattr("sys.argv", ["check_file_size.py", "./src", "--warn", "10"])

    result = ArgParser(_sample_flags()).parse()

    assert result["path"] == "./src"
    assert result["warn"] == 10


def test_build_returns_usable_argument_parser():
    parser = ArgParser(_sample_flags()).build()

    assert isinstance(parser, argparse.ArgumentParser)
    # Should not raise.
    parser.print_help()


def test_parse_raises_on_missing_required_positional():
    with pytest.raises(SystemExit):
        ArgParser(_sample_flags()).parse([])
