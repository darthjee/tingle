# Create the bin/tingle CLI hub

Create `bin/tingle`, executable (`chmod +x`), implementing:

1. **`TINGLE_FOLDER` discovery** — resolve the repo root from the script's own location, independent of ambient cwd:
   ```bash
   TINGLE_FOLDER="$(cd "$(dirname "$0")/.." && pwd)"
   ```

2. **Loading mappings** — source every file in `commands/`, guarding against an empty/missing directory so an unexpanded glob doesn't get sourced literally:
   ```bash
   shopt -s nullglob
   cmd_files=("$TINGLE_FOLDER/commands/"*.sh)
   if [ ${#cmd_files[@]} -eq 0 ]; then
       echo "Error: no command mapping files found in $TINGLE_FOLDER/commands/" >&2
       exit 1
   fi
   for cmd_file in "${cmd_files[@]}"; do
       source "$cmd_file"
   done
   ```

3. **No-arguments case** — print usage and exit 1 before attempting any lookup:
   ```bash
   if [ $# -eq 0 ]; then
       echo "Usage: tingle <command> [args...]" >&2
       exit 1
   fi
   ```

4. **Dispatch via indirect parameter expansion** — no `eval`, no `$*`:
   ```bash
   path="${!1}"
   if [ -z "$path" ]; then
       echo "Error: command '$1' not found." >&2
       echo "Available commands: ..." >&2   # see "available commands" below
       exit 1
   fi
   shift
   "$TINGLE_FOLDER/$path" "$@"
   ```
   Missing/non-executable target scripts are **not** pre-checked — let the shell's own exec error surface (e.g. "No such file or directory" / "Permission denied"), per the issue's Edge Cases decision.

5. **Listing available commands on the not-found error** — since mappings are loaded as plain shell variables (not an associative array), track the list of command names as they're sourced (e.g. accumulate `${cmd_file##*/}`-derived names, or grep `^\w+=` out of each sourced file) so the error message can print something like `Available commands: check_file_size`.

## Files to Change

- `bin/tingle` — new file, the CLI hub described above.
