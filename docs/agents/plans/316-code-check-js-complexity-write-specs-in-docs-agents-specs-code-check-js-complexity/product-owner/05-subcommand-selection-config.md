# subcommand.md, file-selection.md, config.md
**`docs/agents/specs/code_check/js_complexity/subcommand.md`** (#320) covers:
- the preflight and the `docker run` line, through `docker_check`;
- merged-JSON parsing and path mapping;
- the report: the columns `Status/FTA/Cyclo/Lines/Assessment/File` (with `Dup` reserved for #324), sorting, `⛔ PARSE` rows, and the summary with `FTA score: avg X | max Y`;
- the thresholds `50/60/75`, confirmed against the bands from step 01;
- `--top`, `--min-level`, `--fail-on` and `--image`;
- exit codes;
- every edge case from #315 plus the additional ones;
- the **exact message texts**;
- the registration (`SUBCOMMAND_NAMES`, `SUBCOMMANDS`, `long_help`, `commands/python.json`, completion).

**`docs/agents/specs/code_check/js_complexity/file-selection.md`** (#321, #323) covers:
- the extensions, matched regardless of case, with `.d.ts/.d.mts/.d.cts` skipped;
- the default excludes;
- `--exclude`/`--no-default-excludes`, `--ignore`, `--include` and `.gitignore`/`--no-gitignore`;
- symlinks, single-file targets and the filter order;
- the **minified section**: `*.min.js/.mjs/.cjs` is a default exclude, `--include` never brings those files back, and only `--no-default-excludes` (or the config key) turns the skip off.

**`docs/agents/specs/code_check/js_complexity/config.md`** (#322) covers:
- the `js_complexity` `SCHEMA` built from `code_check.validators`, with `details` added by #325 and no `ext`;
- precedence, list merging, errors (reusing `file_size`'s wording) and `--no-config`;
- the compatibility invariant that existing config files stay valid;
- an example.

## Files to Change
- `docs/agents/specs/code_check/js_complexity/subcommand.md` — new.
- `docs/agents/specs/code_check/js_complexity/file-selection.md` — new.
- `docs/agents/specs/code_check/js_complexity/config.md` — new.
