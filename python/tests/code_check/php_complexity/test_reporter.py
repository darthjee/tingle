"""Unit tests for code_check.php_complexity.reporter.Reporter."""

from __future__ import annotations

import io

import pytest

from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.palette import Colors, Palette
from code_check.php_complexity.output_parser import FileResult, ParsedOutput, parse
from code_check.php_complexity.reporter import Reporter
from tests.code_check.php_complexity.sample_output import DETAILED, LINES, dumps

HEADER = f"{'Status':<16} {'CCN':>5}  {'Max':>5}  {'NPath':>7}  {'MI':>5}  {'Lines':>5}  File"
SEPARATOR = f"{'─' * 16} {'─' * 5}  {'─' * 5}  {'─' * 7}  {'─' * 5}  {'─' * 5}  {'─' * 50}"
RULE = "─" * 78

# cli.md §6 full example (#348 only), table and summary.
FULL_EXAMPLE = """\
Status             CCN    Max    NPath     MI  Lines  File
──────────────── ─────  ─────  ───────  ─────  ─────  ──────────────────────────────────────────────────
✅ OK                11      7       36     54     22  fixture/Calculator.php
✅ OK                 6      2        2     78     11  fixture/Shapes.php
✅ OK                 4      3        4     66     12  fixture/helpers.php
✅ OK                 3      3        4     58      9  fixture/dup_a.php
✅ OK                 3      3        4     58      9  fixture/dup_b.php
✅ OK                 2      2        4     66      6  fixture/Anon.php
✅ OK                 2      2        2     80      2  fixture/CVS/legacy.php
✅ OK                 2      1        1     79     11  fixture/Modern.php
✅ OK                 2      2        2     78      2  fixture/UPPER.PHP
✅ OK                 2      2        2     80      2  fixture/bom.php
✅ OK                 2      2        2     80      2  fixture/crlf.php
✅ OK                 2      2        2     90      4  fixture/page.php
✅ OK                 1      1        1     83      2  fixture/latin1.php
✅ OK                 0      -        -      -      -  fixture/bootstrap.php
✅ OK                 0      -        -      -      -  fixture/empty.php
⛔ PARSE              -      -        -      -      -  fixture/attr_anon.php
⛔ PARSE              -      -        -      -      -  fixture/broken.php
⛔ PARSE              -      -        -      -      -  fixture/lenient.php

──────────────────────────────────────────────────────────────────────────────
Summary: 18 file(s) | 15 OK | 0 WARN | 0 ERROR | 0 CRITICAL | 3 skipped (parse error)
CCN: avg 2.80 | max 11.00
"""

# cli.md §6, the same data with --warn 4 --error 6 --critical 10 --min-level warn.
FILTERED_EXAMPLE = """\
Status             CCN    Max    NPath     MI  Lines  File
──────────────── ─────  ─────  ───────  ─────  ─────  ──────────────────────────────────────────────────
🟣 CRITICAL          11      7       36     54     22  fixture/Calculator.php
🔴 ERROR              6      2        2     78     11  fixture/Shapes.php
⚠️  WARN             4      3        4     66     12  fixture/helpers.php
⛔ PARSE              -      -        -      -      -  fixture/attr_anon.php
⛔ PARSE              -      -        -      -      -  fixture/broken.php
⛔ PARSE              -      -        -      -      -  fixture/lenient.php

──────────────────────────────────────────────────────────────────────────────
Summary: 18 file(s) | 12 OK | 1 WARN | 1 ERROR | 1 CRITICAL | 3 skipped (parse error)
CCN: avg 2.80 | max 11.00
"""


# details.md §4: the same data with --warn 4 --error 6 --critical 10
# --min-level warn --details 2.
DETAILS_EXAMPLE = """\
Status             CCN    Max    NPath     MI  Lines  File
──────────────── ─────  ─────  ───────  ─────  ─────  ──────────────────────────────────────────────────
🟣 CRITICAL          11      7       36     54     22  fixture/Calculator.php
                 ccn   7  npath      36  Calculator::grade  (fixture/Calculator.php:22)
                 ccn   3  npath       3  Calculator::sign  (fixture/Calculator.php:12)
🔴 ERROR              6      2        2     78     11  fixture/Shapes.php
                 ccn   2  npath       2  Circle::area  (fixture/Shapes.php:28)
                 ccn   1  npath       1  Square::__construct  (fixture/Shapes.php:12)
⚠️  WARN             4      3        4     66     12  fixture/helpers.php
                 ccn   3  npath       4  clamp  (fixture/helpers.php:3)
                 ccn   1  npath       1  greet  (fixture/helpers.php:14)
⛔ PARSE              -      -        -      -      -  fixture/attr_anon.php
⛔ PARSE              -      -        -      -      -  fixture/broken.php
⛔ PARSE              -      -        -      -      -  fixture/lenient.php

──────────────────────────────────────────────────────────────────────────────
Summary: 18 file(s) | 12 OK | 1 WARN | 1 ERROR | 1 CRITICAL | 3 skipped (parse error)
CCN: avg 2.80 | max 11.00
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


def _r(line, ccn, max_ccn=2, max_npath=4, min_mi=66.0, lloc=6, functions=None):
    return FileResult(line, ccn, max_ccn, max_npath, min_mi, lloc, True, functions=functions)


def _fn(name, line, ccn, npath=1):
    return {"name": name, "line": line, "ccn": ccn, "npath": npath}


def _unit(name, path, line, ccn, npath=1):
    return f"{'':<16} ccn {ccn:>3}  npath {npath:>7}  {name}  ({path}:{line})"


UNAVAILABLE = f"{'':<16} (per-function data unavailable)"


def _reporter(target, root=None, palette=None, thresholds=(20, 40, 60)):
    analyzer = FileAnalyzer(*thresholds)
    root = target if root is None else root
    return Reporter(analyzer, target, root, palette or Palette(io.StringIO()))


def _parsed(*results, parse_errors=None):
    return ParsedOutput(
        results={r.line: r for r in results}, parse_errors=dict(parse_errors or {})
    )


def _out(capsys):
    return capsys.readouterr().out.splitlines()


# --- table -------------------------------------------------------------------------


def test_full_example_layout(target, capsys):
    _reporter(target).report(parse(dumps(), LINES))

    assert capsys.readouterr().out == FULL_EXAMPLE


def test_full_example_with_low_thresholds_and_min_level(target, capsys):
    _reporter(target, thresholds=(4, 6, 10)).report(parse(dumps(), LINES), min_level="warn")

    assert capsys.readouterr().out == FILTERED_EXAMPLE


def test_header_and_separator(target, capsys):
    _reporter(target).report(_parsed(_r("a.php", 1)))

    assert _out(capsys)[:2] == [HEADER, SEPARATOR]


def test_sort_by_ccn_then_line(target, capsys):
    _reporter(target).report(
        _parsed(_r("b.php", 10), _r("c.php", 20), _r("a.php", 10), _r("d.php", 0))
    )

    files = [line.split()[-1] for line in _out(capsys)[2:6]]
    assert files == ["fixture/c.php", "fixture/a.php", "fixture/b.php", "fixture/d.php"]


def test_sort_rows_is_static():
    rows = Reporter.sort_rows({"b": _r("b", 1), "a": _r("a", 1), "c": _r("c", 2)})

    assert [line for line, _ in rows] == ["c", "a", "b"]


def test_single_file_shows_the_file_name(tmp_path, capsys):
    file = tmp_path / "app.php"
    file.write_text("x")

    _reporter(file, root=tmp_path).report(_parsed(_r("app.php", 1)))

    assert _out(capsys)[2].endswith("  app.php")


def test_display_path_for_a_directory_is_relative_to_its_parent(target):
    assert _reporter(target).display_path("src/a.php") == "fixture/src/a.php"


def test_row_without_pdepend_data(target, capsys):
    _reporter(target).report(_parsed(FileResult("empty.php", 0)))

    assert _out(capsys)[2] == (
        f"{'✅ OK':<16} {0:>5}  {'-':>5}  {'-':>7}  {'-':>5}  {'-':>5}  fixture/empty.php"
    )


def test_row_with_null_maxima(target, capsys):
    result = FileResult("Iface.php", 0, None, None, None, 7, True)

    _reporter(target).report(_parsed(result))

    assert _out(capsys)[2] == (
        f"{'✅ OK':<16} {0:>5}  {'-':>5}  {'-':>7}  {'-':>5}  {7:>5}  fixture/Iface.php"
    )


@pytest.mark.parametrize(
    ("mi", "shown"), [(79.502485917776, "80"), (79.49, "79"), (53.875, "54"), (100, "100")]
)
def test_mi_is_rounded_to_an_integer(target, capsys, mi, shown):
    _reporter(target).report(_parsed(_r("a.php", 1, min_mi=mi)))

    assert _out(capsys)[2].split()[5] == shown


def test_large_npath_is_printed_in_full(target, capsys):
    big = 2**53 + 1

    _reporter(target).report(_parsed(_r("a.php", 1, max_npath=big)))

    assert f"  {big}  " in _out(capsys)[2]


def test_parse_rows_are_sorted_below_level_rows(target, capsys):
    _reporter(target).report(
        _parsed(_r("a.php", 1), parse_errors={"z.php": "m", "b.php": "m"})
    )

    out = _out(capsys)
    assert out[2].endswith("fixture/a.php")
    assert out[3] == (
        f"{'⛔ PARSE':<16} {'-':>5}  {'-':>5}  {'-':>7}  {'-':>5}  {'-':>5}  fixture/b.php"
    )
    assert out[4].endswith("fixture/z.php")


# --- filters -----------------------------------------------------------------------


def test_top_keeps_first_n_level_rows_and_all_parse_rows(target, capsys):
    _reporter(target).report(
        _parsed(_r("a.php", 50), _r("b.php", 25), _r("c.php", 1), parse_errors={"p.php": "m"}),
        top=1,
    )

    out = _out(capsys)
    assert out[2].endswith("fixture/a.php")
    assert out[3].endswith("fixture/p.php")
    assert out[4] == ""
    assert "Summary: 4 file(s) | 1 OK | 1 WARN | 1 ERROR | 0 CRITICAL" in out[6]


def test_min_level_then_top(target, capsys):
    _reporter(target).report(
        _parsed(_r("a.php", 70), _r("b.php", 45), _r("c.php", 25), _r("d.php", 1)),
        min_level="warn",
        top=2,
    )

    out = _out(capsys)
    assert [line.split()[-1] for line in out[2:4]] == ["fixture/a.php", "fixture/b.php"]
    assert out[4] == ""


def test_no_rows_left_prints_note_and_summary(target, capsys):
    _reporter(target).report(_parsed(_r("a.php", 1)), min_level="error")

    out = _out(capsys)
    assert out[0] == "No files at or above ERROR."
    assert out[1:] == [
        "",
        RULE,
        "Summary: 1 file(s) | 1 OK | 0 WARN | 0 ERROR | 0 CRITICAL",
        "CCN: avg 1.00 | max 1.00",
    ]


def test_parse_rows_prevent_the_note(target, capsys):
    _reporter(target).report(
        _parsed(_r("a.php", 1), parse_errors={"p.php": "m"}), min_level="critical"
    )

    out = _out(capsys)
    assert out[:2] == [HEADER, SEPARATOR]
    assert out[2].endswith("fixture/p.php")


# --- summary -----------------------------------------------------------------------


def test_summary_without_skipped(target, capsys):
    _reporter(target).report(_parsed(_r("a.php", 10), _r("b.php", 21)))

    assert _out(capsys)[-2:] == [
        "Summary: 2 file(s) | 1 OK | 1 WARN | 0 ERROR | 0 CRITICAL",
        "CCN: avg 15.50 | max 21.00",
    ]


def test_summary_only_parse_errors_ccn_is_na(target, capsys):
    _reporter(target).report(_parsed(parse_errors={"a.php": "m"}))

    assert _out(capsys)[-2:] == [
        "Summary: 1 file(s) | 0 OK | 0 WARN | 0 ERROR | 0 CRITICAL | 1 skipped (parse error)",
        "CCN: n/a",
    ]


def test_score_line_counts_files_without_data_as_zero():
    rows = [("a", _r("a", 30)), ("b", FileResult("b", 0))]

    assert Reporter.score_line(rows) == "avg 15.00 | max 30.00"


# --- levels ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("ccn", "label"),
    [
        (19, "✅ OK"),
        (20, "⚠️  WARN"),
        (39, "⚠️  WARN"),
        (40, "🔴 ERROR"),
        (59, "🔴 ERROR"),
        (60, "🟣 CRITICAL"),
        (250, "🟣 CRITICAL"),
    ],
)
def test_level_boundaries_on_the_total_ccn(target, capsys, ccn, label):
    _reporter(target).report(_parsed(_r("a.php", ccn)))

    assert _out(capsys)[2].startswith(f"{label:<16} {ccn:>5}")


def test_decimal_threshold(target, capsys):
    _reporter(target, thresholds=(2.5, 40, 60)).report(_parsed(_r("a.php", 2), _r("b.php", 3)))

    assert _out(capsys)[-2] == "Summary: 2 file(s) | 1 OK | 1 WARN | 0 ERROR | 0 CRITICAL"


def test_level_ignores_max_npath_and_mi(target, capsys):
    _reporter(target).report(_parsed(_r("a.php", 1, max_ccn=99, max_npath=10**9, min_mi=0.0)))

    assert _out(capsys)[2].startswith(f"{'✅ OK':<16}")


# --- colours -----------------------------------------------------------------------


def test_colours_on_a_tty(target, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    palette = Palette(FakeTTY())

    _reporter(target, palette=palette).report(
        _parsed(_r("a.php", 80), parse_errors={"p.php": "m"})
    )

    out = capsys.readouterr().out
    assert f"{Colors.MAGENTA}{Colors.BOLD}{'🟣 CRITICAL':<16}{Colors.RESET}" in out
    assert f"{Colors.GRAY}{'⛔ PARSE':<16}{Colors.RESET}" in out
    assert f"{Colors.GRAY}| 1 skipped (parse error){Colors.RESET}" in out
    assert f"{Colors.BOLD}CCN:{Colors.RESET} avg 80.00 | max 80.00" in out


# --- details -----------------------------------------------------------------------


def test_details_spec_example(target, capsys):
    _reporter(target, thresholds=(4, 6, 10)).report(
        parse(dumps(DETAILED), LINES), min_level="warn", details=2
    )

    assert capsys.readouterr().out == DETAILS_EXAMPLE


def test_details_none_prints_no_function_lines(target, capsys):
    _reporter(target, thresholds=(4, 6, 10)).report(parse(dumps(DETAILED), LINES), min_level="warn")

    assert "ccn " not in capsys.readouterr().out


def test_details_zero_lists_every_unit_of_shapes(target, capsys):
    _reporter(target, thresholds=(4, 6, 10)).report(
        parse(dumps(DETAILED), LINES), min_level="error", details=0
    )

    out = _out(capsys)
    start = out.index(next(o for o in out if o.endswith("fixture/Shapes.php")))
    assert out[start + 1:start + 6] == [
        _unit("Circle::area", "fixture/Shapes.php", 28, 2, 2),
        _unit("Square::__construct", "fixture/Shapes.php", 12, 1),
        _unit("Square::area", "fixture/Shapes.php", 16, 1),
        _unit("Circle::__construct", "fixture/Shapes.php", 24, 1),
        _unit("Describes::describe", "fixture/Shapes.php", 36, 1),
    ]
    assert out[start + 6].startswith("⛔ PARSE")


def test_details_default_five(target, capsys):
    functions = [_fn(f"f{i}", i, 10 - i) for i in range(1, 8)]

    _reporter(target).report(_parsed(_r("a.php", 49, functions=functions)), details=5)

    out = _out(capsys)
    assert out[3:8] == [_unit(f"f{i}", "fixture/a.php", i, 10 - i) for i in range(1, 6)]
    assert out[8] == ""


def test_details_n_keeps_the_first_n(target, capsys):
    functions = [_fn("a", 1, 1), _fn("b", 2, 5), _fn("c", 3, 3)]

    _reporter(target).report(_parsed(_r("a.php", 9, functions=functions)), details=1)

    out = _out(capsys)
    assert out[3] == _unit("b", "fixture/a.php", 2, 5)
    assert out[4] == ""


def test_details_larger_than_the_list_keeps_all(target, capsys):
    functions = [_fn("a", 1, 1), _fn("b", 2, 5)]

    _reporter(target).report(_parsed(_r("a.php", 6, functions=functions)), details=9)

    assert _out(capsys)[3:5] == [
        _unit("b", "fixture/a.php", 2, 5), _unit("a", "fixture/a.php", 1, 1),
    ]


def test_select_functions_sorts_by_ccn_then_line_then_name():
    functions = [
        _fn("zeta", 10, 2), _fn("alpha", 10, 2), _fn("beta", 3, 2), _fn("top", 50, 9),
        _fn("low", 1, 1),
    ]

    names = [f["name"] for f in Reporter.select_functions(functions, 0)]

    assert names == ["top", "beta", "alpha", "zeta", "low"]


def test_select_functions_keeps_n_or_all():
    functions = [_fn("a", 1, 3), _fn("b", 2, 2), _fn("c", 3, 1)]

    assert [f["name"] for f in Reporter.select_functions(functions, 2)] == ["a", "b"]
    assert [f["name"] for f in Reporter.select_functions(functions, 0)] == ["a", "b", "c"]
    assert Reporter.select_functions([], 3) == []


def test_select_functions_does_not_mutate_the_input():
    functions = [_fn("a", 1, 1), _fn("b", 2, 5)]

    Reporter.select_functions(functions, 1)

    assert [f["name"] for f in functions] == ["a", "b"]


def test_details_only_under_rows_kept_by_top(target, capsys):
    _reporter(target).report(
        _parsed(
            _r("a.php", 9, functions=[_fn("fa", 1, 9)]),
            _r("b.php", 5, functions=[_fn("fb", 1, 5)]),
        ),
        top=1,
        details=0,
    )

    out = "\n".join(_out(capsys))
    assert "fa  (fixture/a.php:1)" in out
    assert "fb" not in out


def test_details_only_under_rows_kept_by_min_level(target, capsys):
    _reporter(target, thresholds=(4, 6, 10)).report(
        _parsed(
            _r("a.php", 9, functions=[_fn("fa", 1, 9)]),
            _r("b.php", 1, functions=[_fn("fb", 1, 1)]),
            _r("c.php", 2, functions=None),
        ),
        min_level="warn",
        details=0,
    )

    out = "\n".join(_out(capsys))
    assert "fa  (fixture/a.php:1)" in out
    assert "fb" not in out
    assert "unavailable" not in out


def test_details_never_under_parse_rows(target, capsys):
    _reporter(target).report(
        _parsed(_r("a.php", 1, functions=[]), parse_errors={"p.php": "m"}), details=0
    )

    out = _out(capsys)
    assert out[2].endswith("fixture/a.php")
    assert out[3].startswith("⛔ PARSE")
    assert out[4] == ""


def test_details_null_functions_prints_the_unavailable_note(target, capsys):
    _reporter(target).report(_parsed(_r("a.php", 1, functions=None)), details=5)

    out = _out(capsys)
    assert out[3] == UNAVAILABLE
    assert out[4] == ""


def test_details_empty_functions_prints_nothing(target, capsys):
    _reporter(target).report(_parsed(_r("a.php", 1, functions=[])), details=5)

    out = _out(capsys)
    assert out[2].endswith("fixture/a.php")
    assert out[3] == ""


def test_details_unavailable_row_keeps_its_level(target, capsys):
    _reporter(target, thresholds=(4, 6, 10)).report(
        _parsed(_r("a.php", 7, functions=None)), details=0
    )

    out = _out(capsys)
    assert out[2].startswith(f"{'🔴 ERROR':<16}")
    assert out[3] == UNAVAILABLE


def test_details_large_npath_is_printed_in_full(target, capsys):
    npath = 2**53 + 1

    _reporter(target).report(
        _parsed(_r("a.php", 9, functions=[_fn("big", 4, 9, npath), _fn("mid", 8, 1, 12345678)])),
        details=0,
    )

    out = _out(capsys)
    assert out[3] == f"{'':<16} ccn   9  npath {npath}  big  (fixture/a.php:4)"
    assert out[4] == f"{'':<16} ccn   1  npath 12345678  mid  (fixture/a.php:8)"


def test_details_large_ccn_is_printed_in_full(target, capsys):
    _reporter(target).report(
        _parsed(_r("a.php", 1234, functions=[_fn("huge", 1, 1234)])), details=0
    )

    assert _out(capsys)[3] == f"{'':<16} ccn 1234  npath       1  huge  (fixture/a.php:1)"


def test_details_single_file_uses_the_file_name(tmp_path, capsys):
    file = tmp_path / "one.php"
    file.write_text("<?php\n")

    _reporter(file, root=tmp_path).report(
        _parsed(_r("one.php", 2, functions=[_fn("f", 3, 2)])), details=0
    )

    assert _out(capsys)[3] == _unit("f", "one.php", 3, 2)


def test_details_lines_are_dim_on_a_tty(target, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    palette = Palette(FakeTTY())

    _reporter(target, palette=palette).report(
        _parsed(_r("a.php", 2, functions=[_fn("f", 3, 2)]), _r("b.php", 1, functions=None)),
        details=0,
    )

    out = capsys.readouterr().out
    assert f"{Colors.DIM}{_unit('f', 'fixture/a.php', 3, 2)}{Colors.RESET}" in out
    assert f"{Colors.DIM}{UNAVAILABLE}{Colors.RESET}" in out


def test_details_do_not_change_the_summary(target, capsys):
    parsed = parse(dumps(DETAILED), LINES)
    _reporter(target, thresholds=(4, 6, 10)).report(parsed, details=0)
    with_details = _out(capsys)[-3:]

    _reporter(target, thresholds=(4, 6, 10)).report(parsed)

    assert _out(capsys)[-3:] == with_details
