# Issue: Breakdown check_file_size.py

## Description
`python/check_file_size.py` has grown into a single large file that mixes
argument parsing, file collection, analysis, and reporting in one place. It
needs to be broken down into focused classes/files, and the resulting
structure should establish the pattern future Tingle commands follow when
they outgrow a single file.

## Problem
- `python/check_file_size.py` bundles `Constants`, `SkipChecks`,
  `FileCollector`, `FileAnalyzer`, `ArgParser`, and `Main` in one file,
  making it harder to read, test, and extend.
- There is no established, documented convention yet for how a Tingle
  command should be structured once it needs more than one file/class, nor
  a shared, reusable argument-parsing building block — each command would
  otherwise reinvent its own `argparse` setup.
- The file still has a pending `from __future__ import annotations` import
  (added with a Portuguese comment marker) that needs to be resolved as
  part of the breakdown.

## Solution
### General command breakdown pattern (to document)
- Commands are registered in `commands/*.json`, pointing at their
  implementation entry point; `bin/tingle` remains the single hub that
  parses the mapping files and dispatches to that entry point.
- A command's entry point becomes a thin shell that parses arguments and
  calls the class(es) that do the actual work.
- Implementation loads additional files from `python/` (or `shell/`,
  `node/`, per language).
- Common/reusable code lives in `python/common/`.
- Argument parsing classes live in `python/common/`:
  - A generic `ArgParser` receives the flags to configure itself.
  - It returns a JSON with the values for each option.
  - Command-specific parsers configure the generic one instead of
    duplicating parsing logic.
- Beyond arg parsing, each command breaks its own logic down by class or
  other files as needed — there's no fixed file count/shape required.

### `check_file_size` breakdown
- Extract classes to their own files under `python/check_file_size/`.
- The entry point becomes a thin shell that calls a new `CheckFileSize`
  class (orchestrator) that does the actual work — replacing today's
  `Main.run()`.
- Resolve the pending `from __future__ import annotations` forward
  reference as part of the breakdown.
- Update `commands/python.json`'s `check_file_size.path` to point at the
  new entry point, and remove the old single-file `python/check_file_size.py`.

### Target structure
```text
bin/tingle                          # hub — routes commands (existing)
python/common/arg_parser.py         # generic ArgParser (flags -> JSON of option values)
python/check_file_size/
├── __init__.py
├── check_file_size.py              # class CheckFileSize (orchestrator)
├── constants.py                    # Constants
├── skip_checks.py                  # SkipChecks
├── file_collector.py               # FileCollector
├── file_analyzer.py                # FileAnalyzer
└── reporter.py                     # Reporter (output + OK/WARN/ERROR/CRITICAL counters)
```

## Benefits
- `check_file_size` becomes easier to read, test, and extend, with each
  class owning a single responsibility.
- A documented, reusable pattern (including a shared `ArgParser`) means
  future commands don't need to reinvent argument parsing or file
  organization from scratch.
- Removes the lingering `from __future__ import annotations` TODO.
