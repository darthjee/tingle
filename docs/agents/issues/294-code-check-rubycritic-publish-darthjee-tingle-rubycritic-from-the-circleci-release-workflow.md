# Issue: code_check rubycritic: publish darthjee/tingle_rubycritic from the CircleCI release workflow

## Description
Publish the `darthjee/tingle_rubycritic` image (built from `docker/rubycritic/`, delivered by #293) from the CircleCI `release` workflow, next to `darthjee/tingle`. Parent: #290. The full spec is [docs/agents/specs/code_check/rubycritic/release.md](../specs/code_check/rubycritic/release.md).

Agents: `shell` (script, CircleCI, Docker Hub description files), `product-owner` (implementation doc).

## Problem
The `rubycritic` subcommand (#295) defaults to `darthjee/tingle_rubycritic:<tingle version>`, but nothing publishes that image. Without this pipeline, a tingle release would point at an image tag that does not exist.

**Release ordering:** this issue must be merged before the tingle tag that ships #295 is pushed.

## Expected Behavior
- Pushing git tag `X.Y.Z` (the existing plain-semver filter, `branches: ignore: /.*/`) publishes `darthjee/tingle_rubycritic:X.Y.Z` as one multi-platform manifest for `linux/amd64` and `linux/arm64`.
- There is no `latest` tag, no per-arch tag pushed, and no build on regular commits. A `v`-prefixed tag triggers nothing.
- The tag is resolved like the linux image: `$CIRCLE_TAG` in CI, else `shell/linux/VERSION`. In CI, `verify_version_pin` fails the job if they differ.
- **Every release tag publishes the image.** There is no change detection for the rubycritic image, so `tingle_rubycritic:X.Y.Z` always exists for CLI `X.Y.Z`.
- The CLI release zip (`build-and-publish-release`) is published only after both images are published.
- The Docker Hub description of `darthjee/tingle_rubycritic` is updated on each release.

## Solution
### `scripts/release_image.sh`
Add an optional image selector: `scripts/release_image.sh <subcommand> [linux|rubycritic]`.
- The default is `linux`, so existing calls keep working. `setup-builder` ignores the selector. An unknown selector prints usage on stderr and exits 1.
- Per-image settings:

| Setting | `linux` | `rubycritic` |
|---------|---------|--------------|
| Image name | `darthjee/tingle` | `darthjee/tingle_rubycritic` |
| Dockerfile | `shell/linux/Dockerfile` | `docker/rubycritic/Dockerfile` |
| Build context | `.` | `docker/rubycritic` |
| Change detection | `shell/linux/` since previous tag | none, always runs |
| Smoke test | `smoke_test_image` | new `smoke_test_rubycritic` |
| Short description | `DOCKERHUB_SHORT_DESCRIPTION.txt` | `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt` |
| Full description | `DOCKERHUB_DESCRIPTION.md` | `docker/rubycritic/DOCKERHUB_DESCRIPTION.md` |

- `smoke_test_rubycritic` runs, per platform, the fixture checks from [image.md](../specs/code_check/rubycritic/image.md#6-smoke-test-fixture) against the local `<tag>-<arch>` image with the canonical run line (`--network none`, `-v docker/rubycritic/fixture:/src:ro`, `--user 501:20`), and checks the JSON with `python3`. It also checks that the image has no git and that empty stdin prints the empty object. A failure prints `<reason> on <platform>` on stderr and exits 1.
- scan (Trivy, report-only), publish (with platform verification) and update-description reuse the existing logic.
- The header comment documents the selector, the per-image settings and the no-change-detection rule.

### `.circleci/config.yml`
- New `build-and-publish-rubycritic-image` job (`machine: image: ubuntu-2404:current`): `setup-builder`, `build`, `smoke-test`, `scan`, `publish` with the `rubycritic` selector. No `requires`; it runs in parallel with the linux image job.
- New `update-rubycritic-description` job (`machine: true`), requiring `build-and-publish-rubycritic-image`.
- `build-and-publish-release` requires both image jobs.
- Same tag filters as the existing jobs. The `test` workflow is unchanged.

### Docker Hub description files (`shell`)
- `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt`: one line, 1 to 100 characters.
- `docker/rubycritic/DOCKERHUB_DESCRIPTION.md`: purpose, stdin/stdout contract, canonical run line, pinned Ruby and RubyCritic versions, tag strategy, link to the tingle repository.
- `docker/rubycritic/.dockerignore` also excludes both files.

### Docs (`product-owner`)
- New `docs/agents/tingle-rubycritic-image.md`, in the style of `docs/agents/tingle-linux-image.md`, with the sections listed in [release.md section 6](../specs/code_check/rubycritic/release.md#6-implementation-doc).
- `docs/agents/tingle-linux-image.md` gets a pointer to the new doc, and its release note also lists the rubycritic jobs.

## Benefits
- The `rubycritic` subcommand always finds its image for every tingle release.
- One script handles both images, with no duplicated release logic.
