# Issue: code_check php_complexity: add the tingle code_check php_complexity subcommand (runner, report, thresholds)

## Description
Add the `tingle code_check php_complexity <path>` subcommand (parent #344). It selects the `.php` files on the host, runs them through the `darthjee/tingle_php_complexity` image (PDepend), and prints a per-file complexity report with thresholds and a CI gate. It is built on the shared `python/code_check/docker_check/` package (used as is, not changed), the same way as `rubycritic` and `js_complexity`.

**Normative spec:** `docs/agents/specs/code_check/php_complexity/cli.md`, with the shared contracts in `README.md` (written by #345). The spec takes precedence over this body.

Depends on #345 only. A local build of the image from #346 (`make php-complexity-image`) is used via `--image tingle_php_complexity:dev` for manual end-to-end testing.

## Problem
Tingle can measure Ruby and JS/TS complexity but not PHP.

## Expected Behavior
### Package `python/code_check/php_complexity/`
Laid out like `js_complexity/` (`flags`, `constants`, `errors`, `docker_runner`, `image`, `selection`, `output_parser`, `reporter`, a stub `config`, `executor`), each module a thin binding of `docker_check`.

- **Constants:**
  - `DEFAULT_WARN/ERROR/CRITICAL = 20/40/60`
  - `EXTENSIONS = [".php"]` (case-insensitive), with `*.blade.php` skipped
  - `DEFAULT_EXCLUDES` = `file_size`'s list (which already has `vendor`) plus `var`, `storage` and `.phpunit.cache`
  - `bootstrap/cache` is skipped by a separate path rule (`BOOTSTRAP_CACHE`), not by a name in the exclude list
  - `IMAGE_REPO = "darthjee/tingle_php_complexity"`
- **Selection (base only):** `.php` files minus the default excludes, Blade templates and `bootstrap/cache`, with symlink confinement. A single-file `<path>` is selected only if it is a non-Blade `.php` file. Unsendable names are dropped with a warning. If nothing is selected, the output is `No PHP files found for analysis.` and the exit code is 0, with no Docker call.
- **Output parser:** reads the image's merged JSON, maps container paths back to host paths, and rejects malformed output (`Error: could not parse the output of <image>: <reason>`, exit 1).
- **Reporter:**
  - The layout is `Analyzing:`, `Thresholds:`, a table and a summary.
  - Columns: `Status`, `CCN` (total, decides the level), `Max`, `NPath`, `MI`, `Lines`, `File`. Rows are sorted by CCN, highest first. `PARSE` rows come last, in the order the files were sent.
  - The summary has file counts per level plus `CCN: avg X | max Y` (`CCN: n/a` when there is no level row).
- **Flags:**
  - `--warn/--error/--critical` (numbers ≥ 0, decimals allowed)
  - `--top N` and `--min-level`: these limit the display only
  - `--fail-on <level>` (exits 2)
  - `--image`
- **`PARSE` rows:** a file PDepend can't parse is a `⛔ PARSE` row, counted as skipped, and never triggers `--fail-on`. It is always shown and is not counted by `--top`.
- **Exit codes:** `0` OK, `1` error (Docker missing, PDepend failure, mount failure, bad output, bad path, usage error), `2` gate.

### Registration and docs
- `SUBCOMMAND_NAMES` (`python/code_check/subcommands.py`), `SUBCOMMANDS["php_complexity"]` after `js_complexity` (`python/code_check/executor.py`), `long_help`, `commands/python.json` and tab completion (`python/code_check/completion.py`).
- `docs/guides/code_check/php_complexity.md`, the `docs/guides/code_check.md` index, `docs/agents/architecture.md` and the `README.md` table.

### Tests
- Python unit tests with `docker` mocked, covering the test list in `cli.md`: selection, preflight, pull and container outcomes, parser, reporter, thresholds, flags, `PARSE` rows, empty selection and exit codes.

## Solution
Mirror `python/code_check/js_complexity/`. Only the parser, reporter, flags, constants and skip rules are PHP-specific; everything else comes from `docker_check`.

### Out of scope
- The selection flags (#349), the config section (#350), `--details` (#351) and the `Dup` column (#352).
- Changes to `docker_check` or to the image (#346).
