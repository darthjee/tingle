# Build and smoke verification
1. `make php-complexity-image`, then `docker buildx build --platform linux/amd64 docker/php_complexity` and the same command for `linux/arm64`. Both must succeed.
2. Run the smoke test from image.md §9 by hand against `tingle_php_complexity:dev`. Use `docker run --rm -i --network none --security-opt no-new-privileges --read-only --tmpfs /tmp --user 501:20 -v "$PWD/docker/php_complexity/fixture:/src:ro" -w /src tingle_php_complexity:dev` with the 25-line stdin (19 fixture files, then the 6 hostile lines, including the empty line). Assert:
   - exit 0, and stdout is one JSON object;
   - `tool_versions` is `{php: "8.5.11", pdepend: "3.0.0", jscpd: null}`;
   - 25 entries, with `files[i].path` equal to input line `i`;
   - the per-file `parse_error`/`pdepend` values match the §9 table (`min_mi` rounded to one decimal);
   - `functions`/`duplication` are `null` everywhere;
   - the warnings match the table exactly (tool, path, message, order).
3. `docker run --rm --entrypoint sh tingle_php_complexity:dev -c 'command -v git'` fails.
4. Empty stdin prints `"files":[]`, `"warnings":[]` and exits 0.
5. Record the commands and their results in the PR description. A small throwaway script under the scratchpad is fine for the assertions, but don't commit it (`smoke_test_php_complexity` is #347).

## Files to Change
- None. Verification only.
