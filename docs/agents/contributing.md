# Contributing

## Commit Guidelines

- **Atomic and Unitary:** Each commit must represent a single logical change.
  *Example:*
  - Good: `Add rename script for bulk file renaming`
  - Bad: `Add rename script and refactor unrelated log helper`
- **No Unrelated Changes:** Do not mix unrelated changes in the same commit.
- **Separate Refactoring:** Whenever possible, separate refactoring commits from new feature or bugfix commits.

## Pull Requests

- **Descriptive Summary:** Every PR must include a clear and descriptive summary of its purpose and changes.
- **PR Description Files:** If a description cannot be provided directly in the PR, generate a file with the PR description (e.g., `docs/issues/<pr_number>_description.md`), but do not commit this file.

## Definition of Done for PRs

A PR is considered complete when:

- The stated objective has been achieved.
- The script runs correctly for its documented usage and options.
- Linting passes without errors (see Style below).
- Code is not overly complex:
  - Each script should do one thing well; if it grows unwieldy, split responsibilities into separate scripts or functions.
  - Functions should be small and do exactly one thing. If a function is growing, extract parts into separate functions.

## Style

Since Tingle spans multiple languages, apply the idiomatic style and linter for each:

| Language | Convention | Suggested lint/check |
|----------|-----------|-----------------------|
| Shell (`shell/`) | `snake_case` filenames, `set -euo pipefail` at the top of scripts | `shellcheck` |
| Python (`python/`) | `snake_case` filenames, PEP 8 | `flake8` / `ruff` |
| Node.js (`node/`) | `camelCase` or `kebab-case` filenames | `eslint` |

Each script must document its own usage and dependencies in a header comment
(see `README.md`'s "Usage" section).

## Code Organization

- Scripts are independent by default — avoid introducing shared internal
  libraries or cross-script imports unless a clear, recurring need arises.
- `bin/` holds the callable entry points meant to be placed on `PATH`. Each
  entry point is a thin wrapper that dispatches to the actual implementation
  in `shell/`, `python/`, or `node/`.

## Refactoring Guidelines

When refactoring, aim to:

- **Reduce Code Duplication:** if the same logic is copied across scripts,
  consider whether it is worth extracting into a small shared helper — but
  only once duplication is a real recurring pain point, not preemptively.
- **Keep Scripts Focused:** if a script accumulates unrelated
  responsibilities (e.g. renaming files *and* uploading them), split it into
  separate scripts.
