# Write the shared-contracts README
Create `docs/agents/specs/check_file_size/README.md`, the single source of truth for everything used by more than one sub-issue.

Sections:
1. **Overview**: goal of #247, links to each feature spec and its sub-issue:
   - `ignore-include.md` → #249
   - `exclude.md` → #250
   - `gitignore.md` → #251
   - `min-level.md` → #252
   - `config.md` → #253
   - cleanup → #254
2. **Merge order**: #249 → #250 → #251 (all change `FileCollector`, so merge them one after another to avoid rebase churn). #252 is independent. #253 goes after #249–#252. #254 goes last.
3. **Flags** (table: flag, type, repeatable, default, config key):
   - `--ignore <glob>`: str, repeatable, `[]`, `ignore`
   - `--include <glob>`: str, repeatable, `[]`, `include`
   - `--exclude <a,b>`: comma-separated str, adds to the defaults, `exclude` (list)
   - `--no-default-excludes`: store_true, `no_default_excludes` (bool)
   - `--no-gitignore`: store_true, `gitignore` (bool, default `true`, inverted)
   - `--min-level ok|warn|error|critical`: default `ok`, `min_level`
   - Existing flags mapped too: `warn`, `error`, `critical`, `top` (int), `ext` (list), `fail_on` (str or null)
4. **Precedence**: built-in defaults < config < CLI for single values. For list keys (`exclude`, `ignore`, `include`, `ext`), the config list and CLI list are concatenated (deduplicated, order kept). Boolean flags on the CLI can only turn behaviour *off* (`--no-*`), and the config may set either value.
5. **Filter pipeline in `FileCollector`** (in order): default excludes (unless `no_default_excludes`) → `--exclude` names → `.gitignore` (unless disabled) → `--ignore` globs → `--include` globs **and** `--ext` (both must match when both are given) → binary check. A single-file `<path>` goes through the same steps: globs match its file name, and path-component excludes do not apply to it.
6. **Display vs counting**: `--min-level` is applied first, then `--top`. Neither changes the summary counts or the `--fail-on` gate, which always use every collected file.
7. **Exit codes & streams**: unchanged. 0 ok, 1 error (bad option/value, path not found, config error), 2 gate failed. Errors go to stderr.
8. **Docs per sub-issue**: each of #249–#253 updates `docs/guides/check_file_size.md` (`guide` agent), `long_help` in `commands/python.json`, and tests under `python/tests/check_file_size/`.

## Files to Change
- `docs/agents/specs/check_file_size/README.md` — new.
