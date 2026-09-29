# Scaffold shell/update/ and the executor header
Create `shell/update/main.sh`, a copy of `shell/uninstall/main.sh` with its
header comment pointing at the `update` command. Create
`shell/update/executor.sh` (executable, `#!/usr/bin/env bash`,
`set -euo pipefail`) with a header comment that is the permanent home of the
spec (its section 8): purpose (a thin command that hands off to the new
release's installer), usage and inputs, the flow in order (detect, resolve,
up to date / `--check`, confirm, download and verify, hand off), rule S1 (no
trap, `exec` last, the installer cleans up via `TINGLE_UPDATE_CLEANUP=1`), the
exit codes, and the **test-only** hooks `TINGLE_RELEASE_API_URL` /
`TINGLE_RELEASE_BASE_URL` with their defaults. Dependencies: curl, unzip, jq,
sha256sum or shasum.

Resolve `TINGLE_FOLDER="$(cd "$(dirname "$0")/../.." && pwd)"`, as in
`shell/uninstall/executor.sh`, and source
`"$TINGLE_FOLDER/install/manifest.sh"`. Check that `curl`, `unzip` and `jq`
are on PATH, as `install/bootstrap.sh` does.

## Files to Change
- `shell/update/main.sh` — new flow-verb dispatcher.
- `shell/update/executor.sh` — new executor, header and setup.
