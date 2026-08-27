# python Plan: Set up Python test infrastructure and add unit tests for check_file_size

Main plan: [plan.md](plan.md)

## Shared contracts

- Produces the exact test/lint invocation `architect`'s CircleCI job and
  Docker/`docker-compose` setup must call: `pip install -r
  requirements-dev.txt` then `pytest` (config in `python/pyproject.toml`),
  and `ruff check .` (unchanged from issue #12, now pinned in
  `requirements-dev.txt`).
- Produces `python/Dockerfile`, which `architect`'s `docker-compose.yml`
  builds from (`dockerfile: python/Dockerfile`) — must be non-root (see
  `plan.md` Notes on why: `chmod 000` permission tests need real enforcement).
- Consumes: nothing from `architect` — `python/`'s own tests, deps, and
  Dockerfile are self-contained and don't reference `.circleci/config.yml`,
  `docker-compose.yml`, or `Makefile` directly.
- Produces the decided test folder location (`python/tests/`) that
  `product-owner` records in `docs/agents/architecture.md`.

## Steps

- [01 — Add pinned dev dependencies](python/01-add-dev-dependencies.md)
- [02 — Configure pytest and coverage](python/02-configure-pytest-and-coverage.md)
- [03 — Add non-root test Dockerfile](python/03-add-test-dockerfile.md)
- [04 — Unit tests: ArgParser](python/04-test-arg-parser.md)
- [05 — Unit tests: FileCollector](python/05-test-file-collector.md)
- [06 — Unit tests: FileAnalyzer](python/06-test-file-analyzer.md)
- [07 — Unit tests: Reporter](python/07-test-reporter.md)
- [08 — Unit tests: SkipChecks](python/08-test-skip-checks.md)

## Notes

- No changes to `check_file_size`'s or `ArgParser`'s own behavior/output —
  this is test-infra/coverage only, matching the issue's explicit scope
  boundary.
- Update `.claude/agents/python.md`'s `## Commands` section to add `pytest`
  (and, if useful, `docker-compose run --rm tingle_tests pytest`) alongside
  the existing `ruff check python/` — following the same self-documenting
  pattern issue #12 used when it added `ruff check python/` there.
