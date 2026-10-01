"""output_parser.py — Check and parse the JSON the RubyCritic image prints.

The container prints RubyCritic's `report.json` plus a `parse_errors` key.
`parse` checks its structure, maps every path back to a line tingle sent on
stdin and returns one `FileResult` per sent file (a file missing from the
output counts as complexity 0), the parse errors, the overall score and,
when the `methods` key is present, each file's per-method Flog scores.
A structural problem raises `OutputFormatError` with the reason.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from code_check.rubycritic.constants import Constants


class OutputFormatError(ValueError):
    """The container output does not follow the contract; carries the reason."""

    def __init__(self, reason: str):
        """Store the `reason` (the first failed check)."""
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class FileResult:
    """RubyCritic's figures for one file."""

    complexity: float
    rating: str
    smells: int
    duplication: float


@dataclass(frozen=True)
class MethodResult:
    """Flog's score for one method of a file."""

    name: str
    line: int
    score: float


# Result for a sent file that RubyCritic left out of its report.
MISSING_RESULT = FileResult(0.0, "-", 0, 0)


@dataclass
class ParsedOutput:
    """Per-file results and parse errors, keyed by sent line, plus the overall score."""

    results: dict[str, FileResult] = field(default_factory=dict)
    parse_errors: dict[str, str] = field(default_factory=dict)
    score: float | None = None
    methods: dict[str, list[MethodResult]] | None = None


def _is_number(value: Any) -> bool:
    """Return True for a JSON number (booleans are not numbers here)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def normalize_path(path: str) -> str:
    """Remove a leading `/src/`, then any leading `./`, from a reported path."""
    path = path.removeprefix("/src/")
    while path.startswith("./"):
        path = path[2:]
    return path


def _load(stdout: str) -> dict:
    """Decode `stdout` as one JSON object."""
    try:
        data = json.loads(stdout)
    except ValueError as exc:
        raise OutputFormatError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise OutputFormatError("expected a JSON object")
    return data


def _valid_module(entry: Any) -> bool:
    """Return True when an `analysed_modules` entry has the fields with the right types."""
    return (
        isinstance(entry, dict)
        and isinstance(entry.get("path"), str)
        and _is_number(entry.get("complexity"))
        and isinstance(entry.get("rating"), str)
        and isinstance(entry.get("smells"), list)
        and _is_number(entry.get("duplication"))
    )


def _modules(data: dict) -> list[dict]:
    """Return the checked `analysed_modules` list."""
    modules = data.get("analysed_modules")
    if not isinstance(modules, list):
        raise OutputFormatError("unexpected analysed_modules")
    for index, entry in enumerate(modules):
        if not _valid_module(entry):
            path = entry.get("path") if isinstance(entry, dict) else None
            label = path if isinstance(path, str) else index
            raise OutputFormatError(f"unexpected analysed_modules entry: {label}")
    return modules


def _score(data: dict) -> float | None:
    """Return the checked overall score (`None` when RubyCritic did not run)."""
    score = data.get("score")
    if score is not None and not _is_number(score):
        raise OutputFormatError("unexpected score")
    return score


def _parse_errors(data: dict) -> list[dict]:
    """Return the checked `parse_errors` list (missing means none)."""
    errors = data.get("parse_errors", [])
    valid = isinstance(errors, list) and all(
        isinstance(e, dict)
        and isinstance(e.get("path"), str)
        and isinstance(e.get("message"), str)
        for e in errors
    )
    if not valid:
        raise OutputFormatError("unexpected parse_errors")
    return errors


def _valid_method(entry: Any) -> bool:
    """Return True when a `methods` entry has the fields with the right types."""
    return (
        isinstance(entry, dict)
        and isinstance(entry.get("path"), str)
        and isinstance(entry.get("name"), str)
        and isinstance(entry.get("line"), int)
        and not isinstance(entry.get("line"), bool)
        and _is_number(entry.get("score"))
    )


def _methods(data: dict) -> list[dict] | None:
    """Return the checked `methods` list (`None` when the key is absent)."""
    if "methods" not in data:
        return None
    methods = data["methods"]
    if not (isinstance(methods, list) and all(_valid_method(m) for m in methods)):
        raise OutputFormatError("unexpected methods")
    return methods


def _group_methods(methods: list[dict], lines: set[str]) -> dict[str, list[MethodResult]]:
    """Group `methods` by normalised path, keeping only `lines`; best score first."""
    grouped: dict[str, list[MethodResult]] = {}
    for entry in methods:
        path = normalize_path(entry["path"])
        if path in lines:
            grouped.setdefault(path, []).append(
                MethodResult(entry["name"], entry["line"], float(entry["score"]))
            )
    for results in grouped.values():
        results.sort(key=lambda m: (-m.score, m.name))
    return grouped


def count_smells(smells: list) -> int:
    """Count the Reek smells: entries whose type is not a Flay or Flog one."""
    return sum(
        1
        for smell in smells
        if not (isinstance(smell, dict) and smell.get("type") in Constants.NON_REEK_SMELL_TYPES)
    )


def parse(stdout: str, sent_lines: list[str]) -> ParsedOutput:
    """Check the container `stdout` and map it onto the `sent_lines`.

    Raises `OutputFormatError` when the output breaks the contract.
    """
    data = _load(stdout)
    modules = _modules(data)
    score = _score(data)
    errors = _parse_errors(data)
    methods = _methods(data)

    sent = set(sent_lines)
    parsed = ParsedOutput(score=score)
    for error in errors:
        path = normalize_path(error["path"])
        if path in sent:
            parsed.parse_errors.setdefault(path, error["message"])

    found: dict[str, FileResult] = {}
    for module in modules:
        path = normalize_path(module["path"])
        if path in sent and path not in found:
            found[path] = FileResult(
                float(module["complexity"]),
                module["rating"],
                count_smells(module["smells"]),
                module["duplication"],
            )

    for line in sent_lines:
        if line not in parsed.parse_errors:
            parsed.results[line] = found.get(line, MISSING_RESULT)
    if methods is not None:
        parsed.methods = _group_methods(methods, set(parsed.results))
    return parsed
