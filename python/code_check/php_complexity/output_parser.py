"""output_parser.py — Check and parse the merged JSON the php_complexity image prints.

The container prints one JSON object with `tool_versions`, one `files` entry
per line tingle sent on stdin (in the same order, `path` equal to the line)
and `warnings`. `parse` checks the whole shape (including the `functions`
and `duplication` parts that later sub-issues display), maps entry `i` to
sent line `i` and returns:

- one `FileResult` per file PDepend analysed, listed without data or the
  image refused, scored by its total CCN (`0` when `pdepend` is `null`);
- the `PARSE` files with their messages;
- the refused-line warnings, in `warnings` order;
- the path-less PDepend messages, in `warnings` order;
- the tool versions and the raw warnings.

A structural problem raises `OutputFormatError` with the reason of the first
failed check.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

# Tools allowed in `warnings[].tool`.
WARNING_TOOLS = ("entrypoint", "php", "pdepend", "jscpd")

# Tools whose per-file warning carries the reason of a parse error.
PARSE_ERROR_TOOLS = ("php", "pdepend")

# Message used when a parse error has no matching warning.
UNKNOWN_ERROR = "unknown error"


class OutputFormatError(ValueError):
    """The container output does not follow the contract; carries the reason."""

    def __init__(self, reason: str):
        """Store the `reason` (the first failed check)."""
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class FileResult:
    """PDepend's figures for one sent file (`None` figures when PDepend has no data).

    `score` is the file's total CCN, the value classified by the thresholds.
    """

    line: str
    score: int
    max_ccn: int | None = None
    max_npath: int | None = None
    min_mi: float | None = None
    lloc: int | None = None
    has_data: bool = False
    duplication: dict | None = None
    functions: list[dict] | None = None


@dataclass
class ParsedOutput:
    """Per-file results, parse errors, refused lines and PDepend notes, keyed by sent line."""

    results: dict[str, FileResult] = field(default_factory=dict)
    parse_errors: dict[str, str] = field(default_factory=dict)
    refused: list[tuple[str, str]] = field(default_factory=list)
    pdepend_messages: list[str] = field(default_factory=list)
    tool_versions: dict[str, str | None] = field(default_factory=dict)
    warnings: list[dict] = field(default_factory=list)


def _is_number(value: Any) -> bool:
    """Return True for a JSON number (booleans are not numbers here)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_int(value: Any, minimum: int) -> bool:
    """Return True for a JSON integer >= `minimum` (booleans are not ints here)."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def _is_optional_int(value: Any, minimum: int) -> bool:
    """Return True for `null` or a JSON integer >= `minimum`."""
    return value is None or _is_int(value, minimum)


def _load(stdout: str) -> dict:
    """Decode `stdout` as one JSON object (ints of any size stay exact)."""
    try:
        data = json.loads(stdout)
    except ValueError as exc:
        raise OutputFormatError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise OutputFormatError("expected a JSON object")
    return data


def _tool_versions(data: dict) -> dict:
    """Return the checked `tool_versions` object."""
    versions = data.get("tool_versions")
    valid = (
        isinstance(versions, dict)
        and isinstance(versions.get("php"), str)
        and isinstance(versions.get("pdepend"), str)
        and "jscpd" in versions
        and (versions["jscpd"] is None or isinstance(versions["jscpd"], str))
    )
    if not valid:
        raise OutputFormatError("unexpected tool_versions")
    return versions


def _valid_pdepend(pdepend: Any) -> bool:
    """Return True for `null` or a `pdepend` object with the right field types."""
    if pdepend is None:
        return True
    if not isinstance(pdepend, dict) or "min_mi" not in pdepend:
        return False
    min_mi = pdepend["min_mi"]
    return (
        _is_int(pdepend.get("ccn"), 0)
        and "max_ccn" in pdepend
        and _is_optional_int(pdepend["max_ccn"], 1)
        and "max_npath" in pdepend
        and _is_optional_int(pdepend["max_npath"], 1)
        and (min_mi is None or _is_number(min_mi))
        and _is_int(pdepend.get("lloc"), 0)
    )


def _valid_duplication(duplication: Any) -> bool:
    """Return True for `null` or `{"lines": int >= 0}`."""
    if duplication is None:
        return True
    return isinstance(duplication, dict) and _is_int(duplication.get("lines"), 0)


def _valid_function(entry: Any) -> bool:
    """Return True for a `functions` entry with a name and line/ccn/npath ints >= 1."""
    return (
        isinstance(entry, dict)
        and isinstance(entry.get("name"), str)
        and all(_is_int(entry.get(key), 1) for key in ("line", "ccn", "npath"))
    )


def _valid_functions(functions: Any) -> bool:
    """Return True for `null` or a list of valid function entries."""
    if functions is None:
        return True
    return isinstance(functions, list) and all(_valid_function(f) for f in functions)


def _valid_entry(entry: Any, line: str) -> bool:
    """Return True when a `files` entry matches its sent `line` and the contract."""
    if not (isinstance(entry, dict) and entry.get("path") == line):
        return False
    parse_error = entry.get("parse_error")
    if not isinstance(parse_error, bool):
        return False
    pdepend, functions, duplication = (
        entry.get("pdepend"), entry.get("functions"), entry.get("duplication")
    )
    if parse_error and not (pdepend is None and functions is None and duplication is None):
        return False
    return (
        _valid_pdepend(pdepend)
        and _valid_functions(functions)
        and _valid_duplication(duplication)
    )


def _files(data: dict, sent_lines: list[str]) -> list[dict]:
    """Return the checked `files` list (one entry per sent line, in order)."""
    files = data.get("files")
    if not isinstance(files, list) or len(files) != len(sent_lines):
        raise OutputFormatError("files do not match the sent lines")
    for index, (entry, line) in enumerate(zip(files, sent_lines)):
        if not _valid_entry(entry, line):
            raise OutputFormatError(f"unexpected files entry: {index}")
    return files


def _valid_warning(entry: Any) -> bool:
    """Return True for a warning with a known tool, a message and an optional path."""
    return (
        isinstance(entry, dict)
        and entry.get("tool") in WARNING_TOOLS
        and isinstance(entry.get("message"), str)
        and ("path" not in entry or isinstance(entry["path"], str))
    )


def _warnings(data: dict) -> list[dict]:
    """Return the checked `warnings` list."""
    warnings = data.get("warnings")
    if not (isinstance(warnings, list) and all(_valid_warning(w) for w in warnings)):
        raise OutputFormatError("unexpected warnings")
    return warnings


def _result(entry: dict) -> FileResult:
    """Build the `FileResult` of a non-parse-error `files` entry."""
    pdepend = entry["pdepend"]
    if pdepend is None:
        return FileResult(
            entry["path"], 0, duplication=entry["duplication"], functions=entry["functions"]
        )
    return FileResult(
        entry["path"],
        pdepend["ccn"],
        pdepend["max_ccn"],
        pdepend["max_npath"],
        pdepend["min_mi"],
        pdepend["lloc"],
        True,
        entry["duplication"],
        entry["functions"],
    )


def _parse_message(warnings: list[dict], line: str) -> str:
    """Return the first PHP or PDepend warning message for `line`, else `unknown error`."""
    for warning in warnings:
        if warning.get("path") == line and warning["tool"] in PARSE_ERROR_TOOLS:
            return warning["message"]
    return UNKNOWN_ERROR


def parse(stdout: str, sent_lines: list[str]) -> ParsedOutput:
    """Check the container `stdout` and map it onto the `sent_lines`.

    Raises `OutputFormatError` when the output breaks the contract.
    """
    data = _load(stdout)
    versions = _tool_versions(data)
    files = _files(data, sent_lines)
    warnings = _warnings(data)

    parsed = ParsedOutput(tool_versions=dict(versions), warnings=list(warnings))
    for entry in files:
        line = entry["path"]
        if entry["parse_error"]:
            parsed.parse_errors[line] = _parse_message(warnings, line)
        else:
            parsed.results[line] = _result(entry)

    without_data = {line for line, r in parsed.results.items() if not r.has_data}
    parsed.refused = [
        (w["path"], w["message"])
        for w in warnings
        if w["tool"] == "entrypoint" and w.get("path") in without_data
    ]
    parsed.pdepend_messages = [
        w["message"] for w in warnings if w["tool"] == "pdepend" and "path" not in w
    ]
    return parsed
