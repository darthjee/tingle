"""Unit tests for code_check.js_complexity.reporter.Reporter."""

from __future__ import annotations

import io

import pytest

from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.js_complexity.output_parser import FileResult, ParsedOutput
from code_check.js_complexity.reporter import Reporter
from code_check.palette import Colors, Palette

HEADER = f"{'Status':<16} {'FTA':>5}  {'Cyclo':>5}  {'Lines':>5}  {'Assessment':<17}  File"
SEPARATOR = f"{'─' * 16} {'─' * 5}  {'─' * 5}  {'─' * 5}  {'─' * 17}  {'─' * 50}"
RULE = "─" * 78

# Spec §6 full example (#320 only).
FULL_EXAMPLE = """\
Status             FTA  Cyclo  Lines  Assessment         File
──────────────── ─────  ─────  ─────  ─────────────────  ──────────────────────────────────────────────────
🔴 ERROR           71.3    136    245  Needs improvement  fixture/complex.ts
✅ OK              37.4      3     18  OK                 fixture/component.tsx
✅ OK              35.1      9     23  OK                 fixture/dup_b.js
✅ OK              35.0      9     23  OK                 fixture/dup_a.js
✅ OK              31.0      3     11  OK                 fixture/widget.jsx
✅ OK               7.7      1      6  OK                 fixture/simple.js
✅ OK               7.3      2      6  OK                 fixture/bom.ts
✅ OK               7.3      2      6  OK                 fixture/crlf.js
✅ OK               7.3      2      6  OK                 fixture/ext/UPPER.JS
✅ OK               7.3      2      6  OK                 fixture/ext/a.mjs
✅ OK               7.3      2      6  OK                 fixture/ext/b.cjs
✅ OK               7.3      2      6  OK                 fixture/ext/c.mts
✅ OK               7.3      2      6  OK                 fixture/ext/d.cts
✅ OK               6.2      5      1  OK                 fixture/bundle.min.js
✅ OK               3.5      1      1  OK                 fixture/short.js
✅ OK               0.0      -      -  -                  fixture/empty.js
⛔ PARSE              -      -      -  -                  fixture/broken.js
⛔ PARSE              -      -      -  -                  fixture/latin1.js

──────────────────────────────────────────────────────────────────────────────
Summary: 18 file(s) | 15 OK | 0 WARN | 1 ERROR | 0 CRITICAL | 2 skipped (parse error)
FTA score: avg 17.39 | max 71.30
"""


class FakeTTY(io.StringIO):
    """In-memory stream that reports itself as a TTY."""

    def isatty(self) -> bool:
        return True


@pytest.fixture
def target(tmp_path):
    path = tmp_path / "fixture"
    path.mkdir()
    return path


def _r(line, score, cyclo=2, lines=6, assessment="OK"):
    return FileResult(line, score, cyclo, lines, assessment)


def _reporter(target, root=None, palette=None, thresholds=(50, 60, 75)):
    analyzer = FileAnalyzer(*thresholds)
    root = target if root is None else root
    return Reporter(analyzer, target, root, palette or Palette(io.StringIO()))


def _parsed(*results, parse_errors=None):
    return ParsedOutput(
        results={r.line: r for r in results}, parse_errors=dict(parse_errors or {})
    )


def _out(capsys):
    return capsys.readouterr().out.splitlines()


def _example():
    results = [
        _r("complex.ts", 71.3, 136, 245, "Needs improvement"),
        _r("component.tsx", 37.4, 3, 18),
        _r("dup_a.js", 35.0, 9, 23),
        _r("dup_b.js", 35.1, 9, 23),
        _r("widget.jsx", 31.0, 3, 11),
        _r("simple.js", 7.7, 1, 6),
        _r("ext/d.cts", 7.3),
        _r("ext/c.mts", 7.3),
        _r("crlf.js", 7.3),
        _r("ext/UPPER.JS", 7.3),
        _r("bom.ts", 7.3),
        _r("ext/a.mjs", 7.3),
        _r("ext/b.cjs", 7.3),
        _r("bundle.min.js", 6.2, 5, 1),
        _r("short.js", 3.5, 1, 1),
        FileResult("empty.js", 0.0),
    ]
    return _parsed(
        *results, parse_errors={"latin1.js": "not UTF-8", "broken.js": "syntax"}
    )


# --- table -------------------------------------------------------------------------


def test_full_example_layout(target, capsys):
    _reporter(target).report(_example())

    assert capsys.readouterr().out == FULL_EXAMPLE


def test_header_and_separator(target, capsys):
    _reporter(target).report(_parsed(_r("a.js", 1.0)))

    assert _out(capsys)[:2] == [HEADER, SEPARATOR]


def test_sort_by_score_then_line(target, capsys):
    _reporter(target).report(
        _parsed(_r("b.js", 10.0), _r("c.js", 20.0), _r("a.js", 10.0), _r("d.js", 0.0))
    )

    files = [line.split()[-1] for line in _out(capsys)[2:6]]
    assert files == ["fixture/c.js", "fixture/a.js", "fixture/b.js", "fixture/d.js"]


def test_sort_rows_is_static():
    rows = Reporter.sort_rows({"b": _r("b", 1.0), "a": _r("a", 1.0), "c": _r("c", 2.0)})

    assert [line for line, _ in rows] == ["c", "a", "b"]


def test_single_file_shows_the_file_name(tmp_path, capsys):
    file = tmp_path / "app.ts"
    file.write_text("x")

    _reporter(file, root=tmp_path).report(_parsed(_r("app.ts", 1.0)))

    assert _out(capsys)[2].endswith("  app.ts")


def test_display_path_for_a_directory_is_relative_to_its_parent(target):
    assert _reporter(target).display_path("src/a.js") == "fixture/src/a.js"


def test_dropped_file_row(target, capsys):
    _reporter(target).report(_parsed(FileResult("empty.js", 0.0)))

    assert _out(capsys)[2] == (
        f"{'✅ OK':<16} {'0.0':>5}  {'-':>5}  {'-':>5}  {'-':<17}  fixture/empty.js"
    )


def test_parse_rows_are_sorted_below_level_rows(target, capsys):
    _reporter(target).report(
        _parsed(_r("a.js", 1.0), parse_errors={"z.js": "m", "b.js": "m"})
    )

    out = _out(capsys)
    assert out[2].endswith("fixture/a.js")
    assert out[3] == f"{'⛔ PARSE':<16} {'-':>5}  {'-':>5}  {'-':>5}  {'-':<17}  fixture/b.js"
    assert out[4].endswith("fixture/z.js")


# --- filters -----------------------------------------------------------------------


def test_top_keeps_first_n_level_rows_and_all_parse_rows(target, capsys):
    _reporter(target).report(
        _parsed(_r("a.js", 70.0), _r("b.js", 55.0), _r("c.js", 1.0), parse_errors={"p.js": "m"}),
        top=1,
    )

    out = _out(capsys)
    assert out[2].endswith("fixture/a.js")
    assert out[3].endswith("fixture/p.js")
    assert out[4] == ""
    assert "Summary: 4 file(s) | 1 OK | 1 WARN | 1 ERROR | 0 CRITICAL" in out[6]


def test_min_level_then_top(target, capsys):
    _reporter(target).report(
        _parsed(_r("a.js", 80.0), _r("b.js", 65.0), _r("c.js", 55.0), _r("d.js", 1.0)),
        min_level="warn",
        top=2,
    )

    out = _out(capsys)
    assert [line.split()[-1] for line in out[2:4]] == ["fixture/a.js", "fixture/b.js"]
    assert out[4] == ""


def test_no_rows_left_prints_note_and_summary(target, capsys):
    _reporter(target).report(_parsed(_r("a.js", 1.0)), min_level="error")

    out = _out(capsys)
    assert out[0] == "No files at or above ERROR."
    assert out[1:] == [
        "",
        RULE,
        "Summary: 1 file(s) | 1 OK | 0 WARN | 0 ERROR | 0 CRITICAL",
        "FTA score: avg 1.00 | max 1.00",
    ]


def test_parse_rows_prevent_the_note(target, capsys):
    _reporter(target).report(
        _parsed(_r("a.js", 1.0), parse_errors={"p.js": "m"}), min_level="critical"
    )

    out = _out(capsys)
    assert out[:2] == [HEADER, SEPARATOR]
    assert out[2].endswith("fixture/p.js")


# --- summary -----------------------------------------------------------------------


def test_summary_without_skipped(target, capsys):
    _reporter(target).report(_parsed(_r("a.js", 10.0), _r("b.js", 20.0)))

    assert _out(capsys)[-2:] == [
        "Summary: 2 file(s) | 2 OK | 0 WARN | 0 ERROR | 0 CRITICAL",
        "FTA score: avg 15.00 | max 20.00",
    ]


def test_summary_only_parse_errors_score_is_na(target, capsys):
    _reporter(target).report(_parsed(parse_errors={"a.js": "m"}))

    assert _out(capsys)[-2:] == [
        "Summary: 1 file(s) | 0 OK | 0 WARN | 0 ERROR | 0 CRITICAL | 1 skipped (parse error)",
        "FTA score: n/a",
    ]


def test_score_line_counts_dropped_files_as_zero():
    rows = [("a", _r("a", 30.0)), ("b", FileResult("b", 0.0))]

    assert Reporter.score_line(rows) == "avg 15.00 | max 30.00"


def test_score_above_100_is_critical(target, capsys):
    _reporter(target).report(_parsed(_r("big.js", 180.4)))

    out = _out(capsys)
    assert out[2].startswith(f"{'🟣 CRITICAL':<16} 180.4")
    assert out[-1] == "FTA score: avg 180.40 | max 180.40"


# --- levels ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("score", "label"),
    [
        (49.9, "✅ OK"),
        (50.0, "⚠️  WARN"),
        (59.9, "⚠️  WARN"),
        (60.0, "🔴 ERROR"),
        (74.9, "🔴 ERROR"),
        (75.0, "🟣 CRITICAL"),
    ],
)
def test_level_boundaries_on_the_rounded_score(target, capsys, score, label):
    _reporter(target).report(_parsed(_r("a.js", score)))

    assert _out(capsys)[2].startswith(f"{label:<16} {score:>5.1f}")


def test_float_thresholds(target, capsys):
    _reporter(target, thresholds=(10.5, 20.25, 30.75)).report(
        _parsed(_r("a.js", 10.5), _r("b.js", 20.2), _r("c.js", 30.8))
    )

    assert _out(capsys)[-2] == "Summary: 3 file(s) | 0 OK | 2 WARN | 0 ERROR | 1 CRITICAL"


# --- colours -----------------------------------------------------------------------


def test_colours_on_a_tty(target, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    palette = Palette(FakeTTY())

    _reporter(target, palette=palette).report(
        _parsed(_r("a.js", 80.0), parse_errors={"p.js": "m"})
    )

    out = capsys.readouterr().out
    assert f"{Colors.MAGENTA}{Colors.BOLD}{'🟣 CRITICAL':<16}{Colors.RESET}" in out
    assert f"{Colors.GRAY}{'⛔ PARSE':<16}{Colors.RESET}" in out
    assert f"{Colors.GRAY}| 1 skipped (parse error){Colors.RESET}" in out
    assert f"{Colors.BOLD}FTA score:{Colors.RESET} avg 80.00 | max 80.00" in out
