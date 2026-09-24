# Plan: Codacy: Use of assert detected (Bandit B101) in python/tests/ (294 occurrences)

Issue: [194-codacy-use-of-assert-detected-bandit-b101-in-python-tests-294-occurrences.md](../../issues/194-codacy-use-of-assert-detected-bandit-b101-in-python-tests-294-occurrences.md)

## Overview
Add a Bandit-only path exclusion for `python/tests/**` to the root `.codacy.yml`, so Codacy stops reporting B101 (use of `assert`) on pytest files, while Bandit keeps analysing production code (including B101) and other Codacy tools keep analysing the tests.

## Context
All 294 open Bandit B101 findings are in `python/tests/`, where plain `assert` is idiomatic pytest and tests never run under `python -O`. Bandit's `skips` setting is global (it cannot be limited to one directory), and a repo-level Bandit config file would override the patterns selected in the Codacy UI. So the narrowest option is a per-engine `exclude_paths` entry in `.codacy.yml`. The file currently has only a header comment ("No exclusions yet"), which asks that each exclusion be scoped and say why it exists. `.codacy.yml` is a root-level file, so it belongs to the architect. No specialist owns it.

## Implementation Steps

### Step 1 — Add the Bandit exclusion to `.codacy.yml`
Keep the documentation link in the header. Replace "No exclusions yet" with a line saying exclusions must stay scoped and documented. Then add:

```yaml
engines:
  bandit:
    # pytest uses plain `assert` idiomatically and tests never run under `python -O`,
    # so Bandit B101 is pure noise here (issue #194). Scoped to Bandit only: other
    # tools still analyse the tests, and production code keeps full Bandit coverage.
    exclude_paths:
      - "python/tests/**"
```

Do not add a global `exclude_paths`, do not add `.bandit` / `[tool.bandit]`, and do not touch the asserts or existing `# nosec` comments.

### Step 2 — Verify
Validate the YAML (e.g. `python3 -c "import yaml,sys; print(yaml.safe_load(open('.codacy.yml')))"`, or `ruby -ryaml -e 'p YAML.load_file(".codacy.yml")'`), and confirm the only change is `.codacy.yml`. After merge, confirm on the Codacy dashboard that the B101 findings under `python/tests/` are gone, and that Bandit findings still show for `python/kube/`, `python/common/` and `python/check_file_size/`.

## Files to Change
- `.codacy.yml` — add a documented `engines.bandit.exclude_paths: ["python/tests/**"]` and update the header comment.

## Notes
- This hides *all* Bandit rules in `python/tests/`, not just B101. The user accepted this over adding 294 `# nosec B101` comments.
- The effect shows up only after Codacy re-analyses the default branch. There is no local CI job to run for this change (CircleCI only uploads coverage to Codacy).
- The untracked `.codacy/` folder (the local Codacy CLI config) is out of scope.
