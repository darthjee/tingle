# Product-owner Plan: code_check php_complexity: publish darthjee/tingle_php_complexity from the CircleCI release workflow

Main plan: [plan.md](plan.md)

## Shared contracts

Documents, as built by shell, everything in [plan.md](plan.md#shared-contracts): the `php_complexity` selector and its settings, `smoke_test_php_complexity`'s checks, the two CircleCI jobs and their dependencies (including `build-and-publish-release` now requiring four image jobs), and the two Docker Hub description files.

## Implementation Steps

### Step 1 — Write docs/agents/tingle-php-complexity-image.md
Create the doc in the style of `docs/agents/tingle-js-complexity-image.md`, with the seven sections of [release.md](../../specs/code_check/php_complexity/release.md) §6:
1. header bullets (image, tag strategy, source/stages, pins);
2. the contract;
3. runtime user and hardening;
4. the release pipeline (selector, steps, smoke-test checks, CircleCI jobs, no change detection);
5. the Docker Hub description;
6. local build (`make php-complexity-image`, `--image tingle_php_complexity:dev`);
7. bumping versions.

Take the contract, pins and hardening details from [image.md](../../specs/code_check/php_complexity/image.md) and from the actual `docker/php_complexity/` files. Do not invent anything. Leave out the parts that #348, #351 and #352 have not delivered yet: the CLI subcommand, `--details` and jscpd.

### Step 2 — Link the new doc from the existing docs
- `tingle-linux-image.md`, `tingle-rubycritic-image.md` and `tingle-js-complexity-image.md`: add a one-line pointer to the new doc next to the existing cross-image pointers. In each note saying a git tag `X.Y.Z` triggers the image jobs, also list `build-and-publish-php-complexity-image` / `update-php-complexity-description`, and add the fourth requirement of `build-and-publish-release`. Change "all three images" to "all four images" wherever that wording appears.
- `folder-structure.md`: in the `scripts/` row, add the `php_complexity` selector and `darthjee/tingle_php_complexity`. In the `docker/` row, point `docker/php_complexity/` at `tingle-php-complexity-image.md` instead of the spec.
- Grep `docs/agents/` (outside `specs/`, `issues/` and `plans/`) for other lists of the release images or jobs, and update them the same way.

## Files to Change
- `docs/agents/tingle-php-complexity-image.md` — new.
- `docs/agents/tingle-linux-image.md` — pointer and release-job notes.
- `docs/agents/tingle-rubycritic-image.md` — pointer and release-job notes.
- `docs/agents/tingle-js-complexity-image.md` — pointer, release-job notes and "four images" wording.
- `docs/agents/folder-structure.md` — `scripts/` and `docker/` rows.

## Notes
- Write this after shell's work, so the doc matches the real script, job names and description files.
- Leave `docs/agents/specs/code_check/php_complexity/` alone. #353 removes it.
