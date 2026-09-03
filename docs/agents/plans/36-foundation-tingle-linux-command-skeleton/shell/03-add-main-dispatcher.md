# Add the main.sh dispatcher

Create `shell/linux/main.sh`, the flow-verb entrypoint dispatcher, following
`shell/install/main.sh`'s exact shape: reads the flow verb (`run`) from
`$1`, forwards the rest of argv to `executor.sh`. No `complete` case — this
issue adds no `completion.sh` (out of scope).

```bash
#!/usr/bin/env bash
#
# main.sh - Entrypoint dispatcher for the `linux` command (flow-verb protocol).
#
# Usage:
#   main.sh run <subcommand> [args...]
#
# Dependencies: executor.sh in the same directory.
#
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

## Files to Change
- `shell/linux/main.sh` (new) — flow-verb dispatcher forwarding `run` to
  `executor.sh`.
