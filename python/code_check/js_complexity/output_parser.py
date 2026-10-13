"""output_parser.py — Check and parse the merged JSON the js_complexity image prints.

The container prints one JSON object with `tool_versions`, one `files` entry
per line tingle sent on stdin (in the same order, `path` equal to the line)
and `warnings`. `parse` checks the whole shape (including the `duplication`
and `functions` parts that later sub-issues display), maps entry `i` to sent
line `i` and returns:

- one `FileResult` per file FTA analysed, dropped or the image refused, with
  the score rounded to one decimal (`0.0` when `fta` is `null`);
- the `PARSE` files with their messages;
- the refused-line warnings, in `warnings` order;
- the tool versions and the raw warnings.

A structural problem raises `OutputFormatError` with the reason of the first
failed check.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

# Tools allowed in `warnings[].tool`.
WARNING_TOOLS = ("entrypoint", "fta", "jscpd", "escomplex")

# Tools whose per-file warning carries the reason of a parse error.
PARSE_ERROR_TOOLS = ("fta", "entrypoint")

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
    """FTA's figures for one sent file (`None` figures when FTA has no data)."""

    line: str
    score: float
    cyclo: int | None = None
    lines: int | None = None
    assessment: str | None = None
    duplication: dict | None = None
    functions: list[dict] | None = None


@dataclass
class ParsedOutput:
    """Per-file results, parse errors and refused lines, keyed by sent line."""

    results: dict[str, FileResult] = field(default_factory=dict)
    parse_errors: dict[str, str] = field(default_factory=dict)
    refused: list[tuple[str, str]] = field(default_factory=list)
    tool_versions: dict[str, str | None] = field(default_factory=dict)
    warnings: list[dict] = field(default_factory=list)


def _is_number(value: Any) -> bool:
    """Return True for a JSON number (booleans are not numbers here)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_int(value: Any, minimum: int) -> bool:
    """Return True for a JSON integer >= `minimum` (booleans are not ints here)."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def _load(stdout: str) -> dict:
    """Decode `stdout` as one JSON object."""
    try:
        data = json.loads(stdout)
    except ValueError as exc:
        raise OutputFormatError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise OutputFormatError("expected a JSON object")
    return data


def _optional_str(value: Any) -> bool:
    """Return True for a string or `null`."""
    return value is None or isinstance(value, str)


def _tool_versions(data: dict) -> dict:
    """Return the checked `tool_versions` object."""
    versions = data.get("tool_versions")
    valid = (
        isinstance(versions, dict)
        and isinstance(versions.get("fta"), str)
        and "jscpd" in versions
        and _optional_str(versions["jscpd"])
        and "escomplex" in versions
        and _optional_str(versions["escomplex"])
    )
    if not valid:
        raise OutputFormatError("unexpected tool_versions")
    return versions


def _valid_fta(fta: Any) -> bool:
    """Return True for `null` or an `fta` object with the right field types."""
    if fta is None:
        return True
    return (
        isinstance(fta, dict)
        and _is_number(fta.get("score"))
        and _is_int(fta.get("cyclo"), 0)
        and _is_int(fta.get("lines"), 0)
        and isinstance(fta.get("assessment"), str)
    )


def _valid_duplication(duplication: Any) -> bool:
    """Return True for `null` or `{"lines": int >= 0}`."""
    if duplication is None:
        return True
    return isinstance(duplication, dict) and _is_int(duplication.get("lines"), 0)


def _valid_function(entry: Any) -> bool:
    """Return True for a `functions` entry with a name and line/cyclo/sloc ints >= 1."""
    return (
        isinstance(entry, dict)
        and isinstance(entry.get("name"), str)
        and all(_is_int(entry.get(key), 1) for key in ("line", "cyclo", "sloc"))
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
    fta, duplication, functions = (
        entry.get("fta"), entry.get("duplication"), entry.get("functions")
    )
    if parse_error and not (fta is None and duplication is None and functions is None):
        return False
    return _valid_fta(fta) and _valid_duplication(duplication) and _valid_functions(functions)


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
    fta = entry["fta"]
    if fta is None:
        return FileResult(
            entry["path"], 0.0, duplication=entry["duplication"], functions=entry["functions"]
        )
    return FileResult(
        entry["path"],
        round(float(fta["score"]), 1),
        fta["cyclo"],
        fta["lines"],
        fta["assessment"],
        entry["duplication"],
        entry["functions"],
    )


def _parse_message(warnings: list[dict], line: str) -> str:
    """Return the first FTA or entrypoint warning message for `line`, else `unknown error`."""
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

    without_data = {line for line, r in parsed.results.items() if r.assessment is None}
    parsed.refused = [
        (w["path"], w["message"])
        for w in warnings
        if w["tool"] == "entrypoint" and w.get("path") in without_data
    ]
    return parsed
