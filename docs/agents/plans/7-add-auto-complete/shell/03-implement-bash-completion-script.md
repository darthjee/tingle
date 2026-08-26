# Implement bash completion script

Write `completions/tingle.bash`, a bash completion function registered with `complete` for the `tingle` command, so that `tingle <TAB>` completes with available command names.

Behavior:

- Resolve the repo root the same way `bin/tingle` does, so it can locate `commands/*.json` regardless of where the script is sourced from.
- Load command files from `commands/*.json` in alphabetical order (matching `bin/tingle`'s own load order: `node.json`, `python.json`, `shell.json`), and extract top-level keys via `jq -r 'keys_unsorted[]'` (or equivalent) from each.
- Replicate `bin/tingle`'s dedup rule: the first file (alphabetically) to define a given command name wins — do not just union all keys, or a later file's differently-scoped same-named command could wrongly appear as completable.
- Skip a file gracefully (no completions from it, no error/crash) if it is empty (`{}`) or fails to parse as valid JSON (e.g. guard with `jq empty "$file" >/dev/null 2>&1 || continue`).
- Register the completion via `complete -F _tingle_complete tingle` (or equivalent naming) — scope completion to top-level command names only; no argument/flag completion (out of scope for this issue).
- Never `eval`/`source` the JSON content — only read and parse keys via `jq`.
- Must be fast enough to feel instantaneous on TAB; no caching needed given the small number/size of `commands/*.json` files.

## Files to Change

- `completions/tingle.bash` — new file, the completion script described above.
