# Add the image selector to release_image.sh
Make `scripts/release_image.sh` take an optional second argument, `linux` (default) or `rubycritic`, as specified in [release.md section 4](../../../specs/code_check/rubycritic/release.md#4-pipeline).

- In `main`, read `${2:-linux}` and call a `select_image` function that sets per-image globals:
  - `IMAGE_NAME`
  - `DOCKERFILE`
  - `BUILD_CONTEXT`
  - `SHORT_DESCRIPTION_FILE`
  - `FULL_DESCRIPTION_FILE`
  - a change-detection flag/path
  - the smoke-test function name
- The values come from the table in the spec. For an unknown selector, print the usage line (now `Usage: $0 {setup-builder|build|smoke-test|scan|publish|update-description} [linux|rubycritic]`) on stderr and exit 1. `setup-builder` ignores the selector.
- `cmd_build` and `cmd_publish` use `-f "$DOCKERFILE" "$BUILD_CONTEXT"` instead of the hard-coded `-f shell/linux/Dockerfile .`.
- Change detection: `changed_since_previous` (or a wrapper) always returns "changed" for `rubycritic`. The skip messages in build/smoke-test/scan/publish stay worded for `shell/linux/` and only fire for `linux`.
- `cmd_smoke_test` dispatches to `smoke_test_image` (linux) or `smoke_test_rubycritic` (step 02).
- `cmd_update_description` already uses `$IMAGE_NAME` and the description-file variables, so it works once they are per-image.
- Update the header comment: the selector, the per-image settings, and the "no change detection for rubycritic" rule.

## Files to Change
- `scripts/release_image.sh` — selector parsing, per-image settings, Dockerfile/context in build and publish, change-detection bypass, smoke-test dispatch, usage line, header comment.
