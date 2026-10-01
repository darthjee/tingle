# Product-owner Plan: code_check rubycritic: publish darthjee/tingle_rubycritic from the CircleCI release workflow

Main plan: [plan.md](plan.md)

## Shared contracts

- **Script CLI:** `scripts/release_image.sh <subcommand> [linux|rubycritic]`. Subcommands: `setup-builder`, `build`, `smoke-test`, `scan`, `publish`, `update-description`. The selector defaults to `linux`; `setup-builder` ignores it; an unknown selector prints usage on stderr and exits 1.
- **Image:** `darthjee/tingle_rubycritic:<tag>` (one amd64/arm64 manifest). The local per-platform images are `darthjee/tingle_rubycritic:<tag>-<arch>`, loaded and never pushed. The tag comes from `$CIRCLE_TAG`, else `shell/linux/VERSION`, with `verify_version_pin` in CI.
- **No change detection** for `rubycritic`: `build`, `smoke-test`, `scan` and `publish` never skip.
- **CircleCI jobs** (release workflow, same tag filter, `branches: ignore: /.*/`):
  - `build-and-publish-rubycritic-image` (`machine: image: ubuntu-2404:current`, no `requires`)
  - `update-rubycritic-description` (`machine: true`, requires `build-and-publish-rubycritic-image`)
  - `build-and-publish-release` requires both `build-and-publish-linux-image` and `build-and-publish-rubycritic-image`.
- **Docker Hub files:** `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt` (1-100 chars trimmed) and `docker/rubycritic/DOCKERHUB_DESCRIPTION.md`, both excluded by `docker/rubycritic/.dockerignore`.

## Implementation Steps

### Step 1 — Write docs/agents/tingle-rubycritic-image.md
Create the implementation doc in the style of `docs/agents/tingle-linux-image.md`. Use the sections listed in [release.md section 6](../../specs/code_check/rubycritic/release.md#6-implementation-doc):
1. Header bullets: image, tag strategy, source, reproducible pins.
2. Contract.
3. Runtime user and hardening.
4. Release pipeline: the selector, the steps, the smoke-test checks, the CircleCI jobs and dependencies, no change detection.
5. Docker Hub description.
6. Local build: `make rubycritic-image`, `--image tingle_rubycritic:dev`.
7. Bumping versions.

Take the facts from [image.md](../../specs/code_check/rubycritic/image.md) and [release.md](../../specs/code_check/rubycritic/release.md) and from the shared contracts above. Do not invent behavior.

### Step 2 — Link it from existing docs
- `docs/agents/tingle-linux-image.md`: add a one-line pointer to the new doc. In "Bumping versions", the note that a git tag `X.Y.Z` triggers the release also lists the rubycritic jobs and that `build-and-publish-release` now waits for both images.
- Add the new doc to whatever index lists `tingle-linux-image.md`. Check `AGENTS.md`'s documentation section and `docs/agents/architecture.md`/`folder-structure.md` with `grep -rn tingle-linux-image.md`.

## Files to Change
- `docs/agents/tingle-rubycritic-image.md` — new.
- `docs/agents/tingle-linux-image.md` — pointer and release note.
- `AGENTS.md` / other doc indexes that reference `tingle-linux-image.md` — add the new doc, only where one is listed.

## Notes
- Script behavior (selector name, job names, file paths) must match the shared contracts exactly. If the `shell` implementation differs, follow the code and flag the divergence.
