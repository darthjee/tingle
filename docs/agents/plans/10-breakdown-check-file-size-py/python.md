# python Plan: Breakdown check_file_size.py

Main plan: [plan.md](plan.md)

## Shared contracts

Delivers the `python/common/arg_parser.py` `ArgParser` class and the
`python/check_file_size/` package layout exactly as specified in
`plan.md`'s "Shared contracts" section — `product-owner` documents this
shape as-is, so the implementation is the source of truth.

## Implementation Steps

### Step 1 — Extract a generic `ArgParser`

Create `python/common/arg_parser.py` with a class `ArgParser` that takes a
list of flag-definition dicts (mirroring `argparse.add_argument` kwargs,
plus a `"name"` key for the flag string) and exposes `.parse(argv=None) ->
dict`, internally building and using a standard `argparse.ArgumentParser`
under the hood. No command-specific logic here — this class only knows how
to turn flag definitions into a parsed `dict`.

### Step 2 — Break down `check_file_size.py` into a package

Replace the single `python/check_file_size.py` with a
`python/check_file_size/` package:

- `python/check_file_size/__init__.py` — empty/package marker.
- `python/check_file_size/constants.py` — the `Constants` class, unchanged.
- `python/check_file_size/skip_checks.py` — the `SkipChecks` class,
  unchanged.
- `python/check_file_size/file_collector.py` — the `FileCollector` class,
  unchanged.
- `python/check_file_size/file_analyzer.py` — the `FileAnalyzer` class,
  unchanged.
- `python/check_file_size/reporter.py` — a new `Reporter` class that owns
  everything `Main.run()` currently does *after* analysis: printing the
  table, computing `counts`/`total_lines`, and printing the summary. Move
  this logic out of `Main` as-is; no behavior change.
- `python/check_file_size/check_file_size.py` — a new `CheckFileSize`
  orchestrator class that replaces `Main`: builds flags for `ArgParser`
  (from what `ArgParser.build()` used to configure), resolves/validates the
  target path, runs `FileCollector` → `FileAnalyzer` → `Reporter`, same
  flow as today's `Main.run()`. This is also the file's entry point (`if
  __name__ == "__main__":` calling `CheckFileSize().run()` or equivalent) —
  it stays a thin shell that wires the pieces together, not a place for new
  logic.
- Drop the `ArgParser` class that lives inline in today's
  `check_file_size.py` — its flag definitions move into
  `check_file_size.py`'s construction of the shared `ArgParser` from Step 1.
- While moving code, resolve the pending `from __future__ import
  annotations` TODO (today's line 21, with the Portuguese "adicionar esta
  linha" comment): keep the import (still needed for the `list[str]` /
  `Path | None`-style annotations used throughout), drop the stray comment,
  and place it as a normal top-of-file import in each new module that uses
  those annotation styles.

### Step 3 — Update command registration

- Update `commands/python.json`'s `check_file_size.path` to point at the new
  entry point (`python/check_file_size/check_file_size.py`).
- Delete the old `python/check_file_size.py` single file.
- Manually smoke-test: `python3 python/check_file_size/check_file_size.py
  python` still prints the same kind of report as before the breakdown.

## Files to Change

- `python/common/arg_parser.py` — new generic `ArgParser`.
- `python/check_file_size/__init__.py` — new package marker.
- `python/check_file_size/constants.py` — moved `Constants`.
- `python/check_file_size/skip_checks.py` — moved `SkipChecks`.
- `python/check_file_size/file_collector.py` — moved `FileCollector`.
- `python/check_file_size/file_analyzer.py` — moved `FileAnalyzer`.
- `python/check_file_size/reporter.py` — new `Reporter` (extracted from
  `Main.run()`'s printing/summary logic).
- `python/check_file_size/check_file_size.py` — new `CheckFileSize`
  orchestrator + entry point.
- `python/check_file_size.py` — deleted.
- `commands/python.json` — `check_file_size.path` updated to the new entry
  point.

## Notes

- No behavior change is intended: same flags, same output format, same
  thresholds/exit codes.
- `python/check_file_size/__init__.py` should not re-export internals
  beyond what's convenient — keep it minimal, since nothing outside this
  package imports from it yet.
