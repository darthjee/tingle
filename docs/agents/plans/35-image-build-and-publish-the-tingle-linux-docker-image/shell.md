# shell Plan: Image: build and publish the tingle-linux Docker image

Main plan: [plan.md](plan.md)

## Shared contracts

- Publishes as `darthjee/tingle:<tag>`, built from this file's
  `shell/linux/Dockerfile`, consumed by `architect`'s CircleCI job (must
  build successfully via `docker build -f shell/linux/Dockerfile .`).
- Must produce a non-root container (uid 1000) with GNU `coreutils`,
  `findutils`, `grep`, `sed`, `gawk`, `tar`, `diffutils` installed —
  `architect`'s smoke test checks `sed --version` and confirms a non-root
  effective user.

## Implementation Steps

### Step 1 — Create `shell/linux/Dockerfile`

Base the image on `ubuntu` (a recent LTS tag, e.g. `ubuntu:24.04`). Install
the baseline GNU toolbox (`coreutils`, `findutils`, `grep`, `sed`, `gawk`,
`tar`, `diffutils` — most already present in the base image; use
`apt-get install -y --no-install-recommends` for whichever aren't, in a
single `RUN` layer, then clean up apt lists to keep the image lean). Create
a non-root user (uid 1000, mirroring `python/Dockerfile`'s `useradd
--create-home --uid 1000 tingle` + `chown`/`USER` pattern) so files touched
through the volume mount (wired up in a later sub-issue) are owned
correctly on the host. No `CMD`/`ENTRYPOINT` needed — every subcommand
supplies its own command via `docker run <image> <cmd> <args...>` (per
#34), so leave the default shell entrypoint.

## Files to Change

- `shell/linux/Dockerfile` — new: `ubuntu`-based, non-root, GNU toolbox
  image.

## Notes

- No `main.sh`/`executor.sh` here — the `tingle linux` command dispatcher
  itself is out of scope for this sub-issue (tracked in #34's sub-issue 2).
