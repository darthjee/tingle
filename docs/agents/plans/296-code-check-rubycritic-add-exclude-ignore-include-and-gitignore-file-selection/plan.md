# Plan: code_check rubycritic: add --exclude/--ignore/--include and .gitignore file selection

Issue: [296-code-check-rubycritic-add-exclude-ignore-include-and-gitignore-file-selection.md](../../issues/296-code-check-rubycritic-add-exclude-ignore-include-and-gitignore-file-selection.md)

Spec (source of truth): [file-selection.md](../../specs/code_check/rubycritic/file-selection.md)

## Overview

Add `file_size`'s file selection flags (`--exclude`, `--no-default-excludes`,
`--no-gitignore`, `--ignore`, `--include`) to `tingle code_check rubycritic`,
reusing `FileCollector` directly. `FileCollector` gains a keyword-only
`outside_symlinks` argument (default `True`, unchanged for `file_size`) so
rubycritic can drop files that resolve outside the mount root. Kept symlinks are
sent as their target's relative path, deduplicated by resolved path. The help
text and the user guide are updated in the same PR.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

Flags (names, types, help texts) defined in `python/code_check/rubycritic/flags.py`,
which `long_help` and the guide must describe identically:

| Flag | argparse | Default | Help |
|------|----------|---------|------|
| `--exclude` | `type=str`, store (not repeatable; last wins) | `None` | `Extra directory names to skip (comma-separated), added to the defaults: <16 names joined by ,>` |
| `--no-default-excludes` | `store_true` | `False` | `Do not skip the default directories; only --exclude names apply` |
| `--no-gitignore` | `store_true` | `False` | `Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)` |
| `--ignore` | `type=str`, `append` | `None` | `Skip files whose path relative to <path> matches this glob (can be repeated)` |
| `--include` | `type=str`, `append` | `None` | `Only analyse .rb files whose path relative to <path> matches this glob (can be repeated)` |

Default excludes (16, in order): `node_modules, dist, build, .git, vendor,
third_party, .next, __pycache__, .cache, coverage, .nuxt, out, target, tmp, log, .bundle`.

Behaviour to document:

- Filter order: (1) default excludes, (2) `--exclude`, (3) `.gitignore`,
  (4) `--ignore`, (5) `--include` + `.rb`, (6) symlink confinement. First
  rejecting step drops the file.
- `.gitignore` on by default when `<path>` (or a single file's parent) is in a
  git work tree; tracked files always kept; git missing/failing → nothing
  skipped, nothing printed; runs on the host only.
- Symlinks resolving outside the mount root, or dangling, are skipped silently;
  a kept symlink is analysed and displayed as its target; a symlink and its
  target count once; directory symlinks are not walked.
- Single-file `<path>`: excludes do not apply; globs match the file name.
- No `--ext`; no binary check (non-UTF-8 `.rb` files still reach the image as `PARSE` rows).
- Exit codes do not change.
