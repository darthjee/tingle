# Plan: check_file_size: respect .gitignore by default, add --no-gitignore

Issue: [251-check-file-size-respect-gitignore-by-default-add-no-gitignore.md](../../issues/251-check-file-size-respect-gitignore-by-default-add-no-gitignore.md)

## Overview
`tingle check_file_size` starts skipping untracked files that git ignores,
by default, when `<path>` is inside a git work tree. The python agent adds a
`git_ignore.py` helper (one `git ls-files` call per run), wires it into
`FileCollector` as filter step 3, and adds `--no-gitignore`. The guide agent
documents the flag and the new skip rule. The normative contract is
[`docs/agents/specs/check_file_size/gitignore.md`](../../specs/check_file_size/gitignore.md)
plus the shared [`README.md`](../../specs/check_file_size/README.md).

## Agents involved

- [python](python.md)
- [guide](guide.md)

## Shared contracts

- Flag: `--no-gitignore`, `store_true`, default off. Help text:
  `Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)`.
- Behaviour (on by default): when `<path>` is in a git work tree, **untracked**
  files that git ignores are skipped, following nested `.gitignore`,
  `.git/info/exclude` and `core.excludesFile`. Tracked files are always
  analysed, even when they match a pattern.
- Silent fallback: git not installed, `<path>` outside a work tree, or any git
  failure → nothing is skipped by git, no output, exit code unchanged.
- Single-file `<path>`: git runs from its parent; the file is skipped when
  ignored. Subdirectory `<path>`: parent `.gitignore` rules still apply.
  An ignored directory skips every file under it. Only the repository that
  contains `<path>` is consulted.
- Filter order: default excludes → `--exclude` → **.gitignore** → `--ignore`
  → `--include` / `--ext` → binary check.
- The config key `gitignore` is **not** part of this issue (#253).
