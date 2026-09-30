"""palette.py — Stream-aware ANSI colour codes for check_file_size.

A `Palette` exposes the same colour names as `Constants` (`RESET`, `BOLD`,
`DIM`, `GREEN`, `YELLOW`, `RED`, `MAGENTA`, `CYAN`, `GRAY`). Each one holds
the raw ANSI code when the stream is a TTY and `NO_COLOR` is unset or empty,
and `""` otherwise, so the output keeps its layout without escape codes.
"""

from __future__ import annotations

import os
import sys
from typing import TextIO

from .constants import Constants


class Palette:
    """Colour codes resolved for a given output stream."""

    NAMES = ("RESET", "BOLD", "DIM", "GREEN", "YELLOW", "RED", "MAGENTA", "CYAN", "GRAY")

    def __init__(self, stream: TextIO | None = None):
        """Resolve colours for `stream` (defaults to the current `sys.stdout`)."""
        self.enabled = self.supports_color(sys.stdout if stream is None else stream)
        self.RESET = self._code("RESET")
        self.BOLD = self._code("BOLD")
        self.DIM = self._code("DIM")
        self.GREEN = self._code("GREEN")
        self.YELLOW = self._code("YELLOW")
        self.RED = self._code("RED")
        self.MAGENTA = self._code("MAGENTA")
        self.CYAN = self._code("CYAN")
        self.GRAY = self._code("GRAY")

    @staticmethod
    def supports_color(stream: TextIO) -> bool:
        """Return True when `stream` is a TTY and `NO_COLOR` is unset or empty."""
        if os.environ.get("NO_COLOR"):
            return False
        isatty = getattr(stream, "isatty", None)
        if not callable(isatty):
            return False
        try:
            return bool(isatty())
        except (OSError, ValueError):
            return False

    def _code(self, name: str) -> str:
        """Return the raw ANSI code for `name`, or `""` when colour is disabled."""
        return getattr(Constants, name) if self.enabled else ""

    def level_color(self, level: str) -> str:
        """Return the colour used for a classification level key."""
        return {
            "critical": self.MAGENTA + self.BOLD,
            "error": self.RED + self.BOLD,
            "warn": self.YELLOW,
            "ok": self.GREEN,
        }[level]
