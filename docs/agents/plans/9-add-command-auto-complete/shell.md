# Shell Plan: Add command auto complete

Main plan: [plan.md](plan.md)

## Shared contracts

- Must produce `shell/install/main.sh`, matching contract 1 (flow verb protocol) and contract 2 (`cli` will point `commands/shell.json`'s `install.path` at this exact file).
- No `completion.sh` is added for `install` (contract 3) — falls through to `cli`'s generic file/folder fallback (an accepted UX quirk since `install` takes no args). `main.sh` therefore only needs to handle the `run` verb.

## Implementation Steps

### Step 1 — Move `install.sh` under `shell/install/` and split into `executor.sh` + `main.sh`

Move the existing `shell/install.sh` body to `shell/install/executor.sh`, unchanged except:

- `TINGLE_FOLDER="$(cd "$(dirname "$0")/.." && pwd)"` becomes `TINGLE_FOLDER="$(cd "$(dirname "$0")/../.." && pwd)"` — the script is now two directories below the repo root (`shell/install/executor.sh`) instead of one (`shell/install.sh`).

Create `shell/install/main.sh` as the new entrypoint that `commands/shell.json` will point at:

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
flow="$1"
shift

case "$flow" in
    run)
        exec "$SCRIPT_DIR/executor.sh" "$@"
        ;;
esac
```

No `complete` case is needed — `install` ships no `completion.sh`, so `cli`'s hub never calls `main.sh complete` for it (see shared contract 3).

Delete `shell/install.sh`.

## Files to Change

- `shell/install.sh` — removed.
- `shell/install/executor.sh` — new, holds the former `install.sh` body with the adjusted `TINGLE_FOLDER` path (one more `..`).
- `shell/install/main.sh` — new dispatcher entrypoint (flow verb protocol).

## Notes

- No lint/check command is configured for `shell/` yet (per `docs/agents/todo.md`) — nothing to run beyond manual verification (`tingle install` still idempotently appends to `~/.bashrc`).
- Double-check `README.md`'s command table, if it references `shell/install.sh` by path, needs the new path — flag to `product-owner`/`architect` if found, since `README.md` is a root-level file outside both `shell`'s and `product-owner`'s scope.
