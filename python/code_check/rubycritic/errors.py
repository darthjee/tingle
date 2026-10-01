"""errors.py — The error raised by the rubycritic helpers."""

from __future__ import annotations


class RubycriticError(Exception):
    """A failure carrying the user-facing message (printed as `Error: <message>`)."""

    def __init__(self, message: str):
        """Store the user-facing `message`."""
        super().__init__(message)
        self.message = message
