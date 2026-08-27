# Prepend flow verb and add resolve helper to bin/tingle

`bin/tingle` currently execs the resolved command path directly with the raw
user args (`exec "$TINGLE_FOLDER/${command_paths[$index]}" "$@"`). Adopt the
flow verb protocol (shared contract 1) by prepending `run` unconditionally,
and add a `tingle resolve <cmd>` meta-command (shared contract 5) so the
completion hub has a single source of truth for command-to-script
resolution instead of re-parsing `commands/*.json` itself.

Add the `resolve` handling alongside the existing `help`/`--help` special
cases (before the final dispatch block):

```bash
if [ "$1" = "resolve" ] && [ $# -eq 2 ]; then
    command_name="$2"
    index="$(find_command_index "$command_name")"
    if [ -z "$index" ]; then
        command_not_found "$command_name"
    fi
    echo "$TINGLE_FOLDER/${command_paths[$index]}"
    exit 0
fi
```

Update the final dispatch to prepend the flow verb:

```bash
command_name="$1"
index="$(find_command_index "$command_name")"
if [ -z "$index" ]; then
    command_not_found "$command_name"
fi
shift

exec "$TINGLE_FOLDER/${command_paths[$index]}" "run" "$@"
```

## Files to Change

- `bin/tingle` — add `resolve` meta-command; prepend `run` on the final dispatch `exec`.
