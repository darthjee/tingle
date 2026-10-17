"""Unit tests for code_check.php_complexity.output_parser."""

from __future__ import annotations

import copy

import pytest

from code_check.php_complexity.output_parser import (
    FileResult,
    OutputFormatError,
    ParsedOutput,
    parse,
)
from tests.code_check.php_complexity.sample_output import (
    FILLED,
    LINES,
    SAMPLE,
    dumps,
    entry,
    output,
    sample,
)

PDEPEND = {"ccn": 2, "max_ccn": 2, "max_npath": 2, "min_mi": 79.5, "lloc": 2}


def _reason(stdout, lines=LINES):
    with pytest.raises(OutputFormatError) as exc_info:
        parse(stdout, lines)
    return exc_info.value.reason


def _with_file(index, **changes):
    data = copy.deepcopy(SAMPLE)
    data["files"][index].update(changes)
    return dumps(data)


def _pdepend(**changes):
    data = dict(PDEPEND)
    data.update(changes)
    return data


# --- the sample --------------------------------------------------------------------


def test_sample_is_parsed():
    parsed = parse(dumps(), LINES)

    assert parsed.parse_errors == {
        "attr_anon.php": "Unexpected token: #[, line: 14, col: 20",
        "broken.php": 'syntax error, unexpected token ":", expecting variable on line 10',
        "lenient.php": 'syntax error, unexpected token ";" on line 5',
    }
    assert parsed.refused == []
    assert parsed.pdepend_messages == []
    assert parsed.tool_versions == {"php": "8.5.11", "pdepend": "3.0.0", "jscpd": None}
    assert parsed.warnings == SAMPLE["warnings"]
    assert len(parsed.results) == 15
    assert parsed.results["Calculator.php"] == FileResult(
        "Calculator.php", 11, 7, 36, 53.875623305512, 22, True
    )
    assert parsed.results["bootstrap.php"] == FileResult("bootstrap.php", 0)


def test_results_keep_sent_line_order():
    parsed = parse(dumps(), LINES)

    assert list(parsed.results) == [line for line in LINES if line not in parsed.parse_errors]


def test_filled_functions_and_duplication_are_kept():
    parsed = parse(dumps(FILLED), LINES)

    assert parsed.tool_versions["jscpd"] == "5.4.1"
    assert parsed.results["Calculator.php"].functions[2]["name"] == "Calculator::grade"
    assert parsed.results["dup_a.php"].duplication == {"lines": 13}
    assert parsed.results["bootstrap.php"].functions == []
    assert parsed.results["bootstrap.php"].duplication == {"lines": 0}


def test_empty_output():
    parsed = parse(dumps(output([])), [])

    assert parsed == ParsedOutput(
        tool_versions=SAMPLE["tool_versions"], warnings=[]
    )


# --- score -------------------------------------------------------------------------


def test_score_is_the_total_ccn():
    parsed = parse(dumps(output([entry("a.php", 42)])), ["a.php"])

    assert parsed.results["a.php"].score == 42


def test_null_pdepend_scores_zero():
    result = parse(dumps(output([entry("a.php")])), ["a.php"]).results["a.php"]

    assert result == FileResult("a.php", 0, None, None, None, None, False, None, None)


def test_pdepend_with_null_maxima():
    data = output([entry("a.php", 0, max_ccn=None, max_npath=None, min_mi=None, lloc=3)])

    result = parse(dumps(data), ["a.php"]).results["a.php"]

    assert result == FileResult("a.php", 0, None, None, None, 3, True)


def test_npath_above_two_to_the_53_stays_exact():
    big = 2**53 + 1
    data = output([entry("a.php", 5, max_npath=big)])

    assert parse(dumps(data), ["a.php"]).results["a.php"].max_npath == big


def test_integer_min_mi_is_accepted():
    data = output([entry("a.php", 1, min_mi=80)])

    assert parse(dumps(data), ["a.php"]).results["a.php"].min_mi == 80


# --- parse errors, refused lines and path-less messages ----------------------------


def test_parse_error_message_falls_back_to_unknown_error():
    data = output([entry("a.php", parse_error=True)])

    assert parse(dumps(data), ["a.php"]).parse_errors == {"a.php": "unknown error"}


@pytest.mark.parametrize("tool", ["php", "pdepend"])
def test_parse_error_message_from_tool_warning(tool):
    data = output(
        [entry("a.php", parse_error=True)],
        [
            {"tool": "entrypoint", "path": "a.php", "message": "ignored"},
            {"tool": "jscpd", "path": "a.php", "message": "ignored"},
            {"tool": tool, "path": "a.php", "message": "boom"},
        ],
    )

    assert parse(dumps(data), ["a.php"]).parse_errors == {"a.php": "boom"}


def test_parse_error_takes_first_matching_warning():
    data = output(
        [entry("a.php", parse_error=True)],
        [
            {"tool": "php", "path": "a.php", "message": "first"},
            {"tool": "pdepend", "path": "a.php", "message": "second"},
        ],
    )

    assert parse(dumps(data), ["a.php"]).parse_errors == {"a.php": "first"}


def test_refused_lines_in_warnings_order():
    data = output(
        [entry("a.php"), entry("b.php"), entry("c.php", 10)],
        [
            {"tool": "entrypoint", "path": "b.php", "message": "not a regular file under /src"},
            {"tool": "jscpd", "message": "jscpd failed"},
            {"tool": "entrypoint", "path": "a.php", "message": "duplicate line"},
            {"tool": "entrypoint", "path": "c.php", "message": "not refused: has data"},
            {"tool": "jscpd", "path": "a.php", "message": "secondary"},
        ],
    )

    assert parse(dumps(data), ["a.php", "b.php", "c.php"]).refused == [
        ("b.php", "not a regular file under /src"),
        ("a.php", "duplicate line"),
    ]


def test_file_without_data_and_without_warning_is_not_refused():
    assert parse(dumps(output([entry("empty.php")])), ["empty.php"]).refused == []


def test_pathless_pdepend_messages_in_warnings_order():
    data = output(
        [entry("a.php", 1)],
        [
            {"tool": "pdepend", "message": "first"},
            {"tool": "pdepend", "path": "a.php", "message": "per-file"},
            {"tool": "jscpd", "message": "not pdepend"},
            {"tool": "pdepend", "message": "second"},
        ],
    )

    assert parse(dumps(data), ["a.php"]).pdepend_messages == ["first", "second"]


# --- reasons -----------------------------------------------------------------------


def test_invalid_json():
    assert _reason("not json").startswith("invalid JSON: ")


@pytest.mark.parametrize("stdout", ["[]", "1", '"x"', "null"])
def test_not_an_object(stdout):
    assert _reason(stdout) == "expected a JSON object"


@pytest.mark.parametrize(
    "versions",
    [
        None,
        [],
        {},
        {"php": None, "pdepend": "3.0.0", "jscpd": None},
        {"php": 8, "pdepend": "3.0.0", "jscpd": None},
        {"php": "8.5.11", "pdepend": None, "jscpd": None},
        {"php": "8.5.11", "jscpd": None},
        {"php": "8.5.11", "pdepend": "3.0.0"},
        {"php": "8.5.11", "pdepend": "3.0.0", "jscpd": 5},
        {"php": "8.5.11", "pdepend": "3.0.0", "jscpd": False},
    ],
)
def test_unexpected_tool_versions(versions):
    assert _reason(dumps(sample(tool_versions=versions))) == "unexpected tool_versions"


def test_missing_tool_versions():
    data = sample()
    del data["tool_versions"]

    assert _reason(dumps(data)) == "unexpected tool_versions"


@pytest.mark.parametrize("files", [None, {}, "x"])
def test_files_not_a_list(files):
    assert _reason(dumps(sample(files=files))) == "files do not match the sent lines"


def test_files_too_short():
    assert _reason(dumps(), LINES + ["extra.php"]) == "files do not match the sent lines"


def test_files_too_long():
    assert _reason(dumps(), LINES[:-1]) == "files do not match the sent lines"


def test_files_path_mismatch():
    lines = list(LINES)
    lines[1], lines[0] = lines[0], lines[1]

    assert _reason(dumps(), lines) == "unexpected files entry: 0"


@pytest.mark.parametrize(
    ("index", "changes"),
    [
        (0, {"path": 3}),
        (0, {"parse_error": None}),
        (0, {"parse_error": 0}),
        (0, {"pdepend": []}),
        (0, {"pdepend": _pdepend(ccn=True)}),
        (0, {"pdepend": _pdepend(ccn="2")}),
        (0, {"pdepend": _pdepend(ccn=2.0)}),
        (0, {"pdepend": _pdepend(ccn=-1)}),
        (0, {"pdepend": _pdepend(max_ccn=0)}),
        (0, {"pdepend": _pdepend(max_ccn=True)}),
        (0, {"pdepend": _pdepend(max_npath=0)}),
        (0, {"pdepend": _pdepend(max_npath=1.5)}),
        (0, {"pdepend": _pdepend(min_mi="80")}),
        (0, {"pdepend": _pdepend(min_mi=True)}),
        (0, {"pdepend": _pdepend(lloc=None)}),
        (0, {"pdepend": _pdepend(lloc=-1)}),
        (0, {"pdepend": _pdepend(lloc=False)}),
        (0, {"pdepend": {k: v for k, v in PDEPEND.items() if k != "max_ccn"}}),
        (0, {"pdepend": {k: v for k, v in PDEPEND.items() if k != "max_npath"}}),
        (0, {"pdepend": {k: v for k, v in PDEPEND.items() if k != "min_mi"}}),
        (0, {"pdepend": {k: v for k, v in PDEPEND.items() if k != "lloc"}}),
        (0, {"duplication": 0}),
        (0, {"duplication": {}}),
        (0, {"duplication": {"lines": -1}}),
        (0, {"duplication": {"lines": True}}),
        (0, {"duplication": {"lines": 1.5}}),
        (0, {"functions": {}}),
        (0, {"functions": [1]}),
        (0, {"functions": [{"name": 1, "line": 1, "ccn": 1, "npath": 1}]}),
        (0, {"functions": [{"name": "f", "line": 0, "ccn": 1, "npath": 1}]}),
        (0, {"functions": [{"name": "f", "line": 1, "ccn": True, "npath": 1}]}),
        (0, {"functions": [{"name": "f", "line": 1, "ccn": 1, "npath": 0}]}),
        (0, {"functions": [{"name": "f", "line": 1, "ccn": 1}]}),
        (6, {"pdepend": PDEPEND}),
        (6, {"duplication": {"lines": 0}}),
        (6, {"functions": []}),
    ],
)
def test_unexpected_files_entry(index, changes):
    assert _reason(_with_file(index, **changes)) == f"unexpected files entry: {index}"


def test_files_entry_not_an_object():
    data = sample()
    data["files"][3] = "Modern.php"

    assert _reason(dumps(data)) == "unexpected files entry: 3"


def test_missing_parse_error_key():
    data = sample()
    del data["files"][4]["parse_error"]

    assert _reason(dumps(data)) == "unexpected files entry: 4"


def test_first_bad_entry_is_reported():
    data = sample()
    data["files"][4]["pdepend"] = 1
    data["files"][1]["pdepend"] = 1

    assert _reason(dumps(data)) == "unexpected files entry: 1"


def test_functions_with_big_npath_are_accepted():
    big = 2**60
    data = output(
        [entry("a.php", 3, functions=[{"name": "f", "line": 1, "ccn": 3, "npath": big}])]
    )

    assert parse(dumps(data), ["a.php"]).results["a.php"].functions[0]["npath"] == big


@pytest.mark.parametrize(
    "warnings",
    [
        None,
        {},
        ["x"],
        [{"tool": "fta", "message": "m"}],
        [{"tool": "phpmd", "message": "m"}],
        [{"tool": "php"}],
        [{"tool": "php", "message": 1}],
        [{"tool": "pdepend", "message": "m", "path": None}],
        [{"message": "m"}],
    ],
)
def test_unexpected_warnings(warnings):
    assert _reason(dumps(sample(warnings=warnings))) == "unexpected warnings"


def test_missing_warnings():
    data = sample()
    del data["warnings"]

    assert _reason(dumps(data)) == "unexpected warnings"


def test_checks_run_in_spec_order():
    data = sample(tool_versions=None, files=None, warnings=None)

    assert _reason(dumps(data)) == "unexpected tool_versions"
    data["tool_versions"] = SAMPLE["tool_versions"]
    assert _reason(dumps(data)) == "files do not match the sent lines"
    data["files"] = SAMPLE["files"]
    assert _reason(dumps(data)) == "unexpected warnings"


# --- tolerance ---------------------------------------------------------------------


def test_extra_keys_are_ignored():
    data = copy.deepcopy(SAMPLE)
    data["extra"] = 1
    data["tool_versions"]["other"] = "1"
    data["files"][2]["extra"] = True
    data["files"][2]["pdepend"]["ccn2"] = 14
    data["warnings"][0]["extra"] = 2

    assert parse(dumps(data), LINES).results["Calculator.php"].score == 11


def test_whole_run_warning_without_path_is_accepted():
    data = output([entry("a.php", 1)], [{"tool": "jscpd", "message": "failed"}])

    parsed = parse(dumps(data), ["a.php"])

    assert parsed.warnings == [{"tool": "jscpd", "message": "failed"}]
    assert parsed.refused == []
    assert parsed.pdepend_messages == []
