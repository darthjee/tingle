# Python Plan: Codacy: Possible hardcoded password: '--namespace' (python/kube/completion.py:76)

Main plan: [plan.md](plan.md)

## Implementation Steps

### Step 1 — Suppress the B105 false positive
Add an inline `# nosec B105` comment on the `elif token == "--namespace":` line in `_scan()`, with a short rationale noting it's a CLI flag literal, not a credential — matching the existing suppression style already used for the B603/B607 subprocess findings in `python/kube/{scope,auth,exec,inventory}.py` (issue #57, e.g. `# nosec B603 - fixed binary, list-form args, no shell`).

## Files to Change
- `python/kube/completion.py` — add `# nosec B105 - CLI flag literal, not a credential` on line 76 (the `elif token == "--namespace":` branch inside `_scan()`).

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- No behavior change — this is a suppression-comment-only fix, same class as issue #57.
