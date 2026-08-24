# Register tingle in README and document the trust model

Per `cli.md`'s existing convention ("New entry points are registered in the table in README.md"):

1. Add a row to the `Scripts` table in `README.md` for the new hub:
   | Script | Language | Description |
   | --- | --- | --- |
   | `tingle` | Shell | CLI hub — dispatches `tingle <command> [args...]` to the matching script under `python/`, `node/`, or `shell/` via `commands/*.sh` mappings. |

2. Add a short note (e.g. under "Structure" or a new "Commands" subsection) documenting that `commands/*.sh` files are sourced as trusted shell code, not sandboxed data — anyone who can write to `commands/` can execute arbitrary code via `bin/tingle`, per the issue's Performance & Security decision.

## Files to Change

- `README.md` — add the `tingle` row to the Scripts table; add the `commands/*.sh` trust-model note.
