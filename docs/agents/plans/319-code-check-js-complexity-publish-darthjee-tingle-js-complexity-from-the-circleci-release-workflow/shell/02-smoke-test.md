# Add smoke_test_js_complexity

Add `JS_COMPLEXITY_FIXTURE_DIR="docker/js_complexity/fixture"`, a fixture list array (the image.md §9 files, with relative paths such as `build/out.js` and `ext/a.mjs`), and the five hostile lines (`""`, `/etc/passwd`, `../outside.js`, `simple.js`, `missing.js`). Then add `smoke_test_js_complexity <image> <platform>`, modelled on `smoke_test_rubycritic`:

1. Run the canonical line (`--pull never --network none --security-opt no-new-privileges --platform "$platform" --user "$FOREIGN_USER" -v "$PWD/$JS_COMPLEXITY_FIXTURE_DIR:/src:ro" -w /src`). Feed it the fixture list followed by the hostile lines, and fail if the exit status is non-zero.
2. Check the JSON with an inline `python3 -c` script. It must be one object, `tool_versions.fta == "3.1.0"`, and `jscpd`/`escomplex` must be `null`. There must be one `files` entry per input line, in order. Check the FTA expectations per file: `simple.js` score < 20 and `"OK"`; `complex.ts` score > 60 and `"Needs improvement"`; `broken.js` `parse_error: true` plus a `tool: "fta"` warning; `empty.js` `parse_error: false`, `fta: null`; `short.js` and `bundle.min.js` `lines == 1`; `build/out.js`, the `ext/*` files and `ext/types.d.ts` are normal rows; `crlf.js` has the same score as `ext/a.mjs`; `bom.ts` has the same score as `ext/c.mts`; `latin1.js` has `parse_error: true` and a `file is not valid UTF-8` warning. Each hostile line must have `fta: null`, `parse_error: false` and an `entrypoint` warning. Print `<reason> on <platform>` and exit 1 on failure.
3. Check that git is absent (`--entrypoint sh -c 'command -v git'`), as in rubycritic.
4. Run with empty stdin: exit 0, `files == []` and `warnings == []`.

Check the exact JSON field names (`score`, `assessment`, `lines`, `warnings[].tool`, etc.) against `docker/js_complexity/entrypoint.js` and the image.md contract before writing the assertions.

## Files to Change
- `scripts/release_image.sh` — new fixture constants and the `smoke_test_js_complexity` function.
