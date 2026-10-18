# Run jscpd from the entrypoint
Fill `tool_versions.jscpd` and `files[].duplication`, per [duplication.md §1–3 and §5](../../../specs/code_check/php_complexity/duplication.md#2-jscpd-invocation). Port `docker/js_complexity/lib/jscpd.js` to PHP, keeping the same reasons and the same structure (soft-failure exception class, report reader, clone-side validation, covered-lines map).

- New `docker/php_complexity/lib/jscpd.php`:
  - `tpc_jscpd_version()`: runs `/usr/local/bin/jscpd --version` (no shell, `proc_open` with an argument array) and matches `^jscpd (\S+)$`; a failure or no match throws `EntrypointError('cannot read the jscpd version')`.
  - `tpc_run_jscpd()`: removes `/tmp/jscpd/` (`tpc_remove_tree`), runs jscpd with cwd `/tmp` and exactly the spec's argument list (`/tmp/stage --reporters json --output /tmp/jscpd --report-name jscpd --silent --no-tips --no-colors --min-tokens 50 --min-lines 5 --mode mild --kind exact --format php --formats-exts php:php --no-gitignore --max-size 1mb`), stdout and stderr redirected to files and then copied to the entrypoint's stderr, like `tpc_run_pdepend`. Exit status non-zero → `jscpd exited with status <s>`; signaled → `jscpd killed by <signal>`.
  - Report reading and validation: missing/invalid JSON, `duplicates` not a list, malformed entry (`firstFile`/`secondFile` objects with string `name`, int `start`/`end`, `1 <= start <= end <= 1048577`), and `name` not matching `^(\d+)\.php$` for a staged `<n>` → unknown path.
  - `tpc_apply_jscpd(array &$files, array $staged, array &$warnings)`: on success sets `{"lines": count}` for each staged file that is not a parse error and is <= 1,048,576 bytes (use the staged file's size); on any soft failure sets `duplication = null` on every file and appends `['tool' => 'jscpd', 'message' => <one line>]`.
- `entrypoint.php`: require `lib/jscpd.php`; set `'jscpd' => tpc_jscpd_version()` in `$versions`; call `tpc_apply_jscpd` after the PDepend block, only when `$staged !== []` (after PDepend's rejected files are marked `parse_error`, so they keep `duplication: null` while their clones still count for the other file). Update the header comment (Output/`duplication`, jscpd's output passed through to stderr, dependencies).
- Keep `duplication` `null` for every entry when nothing is staged.

## Files to Change
- `docker/php_complexity/lib/jscpd.php` — new: jscpd version, run, report parsing, per-file lines.
- `docker/php_complexity/entrypoint.php` — wire jscpd in, header comment.
