# Add the js_complexity selector

Add a `js_complexity)` case to `select_image()` with the settings from the shared contract (`CHANGE_DETECTION_PATH=""`, so `build`, `smoke-test`, `scan` and `publish` never skip). Update the `USAGE` line to `[linux|rubycritic|js_complexity]`. Update the header comment: the per-subcommand usage lines, add a third column to the settings table, add the "no change detection" note for js_complexity next to the rubycritic one, and add a "Smoke test (js_complexity): see smoke_test_js_complexity()." pointer. `setup-builder` still ignores the selector. Nothing in `main()` changes, because it already passes the selector to `select_image`.

## Files to Change
- `scripts/release_image.sh` — new `select_image` case, `USAGE` and the header comment.
