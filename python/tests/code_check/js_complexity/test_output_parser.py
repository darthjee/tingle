"""Unit tests for code_check.js_complexity.output_parser."""

from __future__ import annotations

import copy

import pytest

from code_check.js_complexity.output_parser import (
    FileResult,
    OutputFormatError,
    ParsedOutput,
    parse,
)
from tests.code_check.js_complexity.sample_output import (
    FILLED,
    LINES,
    SAMPLE,
    SFC,
    SFC_COFFEE_MESSAGE,
    SFC_LINES,
    dumps,
    entry,
    output,
    sample,
)


def _reason(stdout, lines=LINES):
    with pytest.raises(OutputFormatError) as exc_info:
        parse(stdout, lines)
    return exc_info.value.reason


def _with_file(index, **changes):
    data = copy.deepcopy(SAMPLE)
    data["files"][index].update(changes)
    return dumps(data)


# --- the sample --------------------------------------------------------------------


def test_sample_is_parsed():
    parsed = parse(dumps(), LINES)

    assert parsed == ParsedOutput(
        results={
            "complex.ts": FileResult("complex.ts", 71.3, 136, 245, "Needs improvement"),
            "simple.js": FileResult("simple.js", 7.7, 1, 6, "OK"),
            "empty.js": FileResult("empty.js", 0.0),
            "../outside.js": FileResult("../outside.js", 0.0),
        },
        parse_errors={
            "broken.js": 'Error { error: (36..37, Expected(",", "numeric literal (1, 1)")) }',
            "latin1.js": "file is not valid UTF-8",
        },
        refused=[("../outside.js", "path has a '..' segment")],
        tool_versions={"fta": "3.1.0", "jscpd": None, "escomplex": None},
        warnings=SAMPLE["warnings"],
    )


def test_results_keep_sent_line_order():
    assert list(parse(dumps(), LINES).results) == [
        "complex.ts", "simple.js", "empty.js", "../outside.js",
    ]


def test_filled_duplication_and_functions_are_kept():
    parsed = parse(dumps(FILLED), LINES)

    assert parsed.tool_versions == {"fta": "3.1.0", "jscpd": "5.4.1", "escomplex": "0.1.0"}
    assert parsed.results["complex.ts"].duplication == {"lines": 0}
    assert parsed.results["complex.ts"].functions[0]["name"] == "reducer"
    assert parsed.results["simple.js"].functions == []
    assert parsed.results["empty.js"].duplication == {"lines": 0}


def test_empty_output():
    parsed = parse(dumps(output([])), [])

    assert parsed.results == {}
    assert parsed.parse_errors == {}
    assert parsed.refused == []


# --- score -------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(59.96, 60.0), (59.94, 59.9), (7.25, 7.2), (100, 100.0), (0, 0.0), (180.04, 180.0)],
)
def test_score_is_rounded_to_one_decimal(raw, expected):
    parsed = parse(dumps(output([entry("a.js", raw)])), ["a.js"])

    assert parsed.results["a.js"].score == expected


def test_null_fta_scores_zero():
    result = parse(dumps(output([entry("a.js")])), ["a.js"]).results["a.js"]

    assert result == FileResult("a.js", 0.0, None, None, None, None, None)


# --- parse errors and refused lines ------------------------------------------------


def test_parse_error_message_falls_back_to_unknown_error():
    data = output([entry("a.js", parse_error=True)])

    assert parse(dumps(data), ["a.js"]).parse_errors == {"a.js": "unknown error"}


def test_parse_error_message_from_entrypoint_warning():
    data = output(
        [entry("a.vue", parse_error=True)],
        [
            {"tool": "jscpd", "path": "a.vue", "message": "ignored"},
            {"tool": "entrypoint", "path": "a.vue", "message": "cannot extract script"},
        ],
    )

    assert parse(dumps(data), ["a.vue"]).parse_errors == {"a.vue": "cannot extract script"}


def test_parse_error_takes_first_matching_warning():
    data = output(
        [entry("a.js", parse_error=True)],
        [
            {"tool": "fta", "path": "a.js", "message": "first"},
            {"tool": "fta", "path": "a.js", "message": "second"},
        ],
    )

    assert parse(dumps(data), ["a.js"]).parse_errors == {"a.js": "first"}


def test_refused_lines_in_warnings_order():
    data = output(
        [entry("a.js"), entry("b.js"), entry("c.js", 10)],
        [
            {"tool": "entrypoint", "path": "b.js", "message": "not a regular file under /src"},
            {"tool": "jscpd", "message": "jscpd failed"},
            {"tool": "entrypoint", "path": "a.js", "message": "duplicate line"},
            {"tool": "entrypoint", "path": "c.js", "message": "not refused: has data"},
            {"tool": "jscpd", "path": "a.js", "message": "secondary"},
        ],
    )

    assert parse(dumps(data), ["a.js", "b.js", "c.js"]).refused == [
        ("b.js", "not a regular file under /src"),
        ("a.js", "duplicate line"),
    ]


def test_dropped_file_without_warning_is_not_refused():
    assert parse(dumps(output([entry("empty.js")])), ["empty.js"]).refused == []


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
        {"fta": None, "jscpd": None, "escomplex": None},
        {"fta": 3, "jscpd": None, "escomplex": None},
        {"fta": "3.1.0", "escomplex": None},
        {"fta": "3.1.0", "jscpd": None},
        {"fta": "3.1.0", "jscpd": 5, "escomplex": None},
        {"fta": "3.1.0", "jscpd": None, "escomplex": False},
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
    assert _reason(dumps(), LINES + ["extra.js"]) == "files do not match the sent lines"


def test_files_too_long():
    assert _reason(dumps(), LINES[:-1]) == "files do not match the sent lines"


def test_files_path_mismatch():
    lines = list(LINES)
    lines[1], lines[0] = lines[0], lines[1]

    assert _reason(dumps(), lines) == "unexpected files entry: 0"


@pytest.mark.parametrize(
    ("index", "changes"),
    [
        (1, {"path": 3}),
        (1, {"parse_error": None}),
        (1, {"parse_error": 0}),
        (1, {"fta": []}),
        (1, {"fta": {"score": True, "cyclo": 1, "lines": 6, "assessment": "OK"}}),
        (1, {"fta": {"score": "7", "cyclo": 1, "lines": 6, "assessment": "OK"}}),
        (1, {"fta": {"score": 7, "cyclo": True, "lines": 6, "assessment": "OK"}}),
        (1, {"fta": {"score": 7, "cyclo": 1.0, "lines": 6, "assessment": "OK"}}),
        (1, {"fta": {"score": 7, "cyclo": -1, "lines": 6, "assessment": "OK"}}),
        (1, {"fta": {"score": 7, "cyclo": 1, "lines": False, "assessment": "OK"}}),
        (1, {"fta": {"score": 7, "cyclo": 1, "lines": -1, "assessment": "OK"}}),
        (1, {"fta": {"score": 7, "cyclo": 1, "lines": 6, "assessment": None}}),
        (1, {"fta": {"score": 7, "cyclo": 1, "lines": 6}}),
        (1, {"duplication": 0}),
        (1, {"duplication": {}}),
        (1, {"duplication": {"lines": -1}}),
        (1, {"duplication": {"lines": True}}),
        (1, {"duplication": {"lines": 1.5}}),
        (1, {"functions": {}}),
        (1, {"functions": [1]}),
        (1, {"functions": [{"name": 1, "line": 1, "cyclo": 1, "sloc": 1}]}),
        (1, {"functions": [{"name": "f", "line": 0, "cyclo": 1, "sloc": 1}]}),
        (1, {"functions": [{"name": "f", "line": 1, "cyclo": True, "sloc": 1}]}),
        (1, {"functions": [{"name": "f", "line": 1, "cyclo": 1}]}),
        (2, {"fta": {"score": 7, "cyclo": 1, "lines": 6, "assessment": "OK"}}),
        (2, {"duplication": {"lines": 0}}),
        (2, {"functions": []}),
    ],
)
def test_unexpected_files_entry(index, changes):
    assert _reason(_with_file(index, **changes)) == f"unexpected files entry: {index}"


def test_files_entry_not_an_object():
    data = sample()
    data["files"][3] = "latin1.js"

    assert _reason(dumps(data)) == "unexpected files entry: 3"


def test_missing_parse_error_key():
    data = sample()
    del data["files"][4]["parse_error"]

    assert _reason(dumps(data)) == "unexpected files entry: 4"


def test_first_bad_entry_is_reported():
    data = sample()
    data["files"][4]["fta"] = 1
    data["files"][1]["fta"] = 1

    assert _reason(dumps(data)) == "unexpected files entry: 1"


@pytest.mark.parametrize(
    "warnings",
    [
        None,
        {},
        ["x"],
        [{"tool": "eslint", "message": "m"}],
        [{"tool": "fta"}],
        [{"tool": "fta", "message": 1}],
        [{"tool": "fta", "message": "m", "path": None}],
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
    data["files"][0]["extra"] = True
    data["files"][0]["fta"]["halstead"] = {}
    data["warnings"][0]["extra"] = 2

    assert parse(dumps(data), LINES).results["complex.ts"].score == 71.3


def test_integer_score_is_accepted():
    data = output([entry("a.js", 50)])

    assert parse(dumps(data), ["a.js"]).results["a.js"].score == 50.0


def test_whole_run_warning_without_path_is_accepted():
    data = output([entry("a.js", 1)], [{"tool": "escomplex", "message": "failed"}])

    parsed = parse(dumps(data), ["a.js"])

    assert parsed.warnings == [{"tool": "escomplex", "message": "failed"}]
    assert parsed.refused == []


# --- single-file components (#326) -------------------------------------------------


def test_sfc_row_keeps_the_original_path_and_lines():
    result = parse(dumps(SFC), SFC_LINES).results["src/Cart.vue"]

    assert result == FileResult(
        "src/Cart.vue", 30.7, 3, 11, "OK", {"lines": 0}, SFC["files"][0]["functions"]
    )
    assert [f["line"] for f in result.functions] == [13, 17]


def test_sfc_without_script_scores_zero():
    result = parse(dumps(SFC), SFC_LINES).results["src/NoScript.vue"]

    assert result == FileResult("src/NoScript.vue", 0.0, None, None, None, {"lines": 0}, [])


def test_sfc_extraction_error_is_a_parse_error_not_a_refused_line():
    parsed = parse(dumps(SFC), SFC_LINES)

    assert parsed.parse_errors == {"src/Coffee.vue": SFC_COFFEE_MESSAGE}
    assert "src/Coffee.vue" not in parsed.results
    assert parsed.refused == []
