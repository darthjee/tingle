# Issue: Set up Python test infrastructure and add unit tests for check_file_size

## Description
No test folder, test framework, or CI test runner exists in this repo yet. Before `python/check_file_size/` (and the shared `python/common/arg_parser.py`) can get automated coverage, the repo needs pytest wired up, a decision on where tests live, a docker-based test suite, and a CircleCI job to run it.

## Problem
- `python/check_file_size/` (`CheckFileSize`, `Constants`, `SkipChecks`, `FileCollector`, `FileAnalyzer`, `Reporter`) and `python/common/arg_parser.py` (`ArgParser`) have no automated test coverage.
- No dependency management file exists (no `requirements.txt`/`Pipfile`/`pyproject.toml`), so there's nowhere to declare `pytest` as a dev dependency yet.
- No CI pipeline exists to run tests on push/PR.

## Solution
- Decide and set up the test folder location and record the decision + owning agent in `docs/agents/architecture.md`.
- Add `pytest` as a dev dependency (new dependency-management file).
- Add a Docker-based test suite setup so tests run in a reproducible environment.
- Add a CircleCI config/job that runs the test suite.
- Add unit tests for:
  - `ArgParser` — returns the correct dict of values for a given flag/argv combination.
  - `FileCollector` — respects `--exclude` and `--ext` filters, handles empty/non-existent/permission-denied paths.
  - `FileAnalyzer` — classifies line counts into OK/WARN/ERROR/CRITICAL against configurable thresholds.
  - `Reporter` — counts each category correctly and prints the expected summary.
  - `SkipChecks` — binary detection by extension and by content (first 1024 bytes, null byte / UTF-8 decode failure), including edge cases: `--top 0` meaning "show all", default `--exclude` list, `count_lines` returning -1 on missing/permission-denied paths.
- No changes to CLI flags, output format, or `bin/tingle` routing — this issue is test-infra/coverage only, not a behavior change.

### New root-level folder ownership — decided
This issue introduces `.circleci/` (new top-level folder). Owning agent: `architect` — CI config is cross-cutting (it will eventually run checks beyond just Python) rather than belonging to a single language specialist. Record this in `docs/agents/architecture.md` alongside the test folder location decision below.

### Test folder location — decided
`python/tests/`, mirroring the package layout under `python/` (e.g. `python/tests/check_file_size/`, `python/tests/common/`), rather than a top-level `tests/`. Record this in `docs/agents/architecture.md` as part of implementation.

### CI, Docker & Dependency Management
Scoped down from the `darthjee/majora` pattern (CircleCI + Docker + Codacy) — majora's base-image / multi-image / Codacy machinery exists to solve problems tingle doesn't have (compiled runtime deps, multiple image roles, a real dependency tree). Copy the *idioms* (Makefile target names, a single `*_tests` compose service), not the infrastructure.

- **CI provider**: CircleCI. A single `.circleci/config.yml` job runs `ruff check` and `pytest` directly on a stock `cimg/python:3.11` image — installing deps inline, no custom/published base image, no multi-arch build, no `release-image` job. Revisit a custom base image only if tingle later grows a compiled dependency or CI install cost becomes a real problem across many jobs.
- **Dependency management file**: a pinned `requirements-dev.txt` under `python/` (e.g. `pytest==8.x`, `pytest-cov==6.x`), installed via `pip install -r requirements-dev.txt`. Not Poetry — tingle has no runtime dependencies to lock, so Poetry's only payoff would be cosmetic consistency with majora, not worth the added ceremony (`pyproject.toml` `[tool.poetry]` section + `poetry.lock` to maintain for two dev packages). `ruff` config stays in the existing `python/pyproject.toml` as-is.
- **Coverage / Codacy — deferred**: no Codacy wiring in this issue (it needs out-of-band setup — a Codacy project + `CODACY_PROJECT_TOKEN` in CircleCI — that isn't visible from the repo and shouldn't block test infra). Instead, the CI job runs `pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=90`, giving a local pass/fail coverage gate without the external dependency. Wiring Codacy coverage upload is left as a follow-up issue.
- **Docker-based test suite**: a single `Dockerfile` (installing `requirements-dev.txt`, running `pytest`) plus one `docker-compose.yml` service (`tingle_tests`), and a `Makefile` `tests:` target running `docker-compose run --rm tingle_tests pytest` (mirroring majora's `tests:` target naming). No base/dev image split, no `version` file, no `bin/image.sh`, no DockerHub push, no multi-arch. Add a split later only if tingle grows a genuine second role (a long-running service, or a published image other repos consume).

### Performance & Security
- **Non-root test container — decided**: the Dockerfile must create and run as a non-root user (mirroring majora's `app`/`circleci` users), not root. Reason: several planned tests (`SkipChecks`/`FileAnalyzer` permission-denied cases) `chmod 000` a file and expect `PermissionError`/`-1`. Root ignores file-mode bits entirely, so running the container as root would make those tests silently pass without exercising the permission-denied code path at all. This applies to the CircleCI job's `cimg/python:3.11` image too, not just the local Docker compose service.
- **No secrets required**: deferring Codacy means this issue's CircleCI job needs no `CODACY_PROJECT_TOKEN` or other secret.
- **Dependency pinning**: `requirements-dev.txt` pins exact `pytest`/`pytest-cov` versions (not floating ranges), keeping CI/Docker/local installs reproducible.
- **CI/build performance**: expected to be fast — stock `cimg/python:3.11` image, stdlib-only code under test, only two dev dependencies to install, no compiled extensions. No caching layer planned initially.
- **`--cov-fail-under=90` threshold**: a starting gate, not a precisely justified number — adjust once real coverage numbers from the planned unit tests are in.

## Benefits
- Regressions in `check_file_size` or the shared `ArgParser` are caught automatically in CI instead of relying on manual runs.
- Establishes the test-infrastructure pattern (framework, docker, CI) future commands under `python/` (and other languages) can follow.
