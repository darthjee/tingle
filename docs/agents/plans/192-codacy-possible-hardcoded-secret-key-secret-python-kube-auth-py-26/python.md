# Python Plan: Codacy: Possible hardcoded secret key (secret) (python/kube/auth.py:26)

Main plan: [plan.md](plan.md)

## Overview
`ENV_SECRET_KEY = "AWS_SECRET_ACCESS_KEY"` stores the *name* of an environment variable, not a secret. Codacy reports it twice: Prospector's dodgy check (#192, Error) and Bandit B105 (#193). Add one inline suppression comment that covers both tools, keeping the constant name and value unchanged.

## Context
- The repo already suppresses Bandit false positives inline with a justification, e.g. `python/kube/completion.py:72` (`# nosec B105 - CLI flag literal, not a credential`) and `python/kube/auth.py:21` (`# nosec B404 - ...`).
- Bandit honours `# nosec B105`; dodgy does not, but Prospector drops any message on a line carrying `# noqa`.
- The user chose inline suppression only — no renaming or restructuring of the constant.

## Implementation Steps

### Step 1 — Add the inline suppression
Change line 26 of `python/kube/auth.py` to:

```python
ENV_SECRET_KEY = "AWS_SECRET_ACCESS_KEY"  # nosec B105 - env var name, not a secret value  # noqa
```

Leave line 25 (`ENV_ACCESS_KEY`) and every other line untouched. The resulting line is 97 characters, within the configured `line-length = 100`.

### Step 2 — Verify
Run `ruff check .` and `pytest` from `python/` to confirm lint and tests (including coverage threshold) still pass. The PR description must reference both issues so #193 closes with #192 (e.g. `Fixes #192`, `Fixes #193`).

## Files to Change
- `python/kube/auth.py` — add `# nosec B105 - env var name, not a secret value  # noqa` to line 26.

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- It is unverified whether Codacy's Prospector wrapper honours `# noqa`. If Codacy still reports the dodgy finding after merge, a follow-up issue can restructure the literal; that is out of scope here per the user's decision.
- Ruff's default rule set does not enable PGH004 (blanket `noqa`), so the bare `# noqa` will not trip lint.
