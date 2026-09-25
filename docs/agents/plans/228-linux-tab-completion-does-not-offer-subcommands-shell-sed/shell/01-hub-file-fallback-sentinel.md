# Add the file-fallback sentinel to the completion hub
In `_tingle_complete_command_args`, when `completion.<ext>` exists, first capture the handler output: `local out; out="$("$main_path" complete "${COMP_WORDS[@]:2}")"`. If the trimmed output is exactly `__tingle_files__`, use the same branch as the generic fallback (`compgen -f -- "$cur"` plus `compopt -o filenames 2>/dev/null || true`). Otherwise keep `COMPREPLY=($(compgen -W "$out" -- "$cur"))`.

Define the sentinel once, for example as a local or file-level variable next to a short comment, and don't duplicate the fallback lines (a small helper function is fine). Update the header comment so it describes the sentinel. Existing handlers (`kube`) never print the sentinel, so their behaviour doesn't change.

## Files to Change
- `completions/bash/commands.sh` — recognise the `__tingle_files__` sentinel and route it to the native file/folder fallback.
