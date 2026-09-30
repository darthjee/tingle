# Write release.md (#294)
Create `docs/agents/specs/code_check/rubycritic/release.md`, linking #294 at the top. Mirror `docs/agents/tingle-linux-image.md`, `scripts/release_image.sh` and `.circleci/config.yml`.

It must specify:
- **Tagging:** git tag `X.Y.Z` publishes `darthjee/tingle_rubycritic:X.Y.Z`. It uses the same tag filter as `darthjee/tingle`; there is no `latest` tag, no build on regular commits, and `v`-prefixed tags are ignored.
- **Platforms:** a single multi-platform manifest for `linux/amd64` and `linux/arm64`, with no per-architecture tags.
- **Pipeline:** setup-builder → build → smoke test (fixture → valid JSON) → scan → publish, either by extending `scripts/release_image.sh` (e.g. an image selector argument) or with a sibling script. Pick one and justify it. Also give how the CircleCI `release` workflow gains the job(s), and their dependencies.
- **Docker Hub:** the description files and the update step.
- **Implementation doc:** the outline of `docs/agents/tingle-rubycritic-image.md`.
- **Ordering rule:** #294 must be merged before the tingle tag that ships #295.

## Files to Change
- `docs/agents/specs/code_check/rubycritic/release.md`: new.
