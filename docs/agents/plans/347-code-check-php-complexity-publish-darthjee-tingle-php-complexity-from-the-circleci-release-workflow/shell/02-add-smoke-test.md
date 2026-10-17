# Add smoke_test_php_complexity

Add `PHP_COMPLEXITY_FIXTURE_DIR`, `PHP_COMPLEXITY_FIXTURE_FILES` (the 19 files of image.md §9, in that order) and `PHP_COMPLEXITY_HOSTILE_LINES=("" /etc/passwd ../outside.php Calculator.php missing.php notes.txt)` after the js_complexity block. Then add `smoke_test_php_complexity()`, laid out like `smoke_test_js_complexity()`, with a header comment summarizing its checks.

For each platform, it:
1. pipes the fixture files then the hostile lines into the canonical run line (`--pull never --network none --security-opt no-new-privileges --platform <p> --user "$FOREIGN_USER" -v "$PWD/docker/php_complexity/fixture:/src:ro" -w /src`), and fails on a non-zero exit;
2. checks stdout with an embedded `python3 -c` script: one JSON object; the pinned tool versions (PHP, PDepend) and `tool_versions.jscpd` `null`; 25 `files` entries whose `path` equals input line `i`; the per-file expectations and the exact `warnings` from image.md §9 (`min_mi` compared with `round(..., 1)`); `functions` and `duplication` `null` on every row;
3. runs `command -v git` through `--entrypoint sh` and fails if it succeeds;
4. pipes empty stdin and checks `"files": []`, `"warnings": []` and exit 0.

Every failure goes through `smoke_fail` / `fail()` with the message `<reason> on <platform>`. Take the exact per-file values and warning messages from image.md §9 and the grounding run in §10, and do not invent thresholds.

## Files to Change
- `scripts/release_image.sh` — fixture constants and `smoke_test_php_complexity()`.
