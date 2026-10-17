# Issue: code_check php_complexity: add --exclude/--ignore/--include and .gitignore file selection

## Description
Add the host-side file selection flags to `tingle code_check php_complexity` (parent #344): `--exclude`, `--no-default-excludes`, `--ignore`, `--include` and `--no-gitignore`. They go through `docker_check`'s shared selection (`docker_check.selection.select_files` → `file_size`'s `FileCollector`), with the same names, argparse style and meaning as in `js_complexity`.

**Normative spec:** `docs/agents/specs/code_check/php_complexity/selection.md` (with the shared contracts in `README.md`). Where this body and the spec disagree, the spec wins.

Depends on #348 (subcommand core, merged).

## Problem
#348 shipped the subcommand with a fixed selection: `CheckPhpComplexity._selection_options` always returns the default excludes, no globs, `gitignore=False` and `skip_bootstrap_cache=True`. Users cannot narrow or widen what is analysed (e.g. skip tests, analyse `vendor/`), and files ignored by git are analysed.

## Expected Behavior
- `--exclude a,b`: extra directory names, **comma-separated**, added to the default excludes (merged after the defaults and deduplicated via `code_check.excludes.resolve_excludes`). Blank entries are dropped. Not repeatable: a second `--exclude` replaces the first (argparse `store`).
- `--no-default-excludes`: drops the 16 default excludes (`file_size`'s list plus `var`, `storage`, `.phpunit.cache`) **and** the `bootstrap/cache` skip rule; only `--exclude` names apply. `bootstrap/cache` is a skip rule, not an exclude name, so `--exclude bootstrap/cache` matches nothing.
- `--ignore GLOB` (repeatable, `append`): skip files whose path relative to `<path>` matches.
- `--include GLOB` (repeatable, `append`): keep only files matching at least one include glob; combined with the `.php` extension (both must match).
- `.gitignore` is honoured by default (one `git ls-files --others --ignored --exclude-standard --directory -z` call on the host; tracked files always kept; silently off without git or outside a work tree). `--no-gitignore` turns it off.
- Blade templates (`*.blade.php`, any case) stay skipped whatever the flags are; `--include '**/*.blade.php'` selects nothing.
- Filter order (first rejecting step wins): default excludes → `--exclude` → `.gitignore` → `--ignore` → `--include` + extension → skip rules (Blade, then `bootstrap/cache`) → symlink confinement. For a single-file `<path>`, the directory excludes and the `bootstrap/cache` rule do not apply.
- There is no `--ext`.

### Out of scope
- The config file keys for these flags (#350).

## Solution
- `python/code_check/php_complexity/flags.py`: add the five flags with the help texts from `selection.md` §1.
- `python/code_check/php_complexity/executor.py`: replace the placeholder `_selection_options` with `super()._selection_options(options)` plus `skip_bootstrap_cache = not bool(options.get("no_default_excludes"))`, the way `CheckJsComplexity` sets `skip_minified`.
- `commands/python.json`: update the `php_complexity` `long_help` file-selection block (listing the Blade and `bootstrap/cache` rules).
- Completion: `--exclude`, `--ignore`, `--include` take free-form values.
- `docs/guides/code_check/php_complexity.md`: document the flags (including `--ignore` for tests).
- Tests under `python/tests/code_check/php_complexity/` for each case listed in `selection.md` §9. `file_size`'s, `rubycritic`'s and `js_complexity`'s selection tests must still pass unchanged.

## Benefits
- Parity with `file_size`, `rubycritic` and `js_complexity` file selection.
- Lets users drop noisy files (tests, generated code) and respect `.gitignore`, which changes the score and the `--fail-on` gate.
