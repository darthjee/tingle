# Shell Plan: code_check js_complexity: publish darthjee/tingle_js_complexity from the CircleCI release workflow

Main plan: [plan.md](plan.md)

## Shared contracts

- You produce the `js_complexity` selector with the settings, job names and smoke-test checks listed in [plan.md](plan.md#shared-contracts). product-owner documents them as written, so keep names exact.
- `linux` and `rubycritic` must behave exactly as before. Existing CircleCI job calls do not change.

## Steps

- [01 — Add the js_complexity selector](shell/01-add-selector.md)
- [02 — Add smoke_test_js_complexity](shell/02-smoke-test.md)
- [03 — Add the CircleCI release jobs](shell/03-circleci-jobs.md)
- [04 — Write the Docker Hub description files](shell/04-dockerhub-files.md)

## CI Checks
- `scripts/release_image.sh`: `bash -n scripts/release_image.sh` and `shellcheck scripts/release_image.sh` (if available). If Docker with buildx/QEMU is available, run `scripts/release_image.sh build js_complexity && scripts/release_image.sh smoke-test js_complexity` locally (the arm64 FTA build under QEMU is slow, about 100 s).
- `.circleci/config.yml`: `circleci config validate` if the CLI is available. Otherwise check the YAML parses (`python3 -c 'import yaml,sys; yaml.safe_load(open(".circleci/config.yml"))'`).
- `scripts/release_image.sh update-description js_complexity` validation: with no credentials, run it only up to the file checks (or check the short description length by hand: 1–100 chars after trimming).

## Notes
- Out of scope: the jscpd (#324), escomplex (#325) and `Cart.vue` (#326) smoke-test checks. Until then, `Cart.vue` is expected to be refused as `unsupported extension` if it is in the input list. Follow image.md §9 for whether it is piped in.
- Read `docker/js_complexity/entrypoint.js` and `lib/` for the exact warning shapes (the `entrypoint` warning message from image.md §4, `tool: "fta"` warnings, `file is not valid UTF-8`) instead of guessing.
