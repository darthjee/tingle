# Build and manual smoke test
Verify by hand (`image.md` §9, §12) and record the commands and results in the PR description. Commit no script.

1. `docker buildx build --platform linux/amd64 docker/js_complexity` and the same for `linux/arm64`: both succeed.
2. `make js-complexity-image`.
3. From `docker/js_complexity/fixture`, pipe the fixture list (every file, `Cart.vue` included), then the five hostile lines (an empty line, `/etc/passwd`, `../outside.js`, a second `simple.js`, `missing.js`) into:
   `docker run --rm -i --network none --read-only --tmpfs /tmp --user 501:20 -v "$PWD":/src:ro -w /src tingle_js_complexity:dev`
   Check, for example with a `python3` one-liner:
   - exit 0, and one JSON object on stdout;
   - `tool_versions == {"fta": "3.1.0", "jscpd": null, "escomplex": null}`;
   - `len(files)` equals the number of input lines, and `files[i].path` is line `i`;
   - the `fta` column of §9 holds for every file;
   - `Cart.vue` is refused with `unsupported extension`;
   - each hostile line is `fta: null, parse_error: false` with its §4 `entrypoint` warning.
4. `docker run --rm --entrypoint sh tingle_js_complexity:dev -c 'command -v git'` fails.
5. Empty stdin (`</dev/null`) prints `"files": []` and `"warnings": []`, and exits 0.
6. Check that nothing is written outside `/tmp`: the run must succeed with `--read-only`.

If any result contradicts the spec, stop and report it on #318 instead of changing the spec.

## Files to Change
- None (verification only).
