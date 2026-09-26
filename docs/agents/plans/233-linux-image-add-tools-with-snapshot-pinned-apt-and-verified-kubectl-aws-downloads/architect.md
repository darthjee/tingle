# Architect Plan: linux image: add tools with snapshot-pinned apt and verified kubectl/aws downloads

Main plan: [plan.md](plan.md)

## Shared contracts

- You consume the installed paths and the **smoke-check table** in [plan.md](plan.md#smoke-check-table-shells-package-list--architects-smoke-test). Use the shell agent's substitutions if it reports any.
- You produce the `scripts/release_image.sh scan` subcommand and the CircleCI `Scan image` step, as described in plan.md, for the product-owner to document.
- Leave the build invocation (`-f shell/linux/Dockerfile .`, repo-root context) unchanged.

## Implementation Steps

### Step 1 — Extend the smoke test
In `scripts/release_image.sh`, extend `smoke_test_image` (it already runs per platform from `cmd_smoke_test`):

- Keep the existing GNU `sed` and non-root uid checks.
- Add a tool check that runs **one** `docker run --rm --network none --platform "$platform" "$image" bash -c '...'` per image, not one container per tool, because runs are slow under QEMU. Inside it, loop over `name|command` pairs from the smoke-check table. Run each command with its output discarded. On the first failure, print `Missing or broken tool on <platform>: <name>` to stderr and exit 1.
- Keep the table as a readable array or heredoc near the top of the function, so adding a tool is a one-line change.
- `--network none` enforces "no network in the smoke test".

### Step 2 — Add the report-only `scan` subcommand and CI step
- Add `TRIVY_IMAGE="aquasec/trivy:<pinned version>"` next to `BINFMT_IMAGE`. Pin an exact tag; a digest is optional.
- Add `cmd_scan`:
  - It skips with a message when `! changed_since_previous`, like `cmd_smoke_test`.
  - It resolves the tag, then for each platform in `$PLATFORMS` runs:

    ```bash
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      "$TRIVY_IMAGE" image --platform "$platform" --exit-code 0 --no-progress \
      "$IMAGE_NAME:$tag-$(platform_arch "$platform")"
    ```

  - It's report-only: wrap each call so a Trivy failure (DB download error, for example) prints a warning and continues. The subcommand always returns 0, even under `set -euo pipefail`, for example with `if ! docker run ...; then echo "Trivy scan failed for ..." >&2; fi`.
- Wire it up: add `scan)` to `main`'s `case`, to the usage message, and to the header comment (Usage block plus a short "Scan" paragraph saying it's report-only and never fails).
- In `.circleci/config.yml`, `build-and-publish-linux-image` job: add a step between `Smoke test` and `Publish image`:

  ```yaml
  - run:
      name: Scan image
      command: scripts/release_image.sh scan
  ```

## Files to Change
- `scripts/release_image.sh` — tool checks in `smoke_test_image`, `TRIVY_IMAGE`, `cmd_scan`, the `main` dispatch, usage and header comment.
- `.circleci/config.yml` — `Scan image` step in `build-and-publish-linux-image`.

## CI Checks
- Run `shellcheck scripts/release_image.sh` locally; Codacy lints shell scripts.
- Run end to end locally: `scripts/release_image.sh setup-builder build smoke-test scan`, one subcommand per call, with `PLATFORMS=linux/<native-arch>` to skip emulation. Change detection makes these no-ops unless `shell/linux/` changed since the previous tag, which it has on this branch.

## Notes
- The Trivy container reads the local daemon's per-arch images through the docker socket. On the CircleCI `ubuntu-2404` machine executor this works as-is.
- Don't add `--severity` filters or `--exit-code 1`. The findings are informational, and they tell you when a manual bump is due.
