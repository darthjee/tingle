# Shell Plan: code_check js_complexity: build the tingle_js_complexity Docker image with FTA (docker/js_complexity/)

Main plan: [plan.md](plan.md)

## Shared contracts

- Build context `docker/js_complexity/`; local tag `tingle_js_complexity:dev` via `make js-complexity-image`.
- [`image.md`](../../specs/code_check/js_complexity/image.md) is normative. Copy versions, digests, options, warning messages and JSON keys from it verbatim. If the spec turns out to be wrong, stop and report it; do not deviate silently.

## Steps

- [01 — package.json and lock](shell/01-package-json-and-lock.md)
- [02 — Dockerfile and .dockerignore](shell/02-dockerfile.md)
- [03 — Entrypoint](shell/03-entrypoint.md)
- [04 — Fixture](shell/04-fixture.md)
- [05 — Makefile target and shell agent scope](shell/05-makefile-and-agent-scope.md)
- [06 — Build and manual smoke test](shell/06-build-and-smoke-test.md)

## CI Checks
- No CI job builds `docker/js_complexity/` until #319. The `lint` (`ruff check .`) and `tests` (`pytest`) jobs are unaffected; run them only if a Python file is touched by mistake (none should be).

## Notes
- **Out of scope:** `scripts/release_image.sh`, `.circleci/`, the `DOCKERHUB_*` files, `docs/agents/`, `python/`, jscpd, escomplex and SFC.
- **No unit tests** for the entrypoint, matching `docker/rubycritic/`. The manual smoke test (step 06) is the check, and its results go in the PR description.
- Multi-arch builds of the Rust stage are slow under emulation (about 100 s for amd64 on an arm64 host, per the spec).
