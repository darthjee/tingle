# cli Plan: Add tingle hub

Main plan: [plan.md](plan.md)

## Shared contracts

- Must produce `commands/python.sh` with `check_file_size="python/check_file_size.py"`, matching exactly the path the `python` agent relocates the script to.

## Steps

- [01 — Create the bin/tingle CLI hub](cli/01-create-bin-tingle.md)
- [02 — Create the commands/ mapping directory](cli/02-create-commands-dir.md)
- [03 — Extend cli agent's own scope to commands/](cli/03-update-cli-agent-scope.md)
- [04 — Register tingle in README and document the trust model](cli/04-update-readme-cli.md)

## Notes

- No `eval`/`$*` anywhere in the dispatch path — see step 01 for the exact indirect-expansion mechanism decided in the issue.
- `commands/*.sh` files are sourced as trusted shell code, not sandboxed — see step 04 for where this gets documented.
