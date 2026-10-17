# Shell Plan: code_check php_complexity: publish darthjee/tingle_php_complexity from the CircleCI release workflow

Main plan: [plan.md](plan.md)

## Shared contracts

Produces everything in [plan.md](plan.md#shared-contracts): the `php_complexity` selector, `smoke_test_php_complexity`, the two CircleCI jobs and the two Docker Hub description files. product-owner documents them as built, so keep names and step labels exactly as listed there.

## Steps

- [01 — Add the php_complexity selector](shell/01-add-selector.md)
- [02 — Add smoke_test_php_complexity](shell/02-add-smoke-test.md)
- [03 — Add the Docker Hub description files](shell/03-add-dockerhub-descriptions.md)
- [04 — Add the CircleCI release jobs](shell/04-add-circleci-jobs.md)

## CI Checks
- `scripts/`: `bash -n scripts/release_image.sh && shellcheck scripts/release_image.sh`
- Locally (needs Docker with buildx/QEMU): `scripts/release_image.sh setup-builder && scripts/release_image.sh build php_complexity && scripts/release_image.sh smoke-test php_complexity`, with `CIRCLE_TAG` unset.
- `scripts/release_image.sh smoke-test bogus` prints the usage line and exits 1; `linux`, `rubycritic` and `js_complexity` still behave unchanged.
- The release workflow only runs on tags, so the CircleCI change can be checked only with `circleci config validate` (if installed) or by review.

## Notes
- Follow [release.md](../../specs/code_check/php_complexity/release.md) §4–§5 to the letter; [image.md](../../specs/code_check/php_complexity/image.md) §9 is the source of truth for the fixture list and per-file expectations.
- `docker/php_complexity/fixture/` has 20 entries, but the spec lists 19 fixture files. Use the spec's list in its order, and check what the extra entry is (for example a nested dir or a non-input file) before assuming.
- Do not touch the image contents (`Dockerfile`, `entrypoint.php`, `lib/`, `fixture/`), apart from `.dockerignore`.
