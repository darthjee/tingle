# Shell Plan: code_check php_complexity: build the tingle_php_complexity Docker image with PDepend (docker/php_complexity/)

Main plan: [plan.md](plan.md)

## Shared contracts

- Folder `docker/php_complexity/`, build context `docker/php_complexity`, local tag `tingle_php_complexity:dev` (`make php-complexity-image`).
- Until #347 adds `docs/agents/tingle-php-complexity-image.md`, the version-bump pointer in `.claude/agents/shell.md` links to `docs/agents/specs/code_check/php_complexity/image.md#13-bumping-versions`.
- The output JSON contract is spec §7. #346 emits every key: `tool_versions.jscpd`, every `functions` and every `duplication` are all `null`.

## Steps

- [01 — Composer pin and lock](shell/01-composer-pin-and-lock.md)
- [02 — Dockerfile and .dockerignore](shell/02-dockerfile-and-dockerignore.md)
- [03 — PHP entrypoint](shell/03-php-entrypoint.md)
- [04 — Smoke-test fixture](shell/04-smoke-test-fixture.md)
- [05 — Makefile target and shell agent scope](shell/05-makefile-target-and-agent-scope.md)
- [06 — Build and smoke verification](shell/06-build-and-smoke-verification.md)

## CI Checks
- None. No CI job builds this image until #347 adds the release pipeline. Verification is the manual buildx and smoke run in step 06.

## Notes
- If an observed result differs from the spec (the resolved lock packages, a fixture metric, a PDepend message), raise it on #346 and update `image.md` in the same PR rather than deviating silently.
- Commit `composer.lock` as generated. The spec's 17-package table is informational, and the lock is the source of truth.
- Never commit a `vendor/` directory.
