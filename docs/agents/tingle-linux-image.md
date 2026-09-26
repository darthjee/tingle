# `tingle-linux` Docker image

- **Image**: `darthjee/tingle` on Docker Hub.
- **Tag strategy**: the published Docker tag is exactly the plain semver
  git tag — pushing git tag `1.0.0` publishes `darthjee/tingle:1.0.0`
  (same string, not two different formats). The git tag is pushed by hand;
  CircleCI then builds and publishes the image. There is no `latest` tag and
  no build on regular commits. A `v`-prefixed tag triggers no release
  (silently ignored by the CircleCI tag filter). Each published tag is one
  multi-platform manifest covering `linux/amd64` and `linux/arm64`. No
  per-architecture tags (e.g. `1.0.0-arm64`) are published.
- **Source**: `shell/linux/Dockerfile` — a non-root `ubuntu` base with a
  baseline GNU toolbox (`coreutils`, `findutils`, `grep`, GNU `sed`, `gawk`,
  `tar`, `diffutils`).
- **Version pin**: `shell/linux/VERSION` — a single line containing exactly
  the currently-published tag (e.g. `1.0.0`), the one source of truth for
  "what tag is currently published." Both CI and `shell/linux/docker_run.sh`
  read this file instead of hardcoding a tag.
- **Release script**: `scripts/release_image.sh` performs the
  build-needed check (skips rebuild/republish when `shell/linux/` hasn't
  changed since the previous release tag), build, smoke test, publish, and
  `update-description` (pushes the Docker Hub description) — invoked from
  `.circleci/config.yml` rather than inlining that logic in the CI YAML.
  The CircleCI job `build-and-publish-linux-image` runs on a pinned
  `ubuntu-2404` machine image and calls four subcommands in order, in one
  job so the buildx cache is shared:
  1. `setup-builder` (idempotent) registers QEMU/binfmt for every
     non-native platform through a pinned `tonistiigi/binfmt` image. It
     skips this when the builder already lists every platform, as on Docker
     Desktop. It then creates and selects the `docker-container` buildx
     builder `tingle-builder`.
  2. `build` builds each platform with `--load` and tags it locally as
     `darthjee/tingle:<tag>-<arch>` (e.g. `1.0.0-amd64`, `1.0.0-arm64`).
     These tags stay in the local daemon and are never pushed.
  3. `smoke-test` runs every check against each `<tag>-<arch>` image, with
     `--platform` on every `docker run`. It fails if any platform fails.
  4. `publish` does one multi-platform `docker buildx build --push` of
     `darthjee/tingle:<tag>`, then runs `docker buildx imagetools inspect`
     on that tag. The job fails unless the manifest lists every platform.

  `build`, `smoke-test` and `publish` keep the build-needed early exit.
  `build` and `publish` also keep the version-pin check.
- **Platforms**: the `PLATFORMS` env var (space-separated, default
  `linux/amd64 linux/arm64`) picks the platforms that `setup-builder`,
  `build`, `smoke-test` and `publish` handle. Override it to build and test
  locally without emulation, for example `PLATFORMS=linux/arm64` on Apple
  silicon without QEMU.
- **Dual-architecture apt pins**: every pinned apt package version in
  `shell/linux/Dockerfile` must resolve on both architectures. amd64 pulls
  from `archive.ubuntu.com` and arm64 from `ports.ubuntu.com`. A pin missing
  on one architecture fails the build, so check both mirrors when bumping a
  pin.
- **Docker Hub description**: the short description lives in
  `DOCKERHUB_SHORT_DESCRIPTION.txt` (repo root, a single line limited to 100
  characters) and the full description lives in `DOCKERHUB_DESCRIPTION.md`
  (repo root, Markdown). `scripts/release_image.sh update-description` pushes
  both in one Docker Hub API call, through the `update-description` CircleCI
  job on release tags. It fails the job when either file is missing, the
  short description is empty or too long, or the HTTP call fails. Links in
  `DOCKERHUB_DESCRIPTION.md` must be absolute URLs, because Docker Hub cannot
  resolve paths relative to the repository.
- **Reference**: `docker run --rm darthjee/tingle:<tag> ...` — this is the
  exact image reference the `tingle linux` command's `docker run` wrapper
  should target.
