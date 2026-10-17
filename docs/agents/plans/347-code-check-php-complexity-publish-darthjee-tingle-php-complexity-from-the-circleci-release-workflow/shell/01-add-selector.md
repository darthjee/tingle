# Add the php_complexity selector

In `scripts/release_image.sh`, add a `php_complexity)` case to `select_image()` after `js_complexity`. Set `IMAGE_NAME=darthjee/tingle_php_complexity`, `DOCKERFILE=docker/php_complexity/Dockerfile`, `BUILD_CONTEXT=docker/php_complexity`, the two description files under `docker/php_complexity/`, `CHANGE_DETECTION_PATH=""` and `SMOKE_TEST_FUNCTION=smoke_test_php_complexity`.

Update the header comment: the title line, the five per-subcommand usage lines, the settings table (a fourth column), a `Smoke test (php_complexity): see smoke_test_php_complexity().` line, and the change-detection paragraph ("the php_complexity image has NO change detection either…"). Update `USAGE`. Nothing else changes: `setup-builder` still ignores the selector, no selector still means `linux`, and an unknown selector still exits 1 through `usage`.

## Files to Change
- `scripts/release_image.sh` — new `select_image()` case, `USAGE` and header comment.
