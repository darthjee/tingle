"""Unit tests for code_check.rubycritic.reporter.Reporter."""

from __future__ import annotations

import io

import pytest

from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.palette import Colors, Palette
from code_check.rubycritic.output_parser import FileResult, MethodResult, ParsedOutput
from code_check.rubycritic.reporter import Reporter

# The header f-string from spec §6 (as in file_size's reporter).
HEADER = (
    f"{'Status':<16} {'Complexity':>10}  {'Rating':<6}  {'Smells':>6}  {'Duplication':>11}  File"
)
SEPARATOR = f"{'─' * 16} {'─' * 10}  {'─' * 6}  {'─' * 6}  {'─' * 11}  {'─' * 50}"


class FakeTTY(io.StringIO):
    """In-memory stream that reports itself as a TTY."""

    def isatty(self) -> bool:
        return True


@pytest.fixture
def target(tmp_path):
    path = tmp_path / "fixture"
    path.mkdir()
    return path


def _reporter(target, root=None, palette=None):
    analyzer = FileAnalyzer(10, 50, 100)
    root = target if root is None else root
    return Reporter(analyzer, target, root, palette or Palette(io.StringIO()))


def _parsed(results=None, parse_errors=None, score=83.23):
    return ParsedOutput(results or {}, parse_errors or {}, score)


def _out(capsys):
    return capsys.readouterr().out.splitlines()


# --- table -------------------------------------------------------------------------


def test_report_layout_and_order(target, capsys):
    parsed = _parsed(
        {
            "simple.rb": FileResult(0.0, "A", 1, 0),
            "dup_b.rb": FileResult(15.11, "C", 11, 39),
            "complex.rb": FileResult(72.25, "B", 14, 0),
            "dup_a.rb": FileResult(15.11, "C", 11, 39),
            "big.rb": FileResult(400.5, "F", 3, 12.6),
        },
        {"broken.rb": "unexpected token", "aaa.rb": "bad"},
    )

    _reporter(target).report(parsed)

    assert _out(capsys) == [
        HEADER,
        SEPARATOR,
        "🟣 CRITICAL           400.50  F            3           13  fixture/big.rb",
        "🔴 ERROR               72.25  B           14            0  fixture/complex.rb",
        # `⚠️` is two code points (U+26A0 U+FE0F), so `:<16` pads one space less,
        # exactly as in file_size's reporter.
        "⚠️  WARN              15.11  C           11           39  fixture/dup_a.rb",
        "⚠️  WARN              15.11  C           11           39  fixture/dup_b.rb",
        "✅ OK                   0.00  A            1            0  fixture/simple.rb",
        "⛔ PARSE                   -  -            -            -  fixture/aaa.rb",
        "⛔ PARSE                   -  -            -            -  fixture/broken.rb",
        "",
        "─" * 78,
        "Summary: 7 file(s) | 1 OK | 2 WARN | 1 ERROR | 1 CRITICAL | 2 skipped (parse error)",
        "Score: 83.23/100 (RubyCritic)",
    ]


def test_display_path_nested(target):
    assert _reporter(target).display_path("lib/a.rb") == "fixture/lib/a.rb"


def test_display_path_single_file(target):
    file_path = target / "a.rb"
    file_path.write_text("x\n")

    assert _reporter(file_path, root=target).display_path("a.rb") == "a.rb"


def test_level_boundaries(target, capsys):
    parsed = _parsed(
        {
            "a.rb": FileResult(9.99, "A", 0, 0),
            "b.rb": FileResult(10.0, "A", 0, 0),
            "c.rb": FileResult(50.0, "A", 0, 0),
            "d.rb": FileResult(100.0, "A", 0, 0),
        }
    )

    _reporter(target).report(parsed)

    labels = [line.split()[1] for line in _out(capsys)[2:6]]
    assert labels == ["CRITICAL", "ERROR", "WARN", "OK"]


# --- filters -----------------------------------------------------------------------


def _many():
    return {
        "a.rb": FileResult(120.0, "F", 0, 0),
        "b.rb": FileResult(60.0, "D", 0, 0),
        "c.rb": FileResult(20.0, "C", 0, 0),
        "d.rb": FileResult(1.0, "A", 0, 0),
    }


def test_min_level_then_top(target, capsys):
    _reporter(target).report(_parsed(_many(), {"z.rb": "bad"}), min_level="warn", top=2)

    out = _out(capsys)
    rows = [line for line in out if line.endswith(".rb")]
    assert [r.rsplit("/", 1)[1] for r in rows] == ["a.rb", "b.rb", "z.rb"]
    # The summary still counts every file.
    assert "Summary: 5 file(s) | 1 OK | 1 WARN | 1 ERROR | 1 CRITICAL | 1 skipped" in out[-2]


def test_top_does_not_count_parse_rows(target, capsys):
    _reporter(target).report(_parsed(_many(), {"y.rb": "bad", "z.rb": "bad"}), top=1)

    rows = [line for line in _out(capsys) if line.endswith(".rb")]
    assert len(rows) == 3
    assert rows[0].endswith("fixture/a.rb")


def test_no_rows_left_prints_note(target, capsys):
    _reporter(target).report(_parsed({"d.rb": FileResult(1.0, "A", 0, 0)}), min_level="error")

    out = _out(capsys)
    assert out[0] == "No files at or above ERROR."
    assert HEADER not in out


def test_parse_rows_keep_the_table_when_no_level_row_is_left(target, capsys):
    _reporter(target).report(
        _parsed({"d.rb": FileResult(1.0, "A", 0, 0)}, {"z.rb": "bad"}), min_level="error"
    )

    out = _out(capsys)
    assert out[0] == HEADER
    assert out[2].startswith("⛔ PARSE")


# --- method details ----------------------------------------------------------------


def _detail(score, name, location):
    return f"{'':<16} {score:>10.2f}  {name}  ({location})"


def _with_methods(parse_errors=None):
    parsed = _parsed(
        {
            "a.rb": FileResult(120.0, "F", 0, 0),
            "b.rb": FileResult(20.0, "C", 0, 0),
            "c.rb": FileResult(1.0, "A", 0, 0),
        },
        parse_errors,
    )
    parsed.methods = {
        "a.rb": [
            MethodResult("A#big", 3, 80.5),
            MethodResult("A#mid", 10, 30.0),
            MethodResult("A#small", 20, 9.5),
        ],
        "b.rb": [MethodResult("B#run", 7, 20.0)],
    }
    return parsed


def _rows(capsys):
    return _out(capsys)[2:-4]


def test_no_details_by_default(target, capsys):
    _reporter(target).report(_with_methods())

    assert len(_rows(capsys)) == 3


def test_details_limit(target, capsys):
    _reporter(target).report(_with_methods(), details=2)

    assert _rows(capsys) == [
        "🟣 CRITICAL           120.00  F            0            0  fixture/a.rb",
        _detail(80.5, "A#big", "fixture/a.rb:3"),
        _detail(30.0, "A#mid", "fixture/a.rb:10"),
        "⚠️  WARN              20.00  C            0            0  fixture/b.rb",
        _detail(20.0, "B#run", "fixture/b.rb:7"),
        "✅ OK                   1.00  A            0            0  fixture/c.rb",
    ]


def test_details_zero_shows_all(target, capsys):
    _reporter(target).report(_with_methods(), details=0)

    rows = _rows(capsys)
    assert rows[1:4] == [
        _detail(80.5, "A#big", "fixture/a.rb:3"),
        _detail(30.0, "A#mid", "fixture/a.rb:10"),
        _detail(9.5, "A#small", "fixture/a.rb:20"),
    ]
    assert len(rows) == 7


def test_details_score_aligns_under_complexity(target, capsys):
    _reporter(target).report(_with_methods(), details=1)

    rows = _rows(capsys)
    assert rows[1] == "                      80.50  A#big  (fixture/a.rb:3)"
    assert HEADER.index("Complexity") + len("Complexity") == rows[1].index("80.50") + len("80.50")


def test_details_skip_hidden_rows_and_parse_rows(target, capsys):
    parsed = _with_methods({"z.rb": "bad"})
    parsed.methods["z.rb"] = [MethodResult("Z#x", 1, 5.0)]

    _reporter(target).report(parsed, top=1, details=0)

    rows = _rows(capsys)
    assert len(rows) == 5
    assert rows[-1].startswith("⛔ PARSE")
    assert "B#run" not in "\n".join(rows)
    assert "Z#x" not in "\n".join(rows)


def test_details_without_methods_data(target, capsys):
    parsed = _with_methods()
    parsed.methods = None

    _reporter(target).report(parsed, details=5)

    assert len(_rows(capsys)) == 3


def test_details_dim_on_a_tty(target, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    _reporter(target, palette=Palette(FakeTTY())).report(_with_methods(), details=1)

    out = capsys.readouterr().out
    assert f"{Colors.DIM}{_detail(80.5, 'A#big', 'fixture/a.rb:3')}{Colors.RESET}\n" in out


def test_details_colourless_without_a_tty(target, capsys):
    _reporter(target).report(_with_methods(), details=1)

    assert "\033[" not in capsys.readouterr().out


# --- summary -----------------------------------------------------------------------


def test_summary_without_skipped(target, capsys):
    _reporter(target).report(_parsed({"d.rb": FileResult(1.0, "A", 0, 0)}))

    out = _out(capsys)
    assert out[-2] == "Summary: 1 file(s) | 1 OK | 0 WARN | 0 ERROR | 0 CRITICAL"
    assert not any(line.startswith("Total:") for line in out)


def test_summary_null_score(target, capsys):
    _reporter(target).report(_parsed({}, {"a.rb": "bad"}, score=None))

    out = _out(capsys)
    assert out[-2] == (
        "Summary: 1 file(s) | 0 OK | 0 WARN | 0 ERROR | 0 CRITICAL | 1 skipped (parse error)"
    )
    assert out[-1] == "Score: n/a (RubyCritic)"


def test_score_has_two_decimals(target, capsys):
    _reporter(target).report(_parsed({"d.rb": FileResult(1.0, "A", 0, 0)}, score=80))

    assert _out(capsys)[-1] == "Score: 80.00/100 (RubyCritic)"


# --- colours -----------------------------------------------------------------------


def test_colours_on_a_tty(target, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    palette = Palette(FakeTTY())

    _reporter(target, palette=palette).report(
        _parsed({"a.rb": FileResult(72.0, "B", 0, 0)}, {"z.rb": "bad"})
    )

    out = capsys.readouterr().out
    assert f"{Colors.RED}{Colors.BOLD}🔴 ERROR" in out
    assert f"{Colors.GRAY}⛔ PARSE" in out
    assert f" {Colors.GRAY}| 1 skipped (parse error){Colors.RESET}" in out
    assert f"{Colors.BOLD}Score:{Colors.RESET} 83.23/100 (RubyCritic)" in out


def test_no_colours_with_no_color(target, capsys, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    palette = Palette(FakeTTY())

    _reporter(target, palette=palette).report(
        _parsed({"a.rb": FileResult(72.0, "B", 0, 0)}, {"z.rb": "bad"})
    )

    assert "\033[" not in capsys.readouterr().out


def test_palette_defaults_to_stdout(target, capsys):
    reporter = Reporter(FileAnalyzer(10, 50, 100), target, target)

    reporter.report(_parsed({"a.rb": FileResult(1.0, "A", 0, 0)}))

    assert "fixture/a.rb" in capsys.readouterr().out
