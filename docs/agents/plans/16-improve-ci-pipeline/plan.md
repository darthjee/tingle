# Plan: Improve CI pipeline

Issue: [16-improve-ci-pipeline.md](../../issues/16-improve-ci-pipeline.md)

## Overview
Split Tingle's single CircleCI `test` job into separate `lint` and `tests` jobs for the Python codebase, and add Codacy coverage reporting on top of the coverage already produced locally by `pytest-cov`. Scope is `python/` only — `node/`, `shell/`, `bin/`, `commands/` are out of scope, since `node/` and `shell/` currently have no real code or tooling to test/lint.

## Context
`.circleci/config.yml` currently has one `test` job that runs `ruff check .` then `pytest` sequentially, so lint and test failures aren't distinguishable in the CircleCI UI. `python/pyproject.toml` already configures `pytest-cov` to produce `python/coverage.xml` (`--cov-report=xml`, `--cov-fail-under=75`), but nothing uploads it anywhere. There is no `.codacy.yml` in the repo. A Codacy project for `darthjee/tingle` already exists, with `CODACY_PROJECT_TOKEN` set as a CircleCI project-level environment variable (configured in the CircleCI web UI, not the repo).

These are root-level, cross-cutting files (`.circleci/config.yml`, `.codacy.yml`) — not owned by any single specialist agent (`cli`, `node`, `product-owner`, `python`, `shell`), so this plan has no agent split; the architect implements it directly.

## Steps

- [01 — Split lint and tests jobs](plan/01-split-lint-and-tests-jobs.md)
- [02 — Upload coverage to Codacy](plan/02-upload-coverage-to-codacy.md)
- [03 — Add minimal .codacy.yml](plan/03-add-codacy-yml.md)

## CI Checks
- `python/`: `ruff check .` (CI job: `lint`, after this change)
- `python/`: `pytest` (CI job: `tests`, after this change)
- The change itself can only be fully validated by pushing and watching the resulting CircleCI run, since it's a change to the pipeline definition.

## Notes
- Assumes the Codacy project + `CODACY_PROJECT_TOKEN` CircleCI env var already exist (confirmed during issue refinement) — not something this plan creates.
- If the `report` upload step fails in CI (e.g. token missing/misconfigured), that's an infra/dashboard-side fix outside this repo, not a code change.
