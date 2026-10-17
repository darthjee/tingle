# Plan: code_check php_complexity: add --exclude/--ignore/--include and .gitignore file selection

Issue: [349-code-check-php-complexity-add-exclude-ignore-include-and-gitignore-file-selection.md](../../issues/349-code-check-php-complexity-add-exclude-ignore-include-and-gitignore-file-selection.md)

## Overview
Add the five `js_complexity`-style selection flags (`--exclude`, `--no-default-excludes`, `--no-gitignore`, `--ignore`, `--include`) to `tingle code_check php_complexity`. Most of the plumbing already exists: `DockerCheck._merge` and `DockerCheck._selection_options` handle these keys, and `php_complexity.selection.select_files` already accepts `excludes`, `ignore`, `include`, `gitignore` and `skip_bootstrap_cache`. The work is mainly declaring the flags, swapping the placeholder `_selection_options` for the base one, then updating the help, the guide and the tests. The normative spec is `docs/agents/specs/code_check/php_complexity/selection.md`.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

Flags (from `selection.md` §1 and README §3), all in `python/code_check/php_complexity/flags.py`, inserted after `--image`, in this order:

| Flag | argparse | Dest | Help text |
|------|----------|------|-----------|
| `--exclude a,b` | `type=str`, `default=None` (store) | `exclude` | `Extra directory names to skip (comma-separated), added to the defaults: <','.join(Constants.DEFAULT_EXCLUDES)>` |
| `--no-default-excludes` | `store_true` | `no_default_excludes` | `Do not skip the default directories or bootstrap/cache; only --exclude names apply` |
| `--no-gitignore` | `store_true` | `no_gitignore` | `Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)` |
| `--ignore GLOB` | `type=str`, `action=append`, `default=None` | `ignore` | `Skip files whose path relative to <path> matches this glob (can be repeated)` |
| `--include GLOB` | `type=str`, `action=append`, `default=None` | `include` | `Only analyse PHP files whose path relative to <path> matches this glob (can be repeated)` |

Behaviour that the help and the guide must describe:

- `--exclude` adds to the 16 default excludes (`node_modules, dist, build, .git, vendor, third_party, .next, __pycache__, .cache, coverage, .nuxt, out, target, var, storage, .phpunit.cache`). Blank entries are dropped, and a second `--exclude` replaces the first.
- `--no-default-excludes` drops those defaults **and** the `bootstrap/cache` rule. Blade templates (`*.blade.php`, any case) are always skipped, and `--include` never brings one back.
- `.gitignore` is on by default and `--no-gitignore` turns it off. Tracked files are always kept. Without git, or outside a work tree, nothing is skipped and nothing is printed.
- `--ignore`/`--include` take `.gitignore`-style globs, case-insensitive, matched against the path relative to `<path>` (the file name, for a single file). `--ignore` wins over `--include`.
- Filter order: default excludes → `--exclude` → `.gitignore` → `--ignore` → `--include` + `.php` → Blade, then `bootstrap/cache` → symlink confinement. For a single-file `<path>`, the directory excludes and the `bootstrap/cache` rule do not apply.
- There is no `--ext`. There is no `--no-config` and no config section either: those come with #350.
