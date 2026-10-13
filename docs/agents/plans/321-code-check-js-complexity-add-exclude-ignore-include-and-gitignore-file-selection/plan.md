# Plan: code_check js_complexity: add --exclude/--ignore/--include and .gitignore file selection

Issue: [321-code-check-js-complexity-add-exclude-ignore-include-and-gitignore-file-selection.md](../../issues/321-code-check-js-complexity-add-exclude-ignore-include-and-gitignore-file-selection.md)

## Overview
Add `--exclude`, `--no-default-excludes`, `--no-gitignore`, `--ignore` and `--include` to `tingle code_check js_complexity`. The plumbing is already in place: `DockerCheck._merge` resolves these five options and `DockerCheck._selection_options` turns them into `select_files` arguments, and `js_complexity.selection.select_files` accepts them. The work is to declare the flags, which are copied from `rubycritic/flags.py` as the user chose (no shared helper); remove #320's stopgap `_selection_options` override; set `LIST_KEYS`; and update the tests, `long_help` and the guide. Spec: [file-selection.md](../../specs/code_check/js_complexity/file-selection.md).

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

**Flags** (in `python/code_check/js_complexity/flags.py`, after `--image`, in this order, with `rubycritic`'s shapes):

| Flag | argparse | dest | Help text |
|------|----------|------|-----------|
| `--exclude` | `type=str`, `default=None` (store) | `exclude` | `Extra directory names to skip (comma-separated), added to the defaults: <','.join(Constants.DEFAULT_EXCLUDES)>` |
| `--no-default-excludes` | `store_true` | `no_default_excludes` | `Do not skip the default directories; only --exclude names apply` (#323 adds the minified part later) |
| `--no-gitignore` | `store_true` | `no_gitignore` | `Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)` |
| `--ignore` | `type=str`, `action=append`, `default=None` | `ignore` | `Skip files whose path relative to <path> matches this glob (can be repeated)` |
| `--include` | `type=str`, `action=append`, `default=None` | `include` | `Only analyse JavaScript/TypeScript files whose path relative to <path> matches this glob (can be repeated)` |

There is no `--ext` and no `--no-config` (#322 adds that one).

Resulting completion flag order: `--warn --error --critical --top --min-level --fail-on --image --exclude --no-default-excludes --no-gitignore --ignore --include`.

**Behaviour** (spec sections 3, 5, 6 and 7):
- Filter order: default excludes, then `--exclude`, then gitignore, then `--ignore`, then `--include` together with the extensions, then declaration files, then symlink confinement.
- gitignore is **on by default**.
- For a single-file `<path>`, the directory excludes don't apply and the globs match the file name.
- Nothing is printed for gitignore, including when git is missing.

**Merging:** a second `--exclude` replaces the first. `--ignore` and `--include` values are deduplicated, keeping their order.
