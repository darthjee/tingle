# Spec: publishing `darthjee/tingle_rubycritic`

Sub-issue: #294. Parent: #290. Shared contracts: [README.md](README.md).

This spec covers how the image built from `docker/rubycritic/` (see
[image.md](image.md)) is published by the CircleCI `release` workflow, next to
`darthjee/tingle`. It mirrors `docs/agents/tingle-linux-image.md`,
`scripts/release_image.sh` and `.circleci/config.yml`.

## 1. Ordering rule

Issue #294 must be merged before the tingle release tag that ships #295 (the
`rubycritic` subcommand) is pushed. The CLI defaults to
`darthjee/tingle_rubycritic:<tingle version>`, so a tingle release without
this pipeline would point at an image tag that was never published.

## 2. Tagging

- Pushing git tag `X.Y.Z` publishes `darthjee/tingle_rubycritic:X.Y.Z`: the
  same plain semver string as `darthjee/tingle:X.Y.Z` and as the CLI release.
- The tag filter is the existing one:
  `/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/`, with
  `branches: ignore: /.*/`. A `v`-prefixed tag triggers nothing.
- There is no `latest` tag and no build on regular commits.
- The tag is resolved like the linux image: `$CIRCLE_TAG` in CI, else the
  trimmed content of `shell/linux/VERSION`. In CI, `shell/linux/VERSION` must
  equal `$CIRCLE_TAG`, or the job fails before building (`verify_version_pin`).
  This is the same file the CLI reads for its default image tag (see
  [subcommand.md](subcommand.md#4-the-docker-run-line)), so the CLI and the
  image always agree.
- **Every release tag publishes the image.** Unlike the linux image, the
  rubycritic image has **no change detection**: `build`, `smoke-test`, `scan`
  and `publish` never skip, even when `docker/rubycritic/` did not change
  since the previous tag. Skipping would leave `tingle_rubycritic:X.Y.Z`
  missing while the CLI `X.Y.Z` points at it.

## 3. Platforms

One multi-platform manifest per tag covering `linux/amd64` and `linux/arm64`,
built through the same buildx builder (`tingle-builder`, QEMU for the foreign
platform). No per-architecture tags are published. The local per-platform
images used by the smoke test (`darthjee/tingle_rubycritic:<tag>-<arch>`) are
loaded, never pushed. `publish` fails unless
`docker buildx imagetools inspect` lists every platform in `$PLATFORMS`.

## 4. Pipeline

### Choice: extend `scripts/release_image.sh`

`scripts/release_image.sh` gains an optional second argument, the image
selector:

```
scripts/release_image.sh <subcommand> [linux|rubycritic]
```

- The default is `linux`, so every existing call (CI and docs) keeps working
  unchanged.
- `setup-builder` ignores the selector (the builder is shared).
- Why extend rather than add a sibling script: the tag resolution, version
  pin check, builder setup, per-platform build/load, Trivy scan, publish with
  platform verification and Docker Hub description update are identical for
  both images. A sibling script would duplicate about 300 lines that must then
  be kept in sync by hand. Only the settings below and the smoke test differ.

Per-image settings, chosen from the selector:

| Setting | `linux` | `rubycritic` |
|---------|---------|--------------|
| Image name | `darthjee/tingle` | `darthjee/tingle_rubycritic` |
| Dockerfile | `shell/linux/Dockerfile` | `docker/rubycritic/Dockerfile` |
| Build context | `.` (repo root) | `docker/rubycritic` |
| Change detection | `shell/linux/` since the previous tag (unchanged) | none, always runs |
| Smoke test | existing `smoke_test_image` | `smoke_test_rubycritic` (below) |
| Short description | `DOCKERHUB_SHORT_DESCRIPTION.txt` | `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt` |
| Full description | `DOCKERHUB_DESCRIPTION.md` | `docker/rubycritic/DOCKERHUB_DESCRIPTION.md` |

An unknown selector prints the usage line on stderr and exits 1.

### Steps for `rubycritic`

1. **setup-builder:** unchanged.
2. **build:** `verify_version_pin`, then one
   `docker buildx build --load` per platform, tagged
   `darthjee/tingle_rubycritic:<tag>-<arch>`, with
   `-f docker/rubycritic/Dockerfile docker/rubycritic`.
3. **smoke-test:** for each platform, `smoke_test_rubycritic` runs the fixture
   checks from [image.md](image.md#6-smoke-test-fixture) against the local
   `<tag>-<arch>` image, with `--platform <platform>`, the canonical run line
   (`--network none`, `-v docker/rubycritic/fixture:/src:ro`, `--user 501:20`)
   and the fixture list on stdin. The JSON is checked with `python3` (already
   a dependency of the script). It also checks that the image has no git and
   that empty stdin prints the empty object. Any failed check prints
   `<reason> on <platform>` on stderr and exits 1.
4. **scan:** the pinned Trivy image against each local `<tag>-<arch>` image,
   report-only, as for the linux image.
5. **publish:** `verify_version_pin`, `docker login`, one
   `docker buildx build --push` for all of `$PLATFORMS` tagged
   `darthjee/tingle_rubycritic:<tag>`, then the platform verification.
6. **update-description:** the same PATCH as the linux image, with the
   rubycritic description files, against
   `https://hub.docker.com/v2/repositories/darthjee/tingle_rubycritic/`.

The script header comment documents the selector, the per-image settings and
the "no change detection" rule.

### CircleCI

`.circleci/config.yml` gains two jobs in the `release` workflow, with the same
tag filter and `branches: ignore: /.*/` as the existing ones:

| Job | Executor | Steps | Requires |
|-----|----------|-------|----------|
| `build-and-publish-rubycritic-image` | `machine: image: ubuntu-2404:current` | `checkout`, then `scripts/release_image.sh <step> rubycritic` for `setup-builder`, `build`, `smoke-test`, `scan`, `publish` | none |
| `update-rubycritic-description` | `machine: true` | `checkout`, `scripts/release_image.sh update-description rubycritic` | `build-and-publish-rubycritic-image` |

- `build-and-publish-release` (the CLI zip) now requires **both**
  `build-and-publish-linux-image` and `build-and-publish-rubycritic-image`, so
  a CLI release is never published without its images.
- The two image jobs run in parallel. Each runs its own `setup-builder`.
- The existing jobs keep calling the script without a selector.
- The `test` workflow is unchanged: no image is built on regular commits.

## 5. Docker Hub

- New files, owned by the `shell` agent with the rest of `docker/rubycritic/`:
  - `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt`: one line, 1 to 100
    characters after trimming, for example
    `RubyCritic (Flog, Flay, Reek) as JSON for tingle code_check rubycritic.`
  - `docker/rubycritic/DOCKERHUB_DESCRIPTION.md`: what the image is for, the
    stdin/stdout contract, the canonical run line, the pinned Ruby and
    RubyCritic versions, the tag strategy (same tag as tingle, no `latest`)
    and a link to the tingle repository.
- The `.dockerignore` from [image.md](image.md#1-location-and-files) must also
  exclude both description files from the build context.
- `update-description rubycritic` validates the two files the same way as for
  the linux image (missing file, empty or too-long summary → exit 1).
- The Docker Hub repository `darthjee/tingle_rubycritic` is created by the
  first `publish`. `update-description` runs after it, so the repository
  exists by then.

## 6. Implementation doc

Issue #294 adds `docs/agents/tingle-rubycritic-image.md` (owned by
`product-owner`), in the style of `docs/agents/tingle-linux-image.md`, with these sections:

1. **Header bullets:** image name, tag strategy (same semver as tingle, every
   tag published, no `latest`, `v` tags ignored, one amd64/arm64 manifest),
   source (`docker/rubycritic/`, build context, two-stage Dockerfile), and the
   reproducible pins (base digest, `Gemfile.lock`, versions table).
2. **Contract:** the canonical run line, stdin, stdout (`report.json` plus
   `parse_errors`), stderr, exit status, and why the entrypoint pre-parses.
3. **Runtime user and hardening:** arbitrary uid, read-only `/src`, no
   network, no git.
4. **Release pipeline:** the selector, the steps, the smoke-test checks, the
   CircleCI jobs and their dependencies, the "no change detection" rule.
5. **Docker Hub description:** the two files and the update step.
6. **Local build:** `make rubycritic-image` and `--image tingle_rubycritic:dev`.
7. **Bumping versions:** Ruby (tag + digest) and RubyCritic (Gemfile + lock
   regeneration), then the smoke test on both platforms.

`docs/agents/tingle-linux-image.md` gets a one-line pointer to the new doc,
and its "Bumping versions" note that "a git tag `X.Y.Z` triggers ..." also
lists the rubycritic jobs.
