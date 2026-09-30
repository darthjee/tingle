"""Unit tests for check_file_size.palette.Palette."""

from __future__ import annotations

import io

import pytest

from check_file_size.constants import Constants
from check_file_size.palette import Palette


class FakeTTY(io.StringIO):
    """In-memory stream that reports itself as a TTY."""

    def isatty(self) -> bool:
        return True


class BrokenTTY(io.StringIO):
    """Stream whose isatty() raises, as a closed stream would."""

    def isatty(self) -> bool:
        raise ValueError("I/O operation on closed file")


@pytest.fixture(autouse=True)
def _no_color_unset(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)


def test_tty_without_no_color_uses_raw_codes():
    palette = Palette(FakeTTY())

    assert palette.enabled is True
    for name in Palette.NAMES:
        assert getattr(palette, name) == getattr(Constants, name)


def test_non_tty_stream_disables_colours():
    palette = Palette(io.StringIO())

    assert palette.enabled is False
    for name in Palette.NAMES:
        assert getattr(palette, name) == ""


def test_no_color_env_disables_colours_on_tty(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")

    palette = Palette(FakeTTY())

    assert palette.enabled is False
    assert palette.RED == ""


def test_empty_no_color_env_keeps_colours(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "")

    assert Palette(FakeTTY()).enabled is True


def test_stream_without_isatty_disables_colours():
    assert Palette(object()).enabled is False


def test_stream_whose_isatty_raises_disables_colours():
    assert Palette(BrokenTTY()).enabled is False


def test_defaults_to_current_stdout(capsys):
    # pytest's capsys stdout is not a TTY
    assert Palette().enabled is False


@pytest.mark.parametrize(
    "level, expected",
    [
        ("critical", Constants.MAGENTA + Constants.BOLD),
        ("error", Constants.RED + Constants.BOLD),
        ("warn", Constants.YELLOW),
        ("ok", Constants.GREEN),
    ],
)
def test_level_color_when_enabled(level, expected):
    assert Palette(FakeTTY()).level_color(level) == expected


@pytest.mark.parametrize("level", ["critical", "error", "warn", "ok"])
def test_level_color_when_disabled(level):
    assert Palette(io.StringIO()).level_color(level) == ""
