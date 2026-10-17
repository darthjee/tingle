# Write image.md and release.md
**`docs/agents/specs/code_check/php_complexity/image.md` (#346):**
- **Files:** the `docker/php_complexity/` layout: `Dockerfile`, `composer.json`/`composer.lock`, the entrypoint (pick PHP or shell and say why), `fixture/` and `.dockerignore`.
- **Dockerfile:** the base `ARG` with tag and digest; how Composer runs at build time and is absent at runtime; no git; the non-root `USER`; `ENTRYPOINT` with no `CMD`.
- **Input:** byte handling; the refused lines (empty, absolute, `..`, duplicate, not a regular file under `/src`, unsupported extension, Blade), each with its exact warning message.
- **Staging:** each accepted line `<n>` is copied (not symlinked) to `/tmp/stage/<n>.php`; results are mapped back by `<n>`.
- **PDepend run:** the exact command line and options, the working directory and environment, and when PDepend is skipped (nothing staged).
- **XML → JSON mapping:**
  - per-file total CCN (top-level code counts as 0), max method CCN, max NPath, min MI (or the documented drop), `lloc`;
  - the per-function entries (name as `Class::method` or `function`, line, ccn), already filled in or explicitly `null` as README §9 decides.
- **Parse errors:** how they are detected, using the real format from step 01, and how they map to `parse_error: true`.
- **Output and exit status:** the exact JSON and exit status rules, including empty stdin. Writes go under `/tmp` only.
- **Smoke fixture and checks:** each fixture file with its expected result, plus the hostile lines, `--user 501:20`, read-only `/src`, no git and empty stdin.

**`docs/agents/specs/code_check/php_complexity/release.md` (#347):**
- The `php_complexity` selector in `scripts/release_image.sh`'s `select_image()`: Dockerfile, context, smoke function, descriptions.
- `smoke_test_php_complexity`.
- The CircleCI `build-and-publish-php-complexity-image` and `update-php-complexity-description` jobs and their place in the `release` workflow, mirroring the js_complexity jobs.
- `DOCKERHUB_DESCRIPTION.md` and `DOCKERHUB_SHORT_DESCRIPTION.txt`.
- The outline of `docs/agents/tingle-php-complexity-image.md`.

## Files to Change
- `docs/agents/specs/code_check/php_complexity/image.md`: new.
- `docs/agents/specs/code_check/php_complexity/release.md`: new.
