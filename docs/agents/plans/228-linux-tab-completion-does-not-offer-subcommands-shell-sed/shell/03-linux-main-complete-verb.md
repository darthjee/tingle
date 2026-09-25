# Add the complete flow verb to shell/linux/main.sh
Add a `complete)` branch to the `case "$flow"` in `shell/linux/main.sh` that runs `exec "$SCRIPT_DIR/completion.sh" "$@"`. Update the usage line in the header comment to show `main.sh complete [args...]`.

`flow="$1"` fails under `set -u` if there are no arguments. The hub always passes a flow verb, so that is fine, but check that an empty trailing argument (`main.sh complete sed ""`) is forwarded as-is.

## Files to Change
- `shell/linux/main.sh` — add the `complete` flow verb.
