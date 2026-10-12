# Spec: publishing `darthjee/tingle_js_complexity`

Sub-issue: #319. Parent: #315. Shared contracts: [README.md](README.md).

This spec covers how the image built from `docker/js_complexity/` (see
[image.md](image.md)) is published by the CircleCI `release` workflow, next to
`darthjee/tingle` and `darthjee/tingle_rubycritic`. It extends the existing
`scripts/release_image.sh` and `.circleci/config.yml`; it adds no new script.

## 1. Ordering rule

#319 must be merged before the tingle release tag that ships #320 (the
`js_complexity` subcommand) is pushed. The CLI defaults to
`darthjee/tingle_js_complexity:<tingle version>`, so a tingle release without
this pipeline would point at an image tag that was never published.

## 2. Tagging

- Pushing git tag `X.Y.Z` publishes `darthjee/tingle_js_complexity:X.Y.Z`:
  the same plain semver string as `darthjee/tingle:X.Y.Z`,
  `darthjee/tingle_rubycritic:X.Y.Z` and the CLI release.
- The tag filter is the existing one,
  `/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/`, with
  `branches: ignore: /.*/`. A `v`-prefixed tag triggers nothing.
- There is no `latest` tag and no build on regular commits.
- The tag is resolved by the existing `resolve_tag`: `$CIRCLE_TAG` in CI,
  else the trimmed content of `shell/linux/VERSION`. In CI,
  `verify_version_pin` fails the job before building or publishing when the
  two differ. The CLI reads the same file for its default image tag, so the
  CLI and the image always agree.
- **Every release tag publishes the image.** Like `rubycritic`, the
  `js_complexity` image has **no change detection**: `build`, `smoke-test`,
  `scan` and `publish` never skip. Skipping would leave
  `tingle_js_complexity:X.Y.Z` missing while the CLI `X.Y.Z` points at it.

## 3. Platforms

One multi-platform manifest per tag covering `linux/amd64` and
`linux/arm64`, built through the shared buildx builder (`tingle-builder`,
QEMU for the foreign platform). No per-architecture tags are published. The
local per-platform images used by the smoke test
(`darthjee/tingle_js_complexity:<tag>-<arch>`) are loaded, never pushed.
`publish` fails unless `docker buildx imagetools inspect` lists every
platform in `$PLATFORMS`.

The FTA stage compiles Rust (see [image.md](image.md#2-dockerfile)). Under
QEMU the arm64 build is much slower than the native one (100 s for the
emulated platform on the grounding host, against 29 s native). That is
accepted; no cross-compilation or prebuilt binary is introduced.

## 4. Pipeline

### `scripts/release_image.sh`

The script gains a third image selector:

```
scripts/release_image.sh <subcommand> [linux|rubycritic|js_complexity]
```

`select_image()` gets a `js_complexity` case:

| Setting | `linux` | `rubycritic` | `js_complexity` |
|---------|---------|--------------|-----------------|
| Image name | `darthjee/tingle` | `darthjee/tingle_rubycritic` | `darthjee/tingle_js_complexity` |
| Dockerfile | `shell/linux/Dockerfile` | `docker/rubycritic/Dockerfile` | `docker/js_complexity/Dockerfile` |
| Build context | `.` (repo root) | `docker/rubycritic` | `docker/js_complexity` |
| Change detection | `shell/linux/` since the previous tag | none, always runs | none, always runs |
| Smoke test | `smoke_test_image` | `smoke_test_rubycritic` | `smoke_test_js_complexity` |
| Short description | `DOCKERHUB_SHORT_DESCRIPTION.txt` | `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt` | `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` |
| Full description | `DOCKERHUB_DESCRIPTION.md` | `docker/rubycritic/DOCKERHUB_DESCRIPTION.md` | `docker/js_complexity/DOCKERHUB_DESCRIPTION.md` |

- The `USAGE` line and the header comment list the new selector, its
  settings and the "no change detection" rule.
- `setup-builder` still ignores the selector.

### Compatibility (normative)

- Calling `scripts/release_image.sh` with no selector still means `linux`.
- The `linux` and `rubycritic` selectors behave exactly as before: same
  settings, same smoke tests, same skips. `js_complexity` is only added.
- An unknown selector still prints the usage line on stderr and exits 1.

### Steps for `js_complexity`

1. **setup-builder:** unchanged.
2. **build:** `verify_version_pin`, then one `docker buildx build --load` per
   platform, tagged `darthjee/tingle_js_complexity:<tag>-<arch>`, with
   `-f docker/js_complexity/Dockerfile docker/js_complexity`.
3. **smoke-test:** for each platform, `smoke_test_js_complexity` runs the
   fixture checks from [image.md](image.md#9-smoke-test-fixture) against
   the local `<tag>-<arch>` image, with `--platform <platform>`, the canonical
   run line (`--pull never --network none --security-opt no-new-privileges`,
   `-v docker/js_complexity/fixture:/src:ro`, `--user 501:20`) and the
   fixture list plus the hostile lines on stdin. The JSON is checked with
   `python3`, as for `rubycritic`. It also checks that the image has no git
   and that empty stdin prints empty `files` and `warnings`. Any failed check
   prints `<reason> on <platform>` on stderr and exits 1. The checks for
   jscpd (#324), escomplex (#325) and `Cart.vue` (#326) are added by those
   sub-issues, in the same PR as the image change.
4. **scan:** the pinned Trivy image against each local `<tag>-<arch>` image,
   report-only.
5. **publish:** `verify_version_pin`, `docker login`, one
   `docker buildx build --push` for all of `$PLATFORMS`, tagged
   `darthjee/tingle_js_complexity:<tag>`, then the platform verification.
6. **update-description:** the same PATCH as the other images, with the
   `js_complexity` description files, against
   `https://hub.docker.com/v2/repositories/darthjee/tingle_js_complexity/`.

### CircleCI

`.circleci/config.yml` gains two jobs in the `release` workflow, mirroring
the `rubycritic` ones, with the same tag filter and
`branches: ignore: /.*/`:

| Job | Executor | Steps | Requires |
|-----|----------|-------|----------|
| `build-and-publish-js-complexity-image` | `machine: image: ubuntu-2404:current` | `checkout`, then `scripts/release_image.sh <step> js_complexity` for `setup-builder`, `build`, `smoke-test`, `scan`, `publish` | none |
| `update-js-complexity-description` | `machine: true` | `checkout`, `scripts/release_image.sh update-description js_complexity` | `build-and-publish-js-complexity-image` |

- `build-and-publish-release` (the CLI zip) now requires
  `build-and-publish-linux-image`, `build-and-publish-rubycritic-image`
  **and** `build-and-publish-js-complexity-image`, so a CLI release is never
  published without its images.
- The three image jobs run in parallel, each with its own `setup-builder`.
- The existing jobs keep their calls unchanged.
- The `test` workflow is unchanged: no image is built on regular commits.

## 5. Docker Hub

- New files, owned by the `shell` agent with the rest of
  `docker/js_complexity/`:
  - `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt`: one line, 1 to
    100 characters after trimming, for example
    `FTA, jscpd and escomplex as JSON for tingle code_check js_complexity.`
  - `docker/js_complexity/DOCKERHUB_DESCRIPTION.md`: what the image is for,
    the stdin/stdout contract, the canonical run line, the pinned Node and
    tool versions, the tag strategy (same tag as tingle, no `latest`) and a
    link to the tingle repository.
- The `.dockerignore` from [image.md](image.md#1-location-and-files) also
  excludes both description files.
- `update-description js_complexity` validates the two files like the other
  images (missing file, empty or too-long summary → exit 1).
- The Docker Hub repository `darthjee/tingle_js_complexity` is created by
  the first `publish`; `update-description` runs after it.
- Until #324 and #325 land, the description lists FTA only. Each of them
  updates the description in its own PR.

## 6. Implementation doc

#319 adds `docs/agents/tingle-js-complexity-image.md` (owned by
`product-owner`), in the style of `docs/agents/tingle-rubycritic-image.md`:

1. **Header bullets:** image name, tag strategy (same semver as tingle, every
   tag published, no `latest`, `v` tags ignored, one amd64/arm64 manifest),
   source (`docker/js_complexity/`, build context, the FTA/npm/final
   stages), and the pins (base digest, Rust stage, `package-lock.json`,
   versions table).
2. **Contract:** the canonical run line, stdin, the refused lines, the
   staged tree, the merged JSON on stdout, stderr and exit status.
3. **Runtime user and hardening:** arbitrary uid, read-only `/src`, no
   network, no git, writes only under `/tmp`.
4. **Release pipeline:** the selector, the steps, the smoke-test checks, the
   CircleCI jobs and their dependencies, the "no change detection" rule.
5. **Docker Hub description:** the two files and the update step.
6. **Local build:** `make js-complexity-image` and
   `--image tingle_js_complexity:dev`.
7. **Bumping versions:** from [image.md](image.md#13-bumping-versions).

`docs/agents/tingle-linux-image.md` and
`docs/agents/tingle-rubycritic-image.md` get a one-line pointer to the new
doc, and the note that a git tag `X.Y.Z` triggers the image jobs also lists
the `js_complexity` jobs.
