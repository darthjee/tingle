# product-owner Plan: Image: build and publish the tingle-linux Docker image

Main plan: [plan.md](plan.md)

## Shared contracts

- Documents the exact image reference `darthjee/tingle:<tag>` that
  `architect`'s CircleCI job publishes, for sub-issue 2 (`tingle linux`
  command skeleton) to configure its `docker run` wrapper against.

## Implementation Steps

### Step 1 — Document the image reference

Add a short doc (`docs/agents/tingle-linux-image.md`) naming the Docker Hub
image (`darthjee/tingle`), its tag strategy (plain semver, published on a
manual `v*` git tag push), and a pointer to `shell/linux/Dockerfile` as the
image's source. This is what sub-issue 2 reads to configure the `docker
run` wrapper's image reference.

## Files to Change

- `docs/agents/tingle-linux-image.md` — new: documents the
  `darthjee/tingle` image reference and tag strategy.

## Notes

- Keep this brief — it's a pointer for sub-issue 2, not full user-facing
  docs.
