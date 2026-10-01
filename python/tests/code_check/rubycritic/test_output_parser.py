"""Unit tests for code_check.rubycritic.output_parser."""

from __future__ import annotations

import copy

import pytest

from code_check.rubycritic.output_parser import (
    MISSING_RESULT,
    FileResult,
    MethodResult,
    OutputFormatError,
    count_smells,
    normalize_path,
    parse,
)
from tests.code_check.rubycritic.sample_output import SAMPLE, SENT, dumps, sample


def _module(path, complexity=1.0, **extra):
    entry = {"path": path, "complexity": complexity, "rating": "A", "smells": [],
             "duplication": 0}
    entry.update(extra)
    return entry


def _reason(stdout, sent=SENT):
    with pytest.raises(OutputFormatError) as exc_info:
        parse(stdout, sent)
    return exc_info.value.reason


# --- the sample --------------------------------------------------------------------


def test_parse_sample():
    parsed = parse(dumps(), SENT)

    assert parsed.results == {
        "complex.rb": FileResult(72.25, "B", 2, 0),
        "dup_a.rb": FileResult(15.11, "C", 1, 39),
        "empty.rb": FileResult(0.0, "A", 0, 0),
    }
    assert parsed.parse_errors == {"broken.rb": "unexpected token tSTRING"}
    assert parsed.score == 83.23


def test_results_follow_sent_order():
    assert list(parse(dumps(), SENT).results) == ["complex.rb", "dup_a.rb", "empty.rb"]


# --- structural checks -------------------------------------------------------------


def test_invalid_json():
    assert _reason("not json").startswith("invalid JSON: ")


def test_empty_stdout_is_invalid_json():
    assert _reason("").startswith("invalid JSON: ")


@pytest.mark.parametrize("stdout", ["[]", "1", '"x"', "null"])
def test_not_an_object(stdout):
    assert _reason(stdout) == "expected a JSON object"


@pytest.mark.parametrize("value", [None, {}, "x"])
def test_analysed_modules_not_a_list(value):
    assert _reason(dumps(sample(analysed_modules=value))) == "unexpected analysed_modules"


def test_analysed_modules_missing():
    data = sample()
    del data["analysed_modules"]

    assert _reason(dumps(data)) == "unexpected analysed_modules"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("complexity", "1"),
        ("complexity", True),
        ("complexity", None),
        ("rating", 1),
        ("smells", {}),
        ("duplication", False),
        ("duplication", "0"),
    ],
)
def test_bad_module_field_names_the_path(field, value):
    modules = [_module("a.rb"), _module("b.rb", **{field: value})]

    assert _reason(dumps(sample(analysed_modules=modules))) == (
        "unexpected analysed_modules entry: b.rb"
    )


@pytest.mark.parametrize("field", ["complexity", "rating", "smells", "duplication"])
def test_missing_module_field(field):
    entry = _module("a.rb")
    del entry[field]

    assert _reason(dumps(sample(analysed_modules=[entry]))) == (
        "unexpected analysed_modules entry: a.rb"
    )


@pytest.mark.parametrize("entry", [{"complexity": 1}, {"path": 3}, "a.rb", None])
def test_bad_module_without_path_names_the_index(entry):
    modules = [_module("a.rb"), entry]

    assert _reason(dumps(sample(analysed_modules=modules))) == (
        "unexpected analysed_modules entry: 1"
    )


@pytest.mark.parametrize("value", ["83", True, [], {}])
def test_bad_score(value):
    assert _reason(dumps(sample(score=value))) == "unexpected score"


def test_null_score():
    assert parse(dumps(sample(score=None)), SENT).score is None


def test_integer_score():
    assert parse(dumps(sample(score=80)), SENT).score == 80


@pytest.mark.parametrize(
    "value",
    [
        {},
        "x",
        ["broken.rb"],
        [{"path": "broken.rb"}],
        [{"message": "m"}],
        [{"path": 1, "message": "m"}],
        [{"path": "broken.rb", "message": None}],
    ],
)
def test_bad_parse_errors(value):
    assert _reason(dumps(sample(parse_errors=value))) == "unexpected parse_errors"


def test_missing_parse_errors_means_none():
    data = sample()
    del data["parse_errors"]

    parsed = parse(dumps(data), SENT)

    assert parsed.parse_errors == {}
    assert parsed.results["broken.rb"] == MISSING_RESULT


# --- path mapping ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("lib/a.rb", "lib/a.rb"),
        ("./lib/a.rb", "lib/a.rb"),
        ("/src/lib/a.rb", "lib/a.rb"),
        ("/src/./lib/a.rb", "lib/a.rb"),
        ("././a.rb", "a.rb"),
        ("/other/a.rb", "/other/a.rb"),
        ("src/a.rb", "src/a.rb"),
    ],
)
def test_normalize_path(raw, expected):
    assert normalize_path(raw) == expected


def test_prefixed_paths_are_matched():
    modules = [_module("./a.rb", 5.0), _module("/src/lib/b.rb", 6.0)]
    errors = [{"path": "/src/./c.rb", "message": "bad"}]

    parsed = parse(dumps(sample(analysed_modules=modules, parse_errors=errors)),
                   ["a.rb", "c.rb", "lib/b.rb"])

    assert parsed.results["a.rb"].complexity == 5.0
    assert parsed.results["lib/b.rb"].complexity == 6.0
    assert parsed.parse_errors == {"c.rb": "bad"}


def test_unknown_paths_are_ignored():
    modules = [_module("other.rb", 9.0), _module("a.rb", 1.0)]
    errors = [{"path": "nope.rb", "message": "bad"}]

    parsed = parse(dumps(sample(analysed_modules=modules, parse_errors=errors)), ["a.rb"])

    assert parsed.results == {"a.rb": FileResult(1.0, "A", 0, 0)}
    assert parsed.parse_errors == {}


def test_first_entry_wins_for_duplicates():
    modules = [_module("a.rb", 1.0), _module("./a.rb", 2.0)]
    errors = [{"path": "b.rb", "message": "first"}, {"path": "b.rb", "message": "second"}]

    parsed = parse(dumps(sample(analysed_modules=modules, parse_errors=errors)), ["a.rb", "b.rb"])

    assert parsed.results["a.rb"].complexity == 1.0
    assert parsed.parse_errors == {"b.rb": "first"}


def test_missing_files_are_ok_zero():
    parsed = parse(dumps(), [*SENT, "gone.rb"])

    assert parsed.results["gone.rb"] == FileResult(0.0, "-", 0, 0)


def test_parse_errors_win_over_modules():
    errors = [{"path": "complex.rb", "message": "bad"}]

    parsed = parse(dumps(sample(parse_errors=errors)), SENT)

    assert "complex.rb" not in parsed.results
    assert parsed.parse_errors == {"complex.rb": "bad"}


def test_integer_complexity_becomes_float():
    parsed = parse(dumps(sample(analysed_modules=[_module("a.rb", 3)])), ["a.rb"])

    assert parsed.results["a.rb"].complexity == 3.0
    assert isinstance(parsed.results["a.rb"].complexity, float)


# --- methods -----------------------------------------------------------------------


def _method(path, name="A#a", line=1, score=1.0):
    return {"path": path, "name": name, "line": line, "score": score}


def test_sample_methods():
    parsed = parse(dumps(), SENT)

    assert parsed.methods == {
        "complex.rb": [MethodResult("Complex#run", 2, 72.25)],
        "dup_a.rb": [MethodResult("DupA#a", 2, 15.11)],
    }


def test_absent_methods_key_is_none():
    data = sample()
    del data["methods"]

    assert parse(dumps(data), SENT).methods is None


def test_empty_methods_is_empty_dict():
    assert parse(dumps(sample(methods=[])), SENT).methods == {}


@pytest.mark.parametrize(
    "value",
    [
        None,
        {},
        "x",
        ["a.rb"],
        [{"name": "A#a", "line": 1, "score": 1.0}],
        [{"path": 1, "name": "A#a", "line": 1, "score": 1.0}],
        [{"path": "a.rb", "line": 1, "score": 1.0}],
        [{"path": "a.rb", "name": None, "line": 1, "score": 1.0}],
        [{"path": "a.rb", "name": "A#a", "score": 1.0}],
        [{"path": "a.rb", "name": "A#a", "line": "1", "score": 1.0}],
        [{"path": "a.rb", "name": "A#a", "line": 1.0, "score": 1.0}],
        [{"path": "a.rb", "name": "A#a", "line": True, "score": 1.0}],
        [{"path": "a.rb", "name": "A#a", "line": 1}],
        [{"path": "a.rb", "name": "A#a", "line": 1, "score": "1"}],
        [{"path": "a.rb", "name": "A#a", "line": 1, "score": False}],
    ],
)
def test_bad_methods(value):
    assert _reason(dumps(sample(methods=value))) == "unexpected methods"


def test_method_paths_are_normalised():
    methods = [_method("./a.rb", "A#x"), _method("/src/lib/b.rb", "B#y")]
    modules = [_module("a.rb"), _module("lib/b.rb")]

    parsed = parse(dumps(sample(analysed_modules=modules, methods=methods,
                                parse_errors=[])), ["a.rb", "lib/b.rb"])

    assert parsed.methods == {
        "a.rb": [MethodResult("A#x", 1, 1.0)],
        "lib/b.rb": [MethodResult("B#y", 1, 1.0)],
    }


def test_methods_of_unknown_and_broken_files_are_dropped():
    methods = [_method("other.rb"), _method("broken.rb"), _method("a.rb")]
    errors = [{"path": "broken.rb", "message": "bad"}]

    parsed = parse(dumps(sample(methods=methods, parse_errors=errors)),
                   ["a.rb", "broken.rb"])

    assert parsed.methods == {"a.rb": [MethodResult("A#a", 1, 1.0)]}


def test_methods_are_grouped_and_sorted():
    methods = [
        _method("a.rb", "A#low", 9, 2),
        _method("b.rb", "B#only", 3, 4.5),
        _method("a.rb", "A#zeta", 5, 10.0),
        _method("a.rb", "A#alpha", 1, 10.0),
    ]

    parsed = parse(dumps(sample(methods=methods, parse_errors=[])), ["a.rb", "b.rb"])

    assert parsed.methods == {
        "a.rb": [
            MethodResult("A#alpha", 1, 10.0),
            MethodResult("A#zeta", 5, 10.0),
            MethodResult("A#low", 9, 2.0),
        ],
        "b.rb": [MethodResult("B#only", 3, 4.5)],
    }
    assert isinstance(parsed.methods["a.rb"][2].score, float)


# --- smells ------------------------------------------------------------------------


def test_count_smells_skips_flay_and_flog():
    smells = [
        {"type": "DuplicateCode"},
        {"type": "HighComplexity"},
        {"type": "VeryHighComplexity"},
        {"type": "TooManyStatements"},
        {"type": "FeatureEnvy"},
    ]

    assert count_smells(smells) == 2


def test_count_smells_empty():
    assert count_smells([]) == 0


def test_sample_is_not_mutated():
    before = copy.deepcopy(SAMPLE)

    parse(dumps(), SENT)

    assert before == SAMPLE
