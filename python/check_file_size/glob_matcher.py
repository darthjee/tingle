"""glob_matcher.py — Match relative POSIX paths against `.gitignore`-style globs."""

from __future__ import annotations

import re

# Characters that must be escaped inside a regex character class.
_CLASS_SPECIALS = {"\\", "^", "[", "]", "&", "~", "|"}


class GlobMatcher:
    """Match relative POSIX paths against `.gitignore`-style globs (case-insensitive)."""

    def __init__(self, patterns: list[str]):
        """Compile each non-empty pattern once, with `re.IGNORECASE`."""
        self._regexes = [
            re.compile(self.translate(pattern), re.IGNORECASE)
            for pattern in patterns
            if pattern and pattern.strip("/")
        ]

    def matches(self, rel_path: str) -> bool:
        """Return `True` when any pattern fully matches `rel_path` (`False` with no patterns)."""
        return any(regex.fullmatch(rel_path) for regex in self._regexes)

    @classmethod
    def translate(cls, pattern: str) -> str:
        """Translate one glob into a regex string (to be used with `fullmatch`)."""
        segments = cls._anchor(pattern).split("/")
        last = len(segments) - 1
        out = []
        for index, segment in enumerate(segments):
            if segment == "**":
                out.append(".*" if index == last else "(?:.*/)?")
                continue
            out.append(cls._translate_segment(segment))
            if index != last:
                out.append("/")
        return "".join(out)

    @staticmethod
    def _anchor(pattern: str) -> str:
        """Apply `.gitignore` anchoring: unanchored gets `**/`, trailing `/` gets `/**`."""
        directory = pattern.endswith("/")
        pattern = pattern.rstrip("/")
        if "/" not in pattern:
            pattern = "**/" + pattern
        pattern = pattern.lstrip("/")
        if directory:
            pattern += "/**"
        return pattern

    @classmethod
    def _translate_segment(cls, segment: str) -> str:
        """Translate one path segment (no `/`) into a regex fragment."""
        out = []
        index = 0
        while index < len(segment):
            fragment, index = cls._translate_token(segment, index)
            out.append(fragment)
        return "".join(out)

    @classmethod
    def _translate_token(cls, segment: str, index: int) -> tuple[str, int]:
        """Translate the token starting at `index`; return the fragment and the next index."""
        char = segment[index]
        if char == "\\" and index + 1 < len(segment):
            return re.escape(segment[index + 1]), index + 2
        if char == "*":
            while index < len(segment) and segment[index] == "*":
                index += 1
            return "[^/]*", index
        if char == "?":
            return "[^/]", index + 1
        if char == "[":
            return cls._translate_class(segment, index)
        return re.escape(char), index + 1

    @staticmethod
    def _translate_class(segment: str, index: int) -> tuple[str, int]:
        """Translate a `[...]` class at `index`; an unclosed `[` is a literal `[`."""
        start = index + 1
        negate = start < len(segment) and segment[start] == "!"
        if negate:
            start += 1
        search_from = start + 1 if start < len(segment) and segment[start] == "]" else start
        end = segment.find("]", search_from)
        if end == -1:
            return re.escape("["), index + 1
        body = "".join(
            "\\" + c if c in _CLASS_SPECIALS else c for c in segment[start:end]
        )
        if negate:
            return f"[^/{body}]", end + 1
        return f"(?!/)[{body}]", end + 1
