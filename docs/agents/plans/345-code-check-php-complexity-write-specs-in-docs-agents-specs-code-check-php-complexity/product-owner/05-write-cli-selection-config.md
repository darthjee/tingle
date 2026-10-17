# Write cli.md, selection.md and config.md
**`docs/agents/specs/code_check/php_complexity/cli.md` (#348):**
- **Package:** the `python/code_check/php_complexity/` module list, following `js_complexity/`, and what each module takes from `docker_check`.
- **Constants:** the values for thresholds, extensions, excludes and `IMAGE_REPO`.
- **Parser:** the JSON → rows mapping.
- **Reporter:**
  - the exact header lines and the column set (`Status`, `CCN`, `Max`, `NPath`, `MI` or its documented drop, `Lines`, `File`), with widths and formatting;
  - the sort order and tie-break;
  - the summary lines, including `CCN: avg X | max Y` and the skipped count.
- **Flags:** `--warn/--error/--critical` validation, `--top`, `--min-level`, `--fail-on` and `--image`.
- **`PARSE` rows** and the exit codes.
- **Registration:** `SUBCOMMAND_NAMES`/`SUBCOMMANDS`, `long_help`, `commands/python.json` and completion.
- **Docs to update:** the guide, the `code_check.md` index, `architecture.md` and the README table.
- **Test list**, with `docker` mocked.

**`docs/agents/specs/code_check/php_complexity/selection.md` (#349):** the `--exclude`/`--no-default-excludes`, `--ignore`, `--include` and `--no-gitignore` semantics; the filter order from README §6; the Blade skip surviving every flag; and the test cases.

**`docs/agents/specs/code_check/php_complexity/config.md` (#350):** the `php_complexity` `SCHEMA` built from `code_check.validators`; precedence and list merging; `--no-config`; the exact error messages for invalid JSON, unknown keys (including `ext`) and wrong types; the example config; and the test cases.

## Files to Change
- `docs/agents/specs/code_check/php_complexity/cli.md`: new.
- `docs/agents/specs/code_check/php_complexity/selection.md`: new.
- `docs/agents/specs/code_check/php_complexity/config.md`: new.
