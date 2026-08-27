# product-owner Plan: Set up ruff lint for python/

Main plan: [plan.md](plan.md)

## Shared contracts

- Relies on `python`'s work to make `ruff check python/` pass — documents that exact command string, run only after `python`'s step lands.

## Implementation Steps

### Step 1 — Update the lint TODO
In `docs/agents/todo.md`, remove the `python` — `ruff check python/` bullet from the "Lint/check commands per agent" list now that it's configured, leaving the remaining language entries (`shell`, `node`, `cli`) untouched.

## Files to Change
- `docs/agents/todo.md` — remove the now-resolved `python` lint item.

## Notes
- Do not touch `docs/agents/architecture.md` — the breakdown pattern it documents is unrelated to this lint-only issue.
