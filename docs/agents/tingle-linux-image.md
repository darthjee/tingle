# `tingle-linux` Docker image

- **Image**: `darthjee/tingle` on Docker Hub.
- **Tag strategy**: plain semver tags (e.g. `1.0.0`), published manually by
  pushing a matching `v*` git tag (e.g. `v1.0.0`) — no `latest`/automatic
  builds.
- **Source**: `shell/linux/Dockerfile` — a non-root `ubuntu` base with a
  baseline GNU toolbox (`coreutils`, `findutils`, `grep`, GNU `sed`, `gawk`,
  `tar`, `diffutils`).
- **Reference**: `docker run --rm darthjee/tingle:<tag> ...` — this is the
  exact image reference the `tingle linux` command's `docker run` wrapper
  should target.
