# Python Plan: code_check rubycritic: remove docs/agents/specs/code_check/rubycritic/

Main plan: [plan.md](plan.md)

## Shared contracts

The JSON contract moves to `docs/agents/tingle-rubycritic-image.md`, section
`RubyCritic JSON contract` (`#rubycritic-json-contract`).

## Implementation Steps

### Step 1 — Repoint test comments that cite the removed spec
- `python/tests/code_check/rubycritic/sample_output.py:1` — docstring "The container output sample from the spec (subcommand.md §5), shared by tests." → cite docs/agents/tingle-rubycritic-image.md ("RubyCritic JSON contract").
- `python/tests/code_check/rubycritic/test_reporter.py:14` — "# The header f-string from spec §6 (as in file_size's reporter)." → drop the spec reference (e.g. "# The report header f-string (as in file_size's reporter).").

## Files to Change
- `python/tests/code_check/rubycritic/sample_output.py` — docstring.
- `python/tests/code_check/rubycritic/test_reporter.py` — comment.

## CI Checks
- `python`: `ruff check .` (CI job: `lint`), `make tests` / pytest (CI job: `tests`).
