# Add the subcommand executor

Create `shell/linux/executor.sh`, the `tingle linux` subcommand router. It
mirrors `python/kube/executor.py`'s `_handlers` map pattern, adapted to
Bash: read the subcommand name from `$1`, dispatch via a `case` statement to
a per-subcommand handler function, and source `docker_run.sh` for the
handlers to call.

```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./docker_run.sh
source "$SCRIPT_DIR/docker_run.sh"

_handle_shell() {
    echo "tingle linux shell: not implemented yet (see issue #37)"
    exit 1
}

_handle_sed() {
    echo "tingle linux sed: not implemented yet (see issue #38)"
    exit 1
}

subcommand="${1:-}"
[ -n "$subcommand" ] && shift

case "$subcommand" in
    shell)
        _handle_shell "$@"
        ;;
    sed)
        _handle_sed "$@"
        ;;
    *)
        echo "tingle linux: unknown subcommand '$subcommand'" >&2
        exit 1
        ;;
esac
```

The stub handlers exist to prove the dispatch wiring end-to-end (per the
discussion's confirmed answer) — they are replaced with real behavior in
#37 (`shell`) and #38 (`sed`), which will also start calling `docker_run`
from `docker_run.sh` (already sourced here).

## Files to Change
- `shell/linux/executor.sh` (new) — subcommand router with `shell`/`sed`
  stub handlers, sourcing `docker_run.sh`.
