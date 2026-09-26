# Plan: linux image: entrypoint identity via nss_wrapper and container hardening

Issue: [234-linux-image-entrypoint-identity-via-nss-wrapper-and-container-hardening.md](../../issues/234-linux-image-entrypoint-identity-via-nss-wrapper-and-container-hardening.md)

## Overview
Add an entrypoint to the `darthjee/tingle` image. When the container runs as a uid the image doesn't know, the entrypoint gives that uid a passwd/group identity through `libnss-wrapper`. It also sets `HOME=/home/tingle` and generates an `~/.ssh/config` wrapper for part 3 (#235). The image is hardened: `/etc/passwd` and `/etc/group` stay read-only, there are no setuid or setgid binaries, and `no-new-privileges` is always set. `docker_run` gains a `--`-delimited slot for extra `docker run` arguments, and the release smoke tests cover all of the above.

## Agents involved

- [shell](shell.md): Dockerfile, entrypoint script, `docker_run.sh` and `executor.sh` under `shell/linux/`.
- [architect](architect.md): smoke tests in `scripts/release_image.sh` (root-level `scripts/`).
- [product-owner](product-owner.md): `docs/agents/tingle-linux-image.md`.

## Shared contracts

- **Entrypoint path**: repo file `shell/linux/entrypoint.sh` → image path `/usr/local/bin/tingle-entrypoint`, mode 0755.
- **Image config**: `ENTRYPOINT ["/usr/local/bin/tingle-entrypoint"]`, `CMD ["bash"]`, `USER tingle` (uid 1000) unchanged.
- **Identity for a foreign uid** (for example `--user 501:20`):
  - `id -un` prints `tingle-host`;
  - `HOME=/home/tingle`;
  - `LD_PRELOAD` points at `libnss_wrapper.so`, with `NSS_WRAPPER_PASSWD` and `NSS_WRAPPER_GROUP` set to files in a `mktemp -d` directory.
  - With the default uid 1000, none of these variables are set.
- **Group entry**: `tingle-host:x:<gid>:` is appended only when the gid has no existing group. On Ubuntu, gid 20 is already `dialout`.
- **Permissions**: `/home/tingle` and `/home/tingle/.ssh` are mode 1777. `find / -xdev -perm /6000 -type f` returns nothing.
- **ssh contract with part 3**: when `~/.ssh/host_config` exists and `~/.ssh/config` does not, the entrypoint writes `~/.ssh/config` containing exactly:

  ```
  IgnoreUnknown UseKeychain,AddKeysToAgent
  Include ~/.ssh/host_config
  ```

- **Output**: the entrypoint writes nothing to stdout, nothing to stderr on success, and always ends with `exec "$@"`.
- **`docker_run` signature**: `docker_run <mode: none|tty|stdin> [docker-args...] -- <command> [args...]`.
  - `--` is required, so a `--` among the command's own arguments (for example `tingle linux sed -- ...`) is never mistaken for the separator.
  - Every run always gets `--security-opt no-new-privileges`.
