# Update the executor header comment
Rewrite the header of `shell/update/executor.sh` so it describes both install kinds. The file summary line currently says "Updates a web install". The Inputs section should note that `<version>`/`TINGLE_VERSION` and `--force` are refused on a git checkout, and that `--check` means fetch plus behind/ahead there. Flow step 1 should describe the git path's checks, fetch, `pull --ff-only` and `exec bin/tingle install`. Also update the Exit codes and Dependencies (`git` for git checkouts; `curl`, `unzip` and `jq` only for web installs). Keep the existing style.

## Files to Change
- `shell/update/executor.sh` — header comment only.
