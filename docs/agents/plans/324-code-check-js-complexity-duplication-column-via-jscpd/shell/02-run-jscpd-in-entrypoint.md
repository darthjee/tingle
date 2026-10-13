# Run jscpd in the entrypoint
Add `docker/js_complexity/lib/jscpd.js`, modelled on `lib/fta.js`:

- `jscpdVersion()`: reads `version` from `/opt/tingle_js_complexity/node_modules/jscpd/package.json`.
- `runJscpd()`: `spawnSync` of `/opt/tingle_js_complexity/node_modules/.bin/jscpd` with `cwd: "/tmp"` and exactly the argument list in spec section 2. Both stdout and stderr are written to `process.stderr`.
- `applyJscpd(files, staged, warnings)`: reads `/tmp/jscpd/jscpd.json` and validates it (spec section 5). For each staged entry that is not a parse error, it collects the set of covered line numbers from every `firstFile`/`secondFile` range (`start..end` inclusive). Names are mapped back to input line numbers with `staging.stagedNumber`. Then:
  - each staged, non-parse-error file whose size is at most 1,048,576 bytes gets `duplication = {lines: set.size}`;
  - larger files and parse errors stay `null`;
  - refused lines stay `null`.

Failure handling (spec section 5): a spawn error, a kill signal, a non-zero exit, a missing or invalid JSON report, a malformed `duplicates` entry, or a `name` that does not map to a staged file. Each one leaves `duplication: null` on **every** file and pushes one `{tool: "jscpd", message}` warning with no `path`. It never throws an `EntrypointError` and never changes the exit status. Unlike `stagedEntry` in `fta.js`, an unknown path is a soft jscpd failure, not a fatal error.

In `entrypoint.js` `analyse()`: after FTA, still inside `if (staged.size > 0)`, call the jscpd step. Set `tool_versions.jscpd` from `jscpdVersion()`, both when files are staged and when none are. Update the header comment (dependencies and the "runs FTA" text).

The "over 1 MiB" check uses the staged file's byte size, the threshold jscpd's `--max-size 1mb` applies. Get it with `fs.statSync` on the staged copy, or record it in `stageFile`.

## Files to Change
- `docker/js_complexity/lib/jscpd.js` — new: version, invocation, report parsing, per-file line sets, soft failure.
- `docker/js_complexity/entrypoint.js` — call the jscpd step after FTA, fill `tool_versions.jscpd`, update the header comment.
- `docker/js_complexity/lib/staging.js` — only if the staged byte size or path needs a helper.
