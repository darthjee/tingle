# Complete --all in bash completion

- `_scan`: recognize `--all` as a boolean flag (`flags["all"] = True`, reset
  `pending_flag`), like `--json`, so it is never treated as a positional and
  `--namespace` alias completion keeps working when `--all` comes first.
- `complete` → `_complete_list`: pass `flags` through; when positionals are
  `["pods"]`, return `["--namespace", "--all"]`, omitting `--all` when it was
  already typed (keep `--namespace` offered as today).
- Update the module docstring's list of tolerated flags to include `--all`.

## Files to Change

- `python/kube/completion.py` — `_scan`, `complete`, `_complete_list`,
  module docstring.
- `python/tests/kube/test_completion.py` — `list pods ` offers `--namespace`
  and `--all`; `list pods --all ` offers only `--namespace`;
  `list pods --all --namespace ` completes namespace aliases;
  `list pods --namespace web ` still offers `--all`.
