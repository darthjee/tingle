# `tingle-linux` Docker image

- **Image**: `darthjee/tingle` on Docker Hub.
- **Tag strategy**: the published Docker tag is exactly the `v`-prefixed
  git tag — pushing git tag `v1.0.0` publishes `darthjee/tingle:v1.0.0`
  (same string, not two different formats) — published manually, no
  `latest`/automatic builds.
- **Source**: `shell/linux/Dockerfile` — a non-root `ubuntu` base with a
  baseline GNU toolbox (`coreutils`, `findutils`, `grep`, GNU `sed`, `gawk`,
  `tar`, `diffutils`).
- **Version pin**: `shell/linux/VERSION` — a single line containing exactly
  the currently-published tag (e.g. `v1.0.0`), the one source of truth for
  "what tag is currently published." Both CI and `shell/linux/docker_run.sh`
  read this file instead of hardcoding a tag.
- **Release script**: `scripts/release_image.sh` performs the
  build-needed check (skips rebuild/republish when `shell/linux/` hasn't
  changed since the previous `v*` tag), build, smoke test, and publish —
  invoked from `.circleci/config.yml` rather than inlining that logic in
  the CI YAML.
- **Reference**: `docker run --rm darthjee/tingle:<tag> ...` — this is the
  exact image reference the `tingle linux` command's `docker run` wrapper
  should target.
