# Pin the base image and switch apt to a snapshot

Make the build reproducible before adding any packages.

- Replace `FROM ubuntu:24.04` with `FROM ubuntu:24.04@sha256:<digest>`. Use the multi-platform **index** digest, from `docker buildx imagetools inspect ubuntu:24.04`, not a per-arch manifest digest, so both `linux/amd64` and `linux/arm64` resolve. Use the same reference for both stages. A top-level `ARG BASE_IMAGE=ubuntu:24.04@sha256:...` before the first `FROM` avoids duplicating it.
- Add `ARG UBUNTU_SNAPSHOT=<YYYYMMDDTHHMMSSZ>` with a recent date, and redeclare it inside each stage that uses it.
- Add `SHELL ["/bin/bash", "-o", "pipefail", "-c"]` to each stage, before any `RUN` that pipes (DL4006).
- Change the apt `RUN` to `apt-get update --snapshot "$UBUNTU_SNAPSHOT"`. Keep `--no-install-recommends` and `rm -rf /var/lib/apt/lists/*` in the same `RUN`.
- Re-resolve the 7 existing pins (`coreutils`, `findutils`, `grep`, `sed`, `gawk`, `tar`, `diffutils`) against that snapshot, on both architectures:

  ```bash
  docker run --rm --platform linux/<arch> ubuntu:24.04@sha256:<digest> \
    bash -c 'apt-get update --snapshot <date> >/dev/null && apt-cache policy <pkgs...>'
  ```

- First check that `--snapshot` works before `ca-certificates` is installed (the stock sources use plain HTTP, and apt still checks signatures). If it doesn't, bootstrap `ca-certificates` and add a comment explaining why.

## Files to Change
- `shell/linux/Dockerfile` — digest-pinned `FROM`, `UBUNTU_SNAPSHOT` `ARG`, `SHELL` with pipefail, snapshot `apt-get update`, re-resolved existing pins.
