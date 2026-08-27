# python Plan: Set up ruff lint for python/

Main plan: [plan.md](plan.md)

## Shared contracts

- Owns the ruff config file, placed inside `python/` (e.g. `python/pyproject.toml` or `python/ruff.toml`) so `ruff check python/` picks it up via auto-discovery.
- Must make `ruff check python/` exit clean — `product-owner` will reference that exact command in `docs/agents/todo.md`.

## Implementation Steps

### Step 1 — Add ruff config and fix violations
Add a ruff configuration scoped to `python/` (reasonable defaults: line length, target Python version, the default rule set). Run `ruff check python/` against `python/check_file_size/` and `python/common/arg_parser.py` and fix every violation it reports. No CLI flags, output format, or `bin/tingle` routing changes — lint-only.

### Step 2 — Document the lint command
Update `.claude/agents/python.md`'s "Commands" section, replacing "No lint/check command is configured yet..." with `ruff check python/` as the documented lint command for this agent.

## Files to Change
- `python/pyproject.toml` (or `python/ruff.toml`) — new ruff config scoped to `python/`.
- `python/check_file_size/*.py`, `python/common/arg_parser.py` — fix any lint violations `ruff check python/` reports.
- `.claude/agents/python.md` — document `ruff check python/` as the lint command.

## Notes
- No test suite exists yet to run alongside lint — tracked separately in issue #13 (test infrastructure). This plan is lint-only.
- If `ruff check python/` reports zero violations against the current code, Step 1 only needs the config file added — no source changes.
