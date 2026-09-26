# Architect Plan: linux image: entrypoint identity via nss_wrapper and container hardening

Main plan: [plan.md](plan.md)

## Shared contracts

The smoke tests rely on what the shell agent produces:
- entrypoint `/usr/local/bin/tingle-entrypoint`, `CMD ["bash"]`;
- foreign uid resolves as `tingle-host`, with `HOME=/home/tingle`;
- `/home/tingle` and `/home/tingle/.ssh` are writable by any uid;
- no setuid or setgid files;
- `LD_PRELOAD` is unset for uid 1000.

## Implementation Steps

### Step 1 — Add identity and hardening smoke tests
Add a `smoke_test_identity "$image" "$platform"` function to `scripts/release_image.sh` and call it from `smoke_test_image`. Use `--network none`, and group the checks into as few containers as possible, because runs under QEMU are slow. Each failure prints a clear message that names the platform and exits 1.

- **Default command**:
  - `docker image inspect` shows `Config.Entrypoint == ["/usr/local/bin/tingle-entrypoint"]` and `Config.Cmd == ["bash"]`;
  - `echo 'echo ok' | docker run --rm -i <image>` prints exactly `ok`.
- **Foreign uid**: one container with `--user 501:20` runs a `bash -c` script that asserts:
  - `id -un` is `tingle-host`;
  - `$HOME` is `/home/tingle`;
  - both `$HOME` and `$HOME/.ssh` are writable (touch and remove a file);
  - `ssh -G localhost` succeeds;
  - `/etc/passwd` is still owned by root and not writable, and its sha256 equals the one recorded from a default-uid run.
- **Default uid**: `LD_PRELOAD` is empty, and `id -un` is `tingle`.
- **stdin and exit codes**:
  - `printf a | docker run --rm -i <image> sed s/a/b/` outputs exactly `b` (compare the full output, which proves the entrypoint added nothing);
  - `docker run --rm <image> false` exits non-zero.
- **No setuid/setgid**: `find / -xdev -perm /6000 -type f` prints nothing.

Update the script's header comment where it lists what `smoke-test` checks.

## Files to Change
- `scripts/release_image.sh`: new `smoke_test_identity` function, the call from `smoke_test_image`, and the header comment.

## CI Checks
- `scripts/`: `PLATFORMS=linux/amd64 scripts/release_image.sh build && PLATFORMS=linux/amd64 scripts/release_image.sh smoke-test`. The CI jobs are `Build image` and `Smoke test`. They run on release tags, and `shellcheck scripts/release_image.sh` also applies.

## Notes
- This depends on the shell agent's steps being done first, because the image must be rebuilt before the smoke tests can pass.
