# Per-platform build and smoke test

Change `cmd_build` and `cmd_smoke_test` so each platform in `PLATFORMS` is built into the local daemon and smoke-tested separately.

- `cmd_build`: keep the `changed_since_previous` early exit and `verify_version_pin`. Then, for each platform `p`:

  ```bash
  docker buildx build --builder "$BUILDER_NAME" --platform "$p" --load \
    -t "$IMAGE_NAME:$tag-$(platform_arch "$p")" -f shell/linux/Dockerfile .
  ```

- `cmd_smoke_test`: keep the early exit. Move the existing body (the `sed --version` check, the non-root `id -u` check, and any checks and Trivy scan added by #233 and #234) into `smoke_test_image <image> <platform>`, which passes `--platform "$platform"` to every `docker run`. Loop over `PLATFORMS`, calling it on `$IMAGE_NAME:$tag-<arch>`. Print which platform is being tested, and fail on the first failure (`set -e` already applies).
- If Trivy scans a local image, point it at the per-arch tag, so each platform is scanned.

## Files to Change
- `scripts/release_image.sh` — `cmd_build` platform loop, `smoke_test_image` extraction, `cmd_smoke_test` platform loop.
