# Extend the smoke test
Update `smoke_test_php_complexity` in `scripts/release_image.sh` per [duplication.md §6](../../../specs/code_check/php_complexity/duplication.md#6-smoke-test-docs-and-tests) and [release.md](../../../specs/code_check/php_complexity/release.md#smoke_test_php_complexity). Replace today's "`jscpd` is null" and "`duplication` is null" assertions with:

- `tool_versions.jscpd == "5.4.1"`;
- `duplication == {"lines": 13}` for `dup_a.php` and `dup_b.php`;
- `duplication == {"lines": 0}` for every other normal row, including `bootstrap.php` and `empty.php`;
- `duplication is None` for the parse errors and the refused lines;
- no warning with `tool == "jscpd"`;
- `command -v node` fails inside the image (e.g. `docker run --rm --entrypoint sh <image> -c 'command -v node'` must exit non-zero).

## Files to Change
- `scripts/release_image.sh` — new jscpd/duplication assertions and the no-Node check in `smoke_test_php_complexity`.
