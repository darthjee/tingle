# Entrypoint
Write `docker/js_complexity/entrypoint.js` (CommonJS, Node standard library only), implementing `image.md` §4–8 exactly. Helpers may live in `docker/js_complexity/lib/*.js`. Start the file with a header comment that documents usage and the contract.

1. **Input (§4):** read all of stdin as a Buffer and decode it with a fatal UTF-8 `TextDecoder` (failure → exit 1). Split on `\n`; a trailing `\n` adds no extra line; trim nothing. Ignore any arguments.
2. **Refusal (§4), in this order, first match wins:** `empty line`, `absolute path`, `path has a '..' segment`, `duplicate line` (counted across all earlier lines, refused or not), `not a regular file under /src` (`fs.realpathSync` must stay inside the real path of `/src`, and `lstat`/`stat` must show a regular file), `unsupported extension` (the lower-cased text after the last `.` of the basename must be in `js mjs cjs jsx ts mts cts tsx`). A refused line gets `{path, parse_error: false, fta: null, duplication: null, functions: null}` plus the warning `{"tool": "entrypoint", "path": line, "message": …}`.
3. **Encoding check and staging (§5):** read the real path. If the content is not valid UTF-8 (a BOM is fine), do not stage it: set `parse_error: true` and add the warning `{"tool": "fta", "path": line, "message": "file is not valid UTF-8"}`. Otherwise copy the bytes to `/tmp/stage/plain/<n>.<ext>`, where `<n>` is the 1-based input line number. Create `/tmp/stage/plain` with `recursive: true`.
4. **Version:** run `fta --version` once and parse `fta X.Y.Z` into `"X.Y.Z"` (failure → exit 1).
5. **FTA (§6)**, only if at least one file was staged:
   - write `/tmp/fta.json` with `{"extensions": [".mjs", ".cjs", ".mts", ".cts"]}`;
   - `spawnSync('/usr/local/bin/fta', ['/tmp/stage','--json','--config-path','/tmp/fta.json','--score-cap','1000000000','--exclude-under','0','--include-comments','false'], {cwd: '/tmp', env: <process.env without DEBUG>})`;
   - a signal → exit 1; a non-zero status → exit with FTA's status, stdout empty;
   - write FTA's stderr through to our stderr;
   - match each stderr line against `/Failed to analyze \/tmp\/stage\/(plain|sfc)\/(\d+)\.\S*: (.*)$/`, then set `parse_error: true` on line `<n>`, keep `fta: null`, and add the warning `{"tool": "fta", "path": line, "message": <error>}`;
   - parse stdout as a JSON array (anything else → exit 1). For each entry, parse `<n>` from `file_name` (`plain/<n>.<ext>`) and fail with exit 1 if it does not map to a staged line. Then set `fta = {score: fta_score, cyclo, lines: line_count, assessment}`.
6. **Output (§7):** write `JSON.stringify({tool_versions: {fta, jscpd: null, escomplex: null}, files, warnings}) + "\n"` as the only stdout write. `files` follows input order and `warnings` follows production order. For empty stdin, print empty `files` and `warnings` (with the FTA version filled), run nothing else, and exit 0.
7. **Failures (§8):** catch every unexpected error, print `tingle_js_complexity: <reason>` on stderr and exit 1, writing nothing on stdout. Write only under `/tmp`.

Keep functions small: the same complexity standards apply here. Leave room for #324, #325 and #326 to add tools without reshaping the JSON.

## Files to Change
- `docker/js_complexity/entrypoint.js` — new.
- `docker/js_complexity/lib/*.js` — optional helpers (line refusal, staging, FTA run/parse, output).
