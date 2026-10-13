"""Container output sample (docs/agents/specs/code_check/js_complexity/image.md §7)."""

from __future__ import annotations

import copy
import json

# The sent lines matching SAMPLE["files"], in order.
LINES: list[str] = [
    "complex.ts",
    "simple.js",
    "broken.js",
    "latin1.js",
    "empty.js",
    "../outside.js",
]

SAMPLE: dict = {
    "tool_versions": {"fta": "3.1.0", "jscpd": None, "escomplex": None},
    "files": [
        {
            "path": "complex.ts",
            "parse_error": False,
            "fta": {
                "score": 71.25291592210418,
                "cyclo": 136,
                "lines": 245,
                "assessment": "Needs improvement",
            },
            "duplication": None,
            "functions": None,
        },
        {
            "path": "simple.js",
            "parse_error": False,
            "fta": {"score": 7.690944198185733, "cyclo": 1, "lines": 6, "assessment": "OK"},
            "duplication": None,
            "functions": None,
        },
        {"path": "broken.js", "parse_error": True, "fta": None, "duplication": None,
         "functions": None},
        {"path": "latin1.js", "parse_error": True, "fta": None, "duplication": None,
         "functions": None},
        {"path": "empty.js", "parse_error": False, "fta": None, "duplication": None,
         "functions": None},
        {"path": "../outside.js", "parse_error": False, "fta": None, "duplication": None,
         "functions": None},
    ],
    "warnings": [
        {"tool": "entrypoint", "path": "../outside.js", "message": "path has a '..' segment"},
        {"tool": "fta", "path": "latin1.js", "message": "file is not valid UTF-8"},
        {
            "tool": "fta",
            "path": "broken.js",
            "message": 'Error { error: (36..37, Expected(",", "numeric literal (1, 1)")) }',
        },
    ],
}

# The same output with the jscpd (#324) and escomplex (#325) parts filled in.
FILLED: dict = copy.deepcopy(SAMPLE)
FILLED["tool_versions"] = {"fta": "3.1.0", "jscpd": "5.4.1", "escomplex": "0.1.0"}
FILLED["files"][0]["duplication"] = {"lines": 0}
FILLED["files"][0]["functions"] = [
    {"name": "reducer", "line": 10, "cyclo": 12, "sloc": 40},
    {"name": "Store.dispatch", "line": 60, "cyclo": 4, "sloc": 15},
]
FILLED["files"][1]["duplication"] = {"lines": 3}
FILLED["files"][1]["functions"] = []
FILLED["files"][4]["duplication"] = {"lines": 0}
FILLED["files"][4]["functions"] = []


def sample(**changes) -> dict:
    """Return a deep copy of SAMPLE with top-level `changes` applied."""
    data = copy.deepcopy(SAMPLE)
    data.update(changes)
    return data


def entry(path: str, score: float | None = None, **changes) -> dict:
    """Return one `files` entry for `path` (`fta: null` when `score` is None)."""
    fta = None
    if score is not None:
        fta = {"score": score, "cyclo": 2, "lines": 6, "assessment": "OK"}
    data = {"path": path, "parse_error": False, "fta": fta, "duplication": None,
            "functions": None}
    data.update(changes)
    return data


def output(files: list[dict], warnings: list[dict] | None = None) -> dict:
    """Return a merged JSON object holding `files` and `warnings`."""
    return sample(files=files, warnings=warnings or [])


def dumps(data: dict | None = None) -> str:
    """Serialise `data` (default: SAMPLE) as the container would."""
    return json.dumps(SAMPLE if data is None else data) + "\n"
