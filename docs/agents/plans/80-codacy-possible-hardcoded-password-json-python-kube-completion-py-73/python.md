# Python Plan: Codacy: Possible hardcoded password: '--json' (python/kube/completion.py:73)

Main plan: [plan.md](plan.md)

## Implementation Steps

### Step 1 — Suppress the Bandit B105 false positive on the `--json` comparison

In `python/kube/completion.py`, the `_scan()` function's `if token == "--json":` branch (line 73) is flagged by Codacy/Bandit as `B105` ("Possible hardcoded password"). This is a false positive — `--json` is a CLI flag literal being recognized during bash-completion scanning, not a credential.

The sibling `elif token == "--namespace":` branch a few lines below (line 76) already carries a `# nosec B105 - CLI flag literal, not a credential` suppression comment, added under issue #79 (PR #91). Add the same comment to the `--json` branch, so both flag-literal comparisons in this function are consistently annotated.

## Files to Change
- `python/kube/completion.py` — add `# nosec B105 - CLI flag literal, not a credential` to the `if token == "--json":` line (73), matching the existing comment on the `--namespace` line (76).

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- No behavior change — this only adds a suppression comment. Existing completion tests should continue to pass unmodified.
