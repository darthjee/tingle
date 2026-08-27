# Issue: Improve CI pipeline

## Description
Improve the CircleCI pipeline for Tingle's Python codebase: split the single combined test/lint job into dedicated jobs, and wire up Codacy coverage reporting.

## Problem
The current `.circleci/config.yml` has one `test` job that runs both `ruff check .` and `pytest` sequentially. There is no separation between lint and test results, and no coverage is uploaded anywhere even though `pytest-cov` already generates `python/coverage.xml` locally (`--cov-report=xml`, `--cov-fail-under=75` in `python/pyproject.toml`). There is no `.codacy.yml` and no Codacy project token in the repo.

## Expected Behavior
- CircleCI runs lint and tests as two separate jobs (e.g. `lint` and `tests`), so failures are attributable and visible independently in the CircleCI UI.
- The `tests` job uploads Python coverage to Codacy after the test run.
- A minimal `.codacy.yml` exists at the repo root as a place to add exclusions later.
- Scope is Python only (`python/`). `node/`, `shell/`, `bin/`, `commands/` are out of scope for this issue — `node/` and `shell/` currently have no real code or tooling to test/lint yet; bringing them into CI is deferred to a future issue.

## Solution
- Split `.circleci/config.yml`'s single `test` job into a `lint` job (`ruff check .`) and a `tests` job (`pytest`), both run in the `python/` working directory as today, and both added to the `test` workflow.
- At the end of the `tests` job, add a coverage-upload step using the official Codacy reporter script (downloaded fresh each run, nothing committed):
  ```bash
  bash <(curl -Ls https://coverage.codacy.com/get.sh) report -r python/coverage.xml
  ```
  A single `report` call is sufficient (not partial+final) since there's only one job producing coverage, unlike multi-job setups that need a merge step.
- Assumes a Codacy project for `darthjee/tingle` already exists with `CODACY_PROJECT_TOKEN` set as a CircleCI project-level environment variable (configured in the CircleCI web UI, not the repo) — matches the pattern used in the Majora project.
- Add a minimal `.codacy.yml` at the repo root (no exclusions needed yet).

## Benefits
- Lint and test failures are distinguishable at a glance in CircleCI instead of being buried in one job's combined output.
- Coverage becomes visible on Codacy's dashboard/PR checks instead of only existing as a local artifact.
- Establishes the `.codacy.yml` convention for future exclusions, consistent with other projects (e.g. Majora).
