# Product-owner Plan: linux: publish the tingle Docker image for amd64 and arm64

Main plan: [plan.md](plan.md)

## Shared contracts

- Document the `scripts/release_image.sh` interface from [plan.md](plan.md#shared-contracts):
  - `setup-builder` → `build` → `smoke-test` → `publish`;
  - the `PLATFORMS` env var and its default;
  - the `tingle-builder` buildx builder;
  - the local-only `<tag>-<arch>` tags;
  - one multi-platform `<semver>` tag on Docker Hub.

## Implementation Steps

### Step 1 — Update the image doc
In `docs/agents/tingle-linux-image.md`:
- **Tag strategy:** note that each tag is a multi-platform manifest (`linux/amd64` + `linux/arm64`), and that no per-architecture tags are published.
- **Release script:** describe the four-step flow:
  - `setup-builder` registers QEMU/binfmt via a pinned `tonistiigi/binfmt` and creates the `docker-container` builder `tingle-builder`;
  - `build` loads each platform locally as `<tag>-<arch>`;
  - `smoke-test` runs every check per platform;
  - `publish` does one `buildx --push` and verifies both platforms with `imagetools inspect`.
  - Mention the `PLATFORMS` override for local builds (for example `PLATFORMS=linux/arm64` on Apple silicon without QEMU), and that the CircleCI job runs on a pinned `ubuntu-2404` machine image.
- **Version bump procedure:** add a note (in the #233 procedure, if present, or as a new bullet) that apt pins must resolve on both amd64 (`archive.ubuntu.com`) and arm64 (`ports.ubuntu.com`). A pin missing on one architecture fails the build.

## Files to Change
- `docs/agents/tingle-linux-image.md` — tag strategy, release script flow, `PLATFORMS`, pin note.

## Notes
- If #233 hasn't documented the bump procedure yet when this lands, add the dual-architecture pin note as a standalone bullet under the release script description.
