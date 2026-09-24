# Python Plan: Codacy: Disable pydocstyle D213 (conflicts with D212) (40 occurrences)

Main plan: [plan.md](plan.md)

## Shared contracts

- Convention is D212. ruff enforces it via `python/pyproject.toml`, and the root `.prospector.yaml` (owned by architect) disables D213 for Codacy.
- The comment added here points to `/.prospector.yaml` and issue #203.

## Implementation Steps

### Step 1 — Enforce D212 in ruff
In `python/pyproject.toml`, add a `[tool.ruff.lint]` table with `extend-select = ["D212"]` and a short comment: D212 is the project's docstring convention, D213 is disabled for Codacy in `/.prospector.yaml`, see #203. Use `extend-select`, not `select`, so ruff's default rule set stays as it is. Place the table before the existing `[tool.ruff.lint.per-file-ignores]`.

### Step 2 — Make the lint pass
Run `ruff check .` from `python/` (via `docker-compose run --rm tingle_tests ruff check .` if ruff isn't installed locally). Rewrite any docstring flagged by D212 so its summary starts on the same line as the opening `"""`, keeping the text unchanged. Codacy's D213 report suggests all 40 multi-line docstrings already comply, so few or no fixes are expected. Then run `pytest` to confirm nothing else changed.

## Files to Change
- `python/pyproject.toml`: add `[tool.ruff.lint] extend-select = ["D212"]` with a comment.
- `python/**/*.py`: only if ruff flags a D212 violation; docstring layout only.

## CI Checks
- `python/`: `ruff check .` (CI job: `lint`)
- `python/`: `pytest` (CI job: `tests`)

## Notes
- The rest of the `D` family (D1xx missing docstrings, etc.) is out of scope.
