# Builder and QEMU setup

Add a `setup-builder` subcommand to `scripts/release_image.sh`, so that the machine can build every platform in `PLATFORMS`.

- Add `PLATFORMS="${PLATFORMS:-linux/amd64 linux/arm64}"`, `BUILDER_NAME="tingle-builder"` and a pinned `BINFMT_IMAGE="tonistiigi/binfmt:<version>"` near the other constants.
- Add small helpers:
  - `platform_arch <platform>` → `${1#linux/}`;
  - `platforms_csv` → `PLATFORMS` joined with commas.
- `cmd_setup_builder`:
  1. Unless the builder `tingle-builder` exists (`docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1`), create it: `docker buildx create --name "$BUILDER_NAME" --driver docker-container`.
  2. Bootstrap it: `docker buildx inspect --bootstrap "$BUILDER_NAME"`, and read its `Platforms:` line.
  3. For each platform in `PLATFORMS` that is not listed, collect its arch. If any are missing, run `docker run --privileged --rm "$BINFMT_IMAGE" --install <arch,...>`, then re-bootstrap and check again. Fail with a clear message if a platform is still unsupported.
  - It must be idempotent: running it twice is a no-op the second time. On Docker Desktop, where binfmt is preinstalled, no privileged container is run.
- Wire `setup-builder` into `main`'s `case`, and update the usage line and header comment.

## Files to Change
- `scripts/release_image.sh` — new constants, helpers, `cmd_setup_builder`, `main` dispatch, usage and header comment.
