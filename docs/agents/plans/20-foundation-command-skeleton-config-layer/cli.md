# cli Plan: Foundation: command skeleton + config layer

Main plan: [plan.md](plan.md)

## Shared contracts

- Adds a `"kube"` entry to `commands/python.json` pointing at `path: "python/kube/main.py"` — that file is created by `python`'s work; this entry must reference it by that exact path.
- The dispatcher (`bin/tingle`) needs no changes: it already resolves any command listed in `commands/*.json` generically (see `find_command_index`/the final `exec` in `bin/tingle`) and always invokes `<path> run <args...>`.

## Implementation Steps

### Step 1 — Register `kube` in the command mapping
Add a `"kube"` key to `commands/python.json`, following the existing `"check_file_size"` entry's shape (`path`, `short_help`, `long_help`). Point `path` at `python/kube/main.py`. Write `short_help` as a one-line summary (e.g. "Kubernetes (EKS) subcommand with a scoped alias layer.") and `long_help` covering the command surface from the parent epic (`switch`, `list namespace`, `list pods`, `shell`, `configure context|namespace|pod`), matching the level of detail `check_file_size`'s `long_help` has (usage + examples). No behavior needs to work yet beyond dispatch — `python`'s stubs handle that — but the help text should describe the intended full surface so `tingle kube --help` and `tingle --help` are useful immediately once this lands.

## Files to Change
- `commands/python.json` — add the `"kube"` entry (`path`, `short_help`, `long_help`).

## Notes
- No `bin/tingle` changes are needed — it dispatches to any command registered in `commands/*.json` generically; only the mapping file changes.
- This step has no dependency ordering relative to `python`'s work at the file level (JSON registration doesn't require `python/kube/main.py` to exist to be valid JSON), but the command won't actually run correctly until `python`'s Step 1 (package scaffold) lands — coordinate merge order or land both in the same PR.
