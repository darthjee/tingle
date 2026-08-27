# architect Plan: Set up Python test infrastructure and add unit tests for check_file_size

Main plan: [plan.md](plan.md)

## Shared contracts

- Depends on `python` producing `python/Dockerfile` (non-root, installs
  `python/requirements-dev.txt`, default `CMD` runs `pytest`) and
  `python/requirements-dev.txt`/`python/pyproject.toml` defining the exact
  install + test command (`pip install -r requirements-dev.txt`, then
  `pytest`, config lives in `pyproject.toml`).
- Produces: the CircleCI job definition and local `docker-compose`/`Makefile`
  wiring that `product-owner` references (folder location + ownership) when
  recording `docs/agents/architecture.md`.

## Steps

- [01 — Add CircleCI config](architect/01-add-circleci-config.md)
- [02 — Add docker-compose service](architect/02-add-docker-compose-service.md)
- [03 — Add Makefile test target](architect/03-add-makefile-test-target.md)

## Notes

- These three files are new repo-root artifacts (`.circleci/config.yml` is
  also a brand-new top-level folder) — this issue's own dialogue explicitly
  named `architect` as the owner of `.circleci/`, consistent with root-level
  files being architect's scope.
