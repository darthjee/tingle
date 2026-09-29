# Guide Plan: check_file_size: respect .gitignore by default, add --no-gitignore

Main plan: [plan.md](plan.md)

## Shared contracts

- New flag `--no-gitignore` (default off): turns off the `.gitignore` step.
- By default, when `<path>` is in a git work tree, untracked files git ignores
  are skipped (nested `.gitignore`, `.git/info/exclude`, global excludes).
  Tracked files are always analysed. Without git, or outside a repository,
  nothing is skipped and no warning is shown.
- Single-file `<path>`: skipped when git ignores it. Subdirectory `<path>`:
  parent `.gitignore` rules apply. Only the repository containing `<path>`
  is consulted (not nested repositories or submodules).
- Filter order: default excludes → `--exclude` → .gitignore → `--ignore` →
  `--include` / `--ext` → binary check.

## Implementation Steps

### Step 1 — Add the option to the table and a `--no-gitignore` section
In `docs/guides/check_file_size.md`:
- add a row `| \`--no-gitignore\` | off | Do not skip files ignored by git (see below). |`
  to the Options table, right after `--no-default-excludes`;
- add a `### .gitignore and \`--no-gitignore\`` section after
  `### --no-default-excludes` (before `### --ext`) explaining: on by default,
  which git rules apply, tracked files still analysed, silent fallback without
  git / outside a repo, subdirectory and single-file behaviour, where the step
  sits in the filter order, and examples (`tingle check_file_size .` skipping
  an untracked `debug.log` matched by `*.log`, a force-added `keep.log`
  still analysed, `tingle check_file_size . --no-gitignore`).

### Step 2 — Update the overview, "Skipped files" and Examples
- In "Usage", the directory bullet mentions files ignored by git alongside
  excluded directories and binary files.
- In "Skipped files", the opening sentence lists files ignored by git among
  the things filtered out before the binary check.
- Add a `--no-gitignore` example to the "Examples" section.

## Files to Change
- `docs/guides/check_file_size.md` — Options row, new `.gitignore` /
  `--no-gitignore` section, Usage bullet, "Skipped files" sentence, example.

## Notes
- Match the wording of `long_help` in `commands/python.json` written by the
  python agent, so `tingle check_file_size --help` and the guide agree.
