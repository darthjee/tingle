# Issue: code_check php_complexity: per-method complexity drill-down (--details)

## Description
Add a per-method complexity drill-down, `--details [N]`, to `tingle code_check php_complexity` (parent #344). Under each shown file it lists the file's `N` most complex functions and methods by PDepend CCN, with the same semantics as `rubycritic --details` (#291) and `js_complexity --details` (#325).

**Normative spec:** `docs/agents/specs/code_check/php_complexity/details.md` (with `image.md` for the XML → JSON mapping and the smoke-test fixture). Where this issue and the spec disagree, the spec wins.

Dependencies #347 (release pipeline) and #350 (config section) are already merged.

## Problem
The image built in #346 emits `"functions": null` on every file entry, and the CLI has no way to show which methods drive a file's CCN. To find the hot spot in a file flagged `ERROR`/`CRITICAL`, users have to open the file and work it out by hand.

## Expected Behavior
**Image (`docker/php_complexity/`)**
- `files[].functions` is filled from the same PDepend run (no new tool, options or report, and `tool_versions` stays the same). Each entry is `{name, line, ccn, npath}`, in source order.
- Units are every method of a `class`/`trait` (`Class::method`, short name) and every `function` (short name) that has a `file` child. Closures, arrow functions, enum methods, bare anonymous-class methods and interface methods are not listed. Abstract methods are listed with `ccn` 1.
- `[]` for an analysed file with no counted unit (including `pdepend: null` files such as `bootstrap.php` and `empty.php`); `null` for parse errors and refused lines.
- `sum(ccn) == pdepend.ccn` for every analysed file.
- The smoke test asserts the `functions` column of the fixture table. The Docker Hub description and `docs/agents/tingle-php-complexity-image.md` mention the per-function data.

**CLI (`python/code_check/php_complexity/`)**
- `--details [N]` (`nargs="?"`, `const=5`, default off). `--details 0` lists all units. A negative value gives `Error: --details must be an integer >= 0`, exit 1. `DEFAULT_DETAILS = 5` goes in `constants.py`.
- Under each **shown** level row (after `--min-level`/`--top`), never under `PARSE`, units are sorted by `ccn` desc, then `line` asc, then `name`, and the first `N` are kept. Each unit is one dim line:
  `                 ccn   7  npath      36  Calculator::grade  (fixture/Calculator.php:22)`
- `functions: null` on a level row prints the dim line `(per-function data unavailable)`, and `[]` prints nothing. Neither changes the level or the exit code. The summary and the gate are unchanged.
- The `details` config key (`nullable_non_negative_int`) goes into `SCHEMA` and `SINGLE_DEFAULTS` of the `php_complexity` section, with precedence built-in `null` < config < CLI.
- `long_help`, completion (`--details` takes a free-form value), `docs/guides/code_check/php_complexity.md` and the Python unit tests (as listed in spec §7) are updated.

## Solution
The image change and the Python change land **in the same PR**, so the CLI and the image stay in sync. Owners: `shell` for the image (`entrypoint.php`, `lib/pdepend.php`, smoke test, image docs), `python` for the CLI, config, reporter and tests, and `guide` for the user guide. `tpc_summarize` already walks the counted units to compute `ccn`/`max_ccn`/`max_npath`, so `functions` can be collected in the same pass.

## Benefits
- Points straight at the methods to refactor in a flagged file.
- Consistent `--details` behaviour across `rubycritic`, `js_complexity` and `php_complexity`.
