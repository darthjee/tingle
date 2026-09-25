# Multi-platform publish

Change `cmd_publish` to push one tag for both platforms, and verify it.

- Keep the `changed_since_previous` early exit, `verify_version_pin` and `docker login`.
- Replace `docker push "$IMAGE_NAME:$tag"` with:

  ```bash
  docker buildx build --builder "$BUILDER_NAME" --platform "$(platforms_csv)" --push \
    -t "$IMAGE_NAME:$tag" -f shell/linux/Dockerfile .
  ```

  The same builder already holds the per-platform layers from `build`, so this reuses the cache instead of rebuilding.
- Verify with `docker buildx imagetools inspect "$IMAGE_NAME:$tag"`. For each platform in `PLATFORMS`, check that the output contains `Platform: <p>`, and fail with a clear message otherwise.
- Never push the `<tag>-<arch>` local tags.

## Files to Change
- `scripts/release_image.sh` — `cmd_publish`.
