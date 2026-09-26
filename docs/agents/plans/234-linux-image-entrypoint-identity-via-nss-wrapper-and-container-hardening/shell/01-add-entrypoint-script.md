# Add the entrypoint script
Create `shell/linux/entrypoint.sh`, a POSIX `sh` script (`#!/bin/sh`, no bashisms) with the behavior below. Use the issue's script as the reference implementation. Add a header comment in the style of the other `shell/linux/` scripts, explaining what the script does and why.

- Export `HOME=/home/tingle`.
- If `id -un` fails, the uid has no passwd entry. In that case:
  - Find the library with `ls /usr/lib/*/libnss_wrapper.so | head -n 1`, which is architecture-independent (amd64 and arm64).
  - Create a directory with `mktemp -d`.
  - Write `passwd`: the contents of `/etc/passwd` plus `tingle-host:x:<uid>:<gid>::/home/tingle:/bin/bash`.
  - Write `group`: the contents of `/etc/group`, plus `tingle-host:x:<gid>:` only when `getent group <gid>` fails.
  - Export `LD_PRELOAD`, `NSS_WRAPPER_PASSWD` and `NSS_WRAPPER_GROUP`.
  - If the library or the temp dir is missing, skip this step silently. Never fail.
- If `$HOME/.ssh/host_config` exists and `$HOME/.ssh/config` does not, write the two-line wrapper from the shared contract.
- `exec "$@"`.

Nothing may go to stdout, and nothing to stderr on success. `shellcheck` must pass. The one exception: if `ls` on a glob is flagged, a `find` is also fine, as long as the result is the same.

## Files to Change
- `shell/linux/entrypoint.sh`: new file.
