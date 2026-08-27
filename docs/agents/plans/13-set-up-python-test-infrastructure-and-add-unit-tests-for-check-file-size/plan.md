# Plan: Set up Python test infrastructure and add unit tests for check_file_size

Issue: [13-set-up-python-test-infrastructure-and-add-unit-tests-for-check-file-size.md](../issues/13-set-up-python-test-infrastructure-and-add-unit-tests-for-check-file-size.md)

## Overview

Wire up pytest for `python/`, add a full unit test suite for `check_file_size`
and the shared `ArgParser`, and stand up the first CI pipeline the repo has
ever had (CircleCI, running lint + tests in a Docker-based, non-root
container), plus a local `docker-compose`/`Makefile` path to run the same
suite. Scoped down from the `darthjee/majora` pattern this repo is borrowing
idioms from: a stock CircleCI image, a pinned `requirements-dev.txt` instead
of Poetry, no custom/published base image, and no Codacy wiring (deferred to
a follow-up issue).

## Agents involved

- [architect](architect.md)
- [python](python.md)
- [product-owner](product-owner.md)

`architect` is listed here as a genuine implementer, not just the
coordinator — this issue explicitly assigns it ownership of the new
`.circleci/` root folder (per its own scope: "root-level files"), and it also
owns the two other repo-root files this issue introduces
(`docker-compose.yml`, `Makefile`).

## Shared contracts

- **Test invocation command**: `python` produces a self-contained `pytest`
  invocation for `python/` — dependencies from `python/requirements-dev.txt`,
  config (`testpaths`, `addopts` with `--cov --cov-report=term-missing
  --cov-report=xml --cov-fail-under=90`) from `python/pyproject.toml`. Both
  `architect`'s CircleCI job and its `docker-compose`/`Makefile` setup must
  call exactly `pytest` from a working directory of `python/` (or
  `/app` inside the container) — no extra flags needed, everything lives in
  `pyproject.toml`.
- **Lint command**: unchanged from issue #12 — `ruff check python/` (or
  `ruff check .` from within `python/`), now also pinned in
  `requirements-dev.txt` (`ruff==0.16.4`, matching the version already in use
  locally) so CI lints with the same version as local dev.
- **Docker image contract**: `python` produces `python/Dockerfile` — a
  non-root image (see Notes below) that installs
  `python/requirements-dev.txt` and runs `pytest` by default. `architect`'s
  `docker-compose.yml` builds from this Dockerfile
  (`dockerfile: python/Dockerfile`) as the single `tingle_tests` service; it
  does not need to know the image's internal user name/uid, only that `USER`
  is non-root.
- **Test folder location / new-folder ownership text**: `product-owner`
  records in `docs/agents/architecture.md` exactly what `python` and
  `architect` decided — test folder is `python/tests/` (mirroring
  `python/`'s package layout), and `.circleci/` is owned by `architect`. Both
  facts must match verbatim what's implemented, not be re-derived.

## Notes

- No Codacy wiring in this issue (deferred to a follow-up issue per the
  issue file) — the CircleCI job's only coverage output is
  `--cov-fail-under=90` failing the build locally in CI logs.
- Non-root matters functionally, not just as a security nicety: several
  planned tests `chmod 000` a file and expect a `PermissionError`/`-1`
  return; running as root would make those tests silently pass without
  exercising the code path at all. This applies to both the CircleCI image
  and the local Docker Dockerfile.
- CircleCI's `cimg/python:3.11` image already runs as a non-root `circleci`
  user by default — no extra Dockerfile/user setup is needed on the CI side,
  only for `python/Dockerfile` (the local dev/test image), which is based on
  plain `python:3.11-slim` and runs as root unless a user is added.
