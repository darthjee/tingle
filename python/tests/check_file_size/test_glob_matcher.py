"""Unit tests for check_file_size.glob_matcher.GlobMatcher."""

from __future__ import annotations

import pytest

from check_file_size.glob_matcher import GlobMatcher


@pytest.mark.parametrize(
    ("pattern", "path", "expected"),
    [
        # `*`: any run of characters except `/`, may be empty
        ("*.py", "a.py", True),
        ("*.py", ".py", True),
        ("a*.py", "a.py", True),
        ("src/*.py", "src/x/a.py", False),
        # `?`: exactly one character except `/`
        ("a?.py", "ab.py", True),
        ("a?.py", "a.py", False),
        ("a?.py", "abc.py", False),
        ("src?a.py", "src/a.py", False),
        # character classes
        ("[abc].py", "b.py", True),
        ("[abc].py", "d.py", False),
        ("[a-c].py", "c.py", True),
        ("[a-c].py", "d.py", False),
        ("[!abc].py", "d.py", True),
        ("[!abc].py", "a.py", False),
        ("src[!x]a.py", "src/a.py", False),
        ("src[+-0]a.py", "src/a.py", False),
        ("src[+-0]a.py", "src-a.py", True),
        ("[]].py", "].py", True),
        ("[^a].py", "^.py", True),
        ("[^a].py", "b.py", False),
        # unclosed `[` is a literal `[`
        ("[abc.py", "[abc.py", True),
        ("[abc.py", "a.py", False),
        # escapes
        (r"\*.py", "*.py", True),
        (r"\*.py", "a.py", False),
        (r"\?.py", "?.py", True),
        (r"\[a].py", "[a].py", True),
        (r"\[a].py", "a.py", False),
        # `**` inside a segment is the same as `*`
        ("a**b.py", "axyb.py", True),
        ("src/a**b.py", "src/a/b.py", False),
        # regex specials are literal
        ("a+b.py", "a+b.py", True),
        ("a.py", "aXpy", False),
        ("(a).py", "(a).py", True),
    ],
)
def test_tokens(pattern, path, expected):
    assert GlobMatcher([pattern]).matches(path) is expected


@pytest.mark.parametrize(
    ("pattern", "path", "expected"),
    [
        # unanchored: no `/` matches in any directory
        ("*.py", "a.py", True),
        ("*.py", "x/y/a.py", True),
        ("*.test.js", "src/b.test.js", True),
        # anchored: a `/` anchors the pattern at the root
        ("*/a.py", "x/a.py", True),
        ("*/a.py", "a.py", False),
        ("*/a.py", "x/y/a.py", False),
        ("src/*.py", "src/a.py", True),
        ("src/*.py", "lib/src/a.py", False),
        # leading `/` only marks the anchor
        ("/src/*.py", "src/a.py", True),
        ("/src/*.py", "lib/src/a.py", False),
        ("/main.py", "main.py", True),
        ("/main.py", "x/main.py", False),
        # trailing `/` matches everything under that directory
        ("fixtures/", "fixtures/a.json", True),
        ("fixtures/", "tests/fixtures/x/a.json", True),
        ("fixtures/", "fixtures", False),
        ("fixtures/", "myfixtures/a.json", False),
        ("src/gen/", "src/gen/a.py", True),
        ("src/gen/", "src/gen/x/a.py", True),
        ("src/gen/", "lib/src/gen/a.py", False),
    ],
)
def test_anchoring(pattern, path, expected):
    assert GlobMatcher([pattern]).matches(path) is expected


@pytest.mark.parametrize(
    ("pattern", "path", "expected"),
    [
        # at the start
        ("**/a.py", "a.py", True),
        ("**/a.py", "x/y/a.py", True),
        ("**/a.py", "x/ba.py", False),
        # in the middle
        ("a/**/b", "a/b", True),
        ("a/**/b", "a/x/b", True),
        ("a/**/b", "a/x/y/b", True),
        ("a/**/b", "a/xb", False),
        ("a/**/b", "c/a/b", False),
        # at the end
        ("docs/**", "docs/a.md", True),
        ("docs/**", "docs/x/y/a.md", True),
        ("docs/**", "docs", False),
        ("docs/**", "lib/docs/a.md", False),
        # alone
        ("**", "a.py", True),
        ("**", "x/y/a.py", True),
    ],
)
def test_double_star_segment(pattern, path, expected):
    assert GlobMatcher([pattern]).matches(path) is expected


@pytest.mark.parametrize(
    ("pattern", "path"),
    [
        ("*.test.js", "src/b.TEST.js"),
        ("SRC/*.PY", "src/a.py"),
        ("[A-C].py", "b.py"),
    ],
)
def test_case_insensitive(pattern, path):
    assert GlobMatcher([pattern]).matches(path)


@pytest.mark.parametrize(
    ("pattern", "path"),
    [
        ("a.py", "a.pyc"),
        ("a.py", "ba.py"),
        ("src/a.py", "src/a.py/b"),
        ("src", "src/a.py"),
    ],
)
def test_full_match_only(pattern, path):
    assert not GlobMatcher([pattern]).matches(path)


def test_star_matches_dot_files():
    assert GlobMatcher(["*"]).matches(".env")
    assert GlobMatcher(["*"]).matches("config/.env")


def test_any_pattern_matches():
    matcher = GlobMatcher(["docs/**", "*.md"])

    assert matcher.matches("docs/a.txt")
    assert matcher.matches("README.md")
    assert not matcher.matches("src/a.py")


def test_empty_list_matches_nothing():
    assert not GlobMatcher([]).matches("a.py")


@pytest.mark.parametrize("pattern", ["", "/", "//"])
def test_empty_pattern_is_dropped(pattern):
    matcher = GlobMatcher([pattern])

    assert not matcher.matches("a.py")
    assert not matcher.matches("")


def test_empty_pattern_does_not_affect_others():
    matcher = GlobMatcher(["", "*.py"])

    assert matcher.matches("a.py")
    assert not matcher.matches("a.js")


def test_trailing_backslash_is_literal():
    assert GlobMatcher(["a\\"]).matches("a\\")


def test_bool_reflects_compiled_patterns():
    assert GlobMatcher(["*.py"])
    assert not GlobMatcher([])
    assert not GlobMatcher(["", "/"])
