"""Container output sample (docs/agents/specs/code_check/php_complexity/image.md §7).

`SAMPLE` is the real merged JSON of the grounding image on
`docker/php_complexity/fixture` (cli.md §6 "Full example"), for the 18 lines
tingle selects there (`welcome.blade.php` and `notes.txt` are not sent).
"""

from __future__ import annotations

import copy
import json

# The sent lines matching SAMPLE["files"], in order (sorted, as tingle sends them).
LINES: list[str] = [
    "Anon.php",
    "CVS/legacy.php",
    "Calculator.php",
    "Modern.php",
    "Shapes.php",
    "UPPER.PHP",
    "attr_anon.php",
    "bom.php",
    "bootstrap.php",
    "broken.php",
    "crlf.php",
    "dup_a.php",
    "dup_b.php",
    "empty.php",
    "helpers.php",
    "latin1.php",
    "lenient.php",
    "page.php",
]

# (path, ccn, max_ccn, max_npath, min_mi, lloc); None for `pdepend: null`.
_FIGURES: dict[str, tuple | None] = {
    "Anon.php": (2, 2, 4, 66.280553464404, 6),
    "CVS/legacy.php": (2, 2, 2, 79.502485917776, 2),
    "Calculator.php": (11, 7, 36, 53.875623305512, 22),
    "Modern.php": (2, 1, 1, 79.267620989406, 11),
    "Shapes.php": (6, 2, 2, 77.64073367968, 11),
    "UPPER.PHP": (2, 2, 2, 77.749123910262, 2),
    "bom.php": (2, 2, 2, 79.502485917776, 2),
    "bootstrap.php": None,
    "crlf.php": (2, 2, 2, 79.502485917776, 2),
    "dup_a.php": (3, 3, 4, 58.109128232969, 9),
    "dup_b.php": (3, 3, 4, 58.109128232969, 9),
    "empty.php": None,
    "helpers.php": (4, 3, 4, 66.486020616616, 12),
    "latin1.php": (1, 1, 1, 83.134143220375, 2),
    "page.php": (2, 2, 2, 89.708566255425, 4),
}

# The files PHP or PDepend rejected.
PARSE_ERRORS: tuple[str, ...] = ("attr_anon.php", "broken.php", "lenient.php")


def _pdepend(ccn, max_ccn, max_npath, min_mi, lloc) -> dict:
    return {
        "ccn": ccn, "max_ccn": max_ccn, "max_npath": max_npath, "min_mi": min_mi, "lloc": lloc,
    }


def _fixture_entry(path: str) -> dict:
    if path in PARSE_ERRORS:
        return {"path": path, "parse_error": True, "pdepend": None, "functions": None,
                "duplication": None}
    figures = _FIGURES[path]
    return {
        "path": path,
        "parse_error": False,
        "pdepend": None if figures is None else _pdepend(*figures),
        "functions": None,
        "duplication": None,
    }


SAMPLE: dict = {
    "tool_versions": {"php": "8.5.11", "pdepend": "3.0.0", "jscpd": None},
    "files": [_fixture_entry(line) for line in LINES],
    "warnings": [
        {
            "tool": "php",
            "path": "broken.php",
            "message": 'syntax error, unexpected token ":", expecting variable on line 10',
        },
        {"tool": "php", "path": "lenient.php", "message": 'syntax error, unexpected token ";" on line 5'},
        {"tool": "pdepend", "path": "attr_anon.php", "message": "Unexpected token: #[, line: 14, col: 20"},
    ],
}

# The same output with the functions (#351) and jscpd (#352) parts filled in.
FILLED: dict = copy.deepcopy(SAMPLE)
FILLED["tool_versions"] = {"php": "8.5.11", "pdepend": "3.0.0", "jscpd": "5.4.1"}
for _entry in FILLED["files"]:
    if not _entry["parse_error"]:
        _entry["functions"] = []
        _entry["duplication"] = {"lines": 0}
FILLED["files"][2]["functions"] = [
    {"name": "Calculator::add", "line": 7, "ccn": 1, "npath": 1},
    {"name": "Calculator::sign", "line": 12, "ccn": 3, "npath": 3},
    {"name": "Calculator::grade", "line": 22, "ccn": 7, "npath": 36},
]
FILLED["files"][11]["functions"] = [{"name": "normalize_a", "line": 3, "ccn": 3, "npath": 4}]
FILLED["files"][11]["duplication"] = {"lines": 13}


def sample(**changes) -> dict:
    """Return a deep copy of SAMPLE with top-level `changes` applied."""
    data = copy.deepcopy(SAMPLE)
    data.update(changes)
    return data


def entry(path: str, ccn: int | None = None, **changes) -> dict:
    """Return one `files` entry for `path` (`pdepend: null` when `ccn` is None).

    `changes` keys named like `pdepend` fields (`max_ccn`, `max_npath`,
    `min_mi`, `lloc`) update the `pdepend` object; the others the entry.
    """
    pdepend = None
    if ccn is not None:
        pdepend = _pdepend(ccn, 2, 4, 66.0, 6)
        for key in ("max_ccn", "max_npath", "min_mi", "lloc"):
            if key in changes:
                pdepend[key] = changes.pop(key)
    data = {"path": path, "parse_error": False, "pdepend": pdepend, "functions": None,
            "duplication": None}
    data.update(changes)
    return data


def output(files: list[dict], warnings: list[dict] | None = None) -> dict:
    """Return a merged JSON object holding `files` and `warnings`."""
    return sample(files=files, warnings=warnings or [])


def dumps(data: dict | None = None) -> str:
    """Serialise `data` (default: SAMPLE) as the container would."""
    return json.dumps(SAMPLE if data is None else data) + "\n"
