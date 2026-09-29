# Python Plan: check_file_size: respect .gitignore by default, add --no-gitignore

Main plan: [plan.md](plan.md)

## Shared contracts

- `--no-gitignore`: `{"name": "--no-gitignore", "action": "store_true",
  "help": "Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)"}`,
  placed in `FLAGS` right after `--no-default-excludes`.
- On by default; skips only **untracked** ignored files; silent fallback when
  git is missing, `<path>` is not in a work tree, or git fails.
- Filter order in `FileCollector`: default excludes → `--exclude` →
  **.gitignore** → `--ignore` → `--include` / `--ext` → binary check.
- No config key in this issue (#253 adds `gitignore`).

## Steps

- [01 — Add the git_ignore helper](python/01-add-git-ignore-helper.md)
- [02 — Wire gitignore into FileCollector](python/02-wire-file-collector.md)
- [03 — Add --no-gitignore to the executor and help](python/03-add-flag-and-help.md)

## CI Checks
- `python`: `cd python && ruff check .` (CI job: `lint`)
- `python`: `cd python && pytest` (CI job: `tests`)

## Notes
- `executor.py` already resolves `<path>` (`Path(path).resolve()`), and
  `rglob` yields paths under that resolved root, so joining git's output with
  the same resolved root gives comparable paths. Keep `FileCollector` robust
  for direct callers too: resolve `root` inside `collect()` before calling
  the helper, and compare resolved paths.
- `git ls-files --others --ignored --exclude-standard --directory` reports an
  ignored directory as one `dir/` entry, but when an ignored directory holds a
  tracked file git lists the ignored files individually instead, so tracked
  files are never reported.
- Existing tests use `tmp_path` (outside any repository): the helper returns
  `None` there, so they keep passing unchanged.
- Integration tests that run real git must set a local identity
  (`git -c user.email=... -c user.name=... commit`) or avoid commits by using
  `git add` only (`ls-files` treats staged files as tracked), and must be
  skipped when `shutil.which("git")` is `None`. Also isolate from the
  developer's global excludes (e.g. set `GIT_CONFIG_GLOBAL=/dev/null` via
  `monkeypatch.setenv`) so results are deterministic.
- Codacy/pydocstyle: docstrings start on the first line (D212), matching the
  existing modules.
