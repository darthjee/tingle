# Spec: publishing `darthjee/tingle_php_complexity`

Sub-issue: #347. Parent: #344. Shared contracts: [README.md](README.md).

This spec covers how the image built from `docker/php_complexity/` (see
[image.md](image.md)) is published by the CircleCI `release` workflow, next to
`darthjee/tingle`, `darthjee/tingle_rubycritic` and
`darthjee/tingle_js_complexity`. It extends the existing
`scripts/release_image.sh` and `.circleci/config.yml`; it adds no new script.

## 1. Ordering rule

#347 must be merged before the tingle release tag that ships #348 (the
`php_complexity` subcommand) is pushed. The CLI defaults to
`darthjee/tingle_php_complexity:<tingle version>`, so a tingle release
without this pipeline would point at an image tag that was never published.

## 2. Tagging

- Pushing git tag `X.Y.Z` publishes `darthjee/tingle_php_complexity:X.Y.Z`:
  the same plain semver string as `darthjee/tingle:X.Y.Z`,
  `darthjee/tingle_rubycritic:X.Y.Z`, `darthjee/tingle_js_complexity:X.Y.Z`
  and the CLI release.
- The tag filter is the existing one,
  `/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/`, with
  `branches: ignore: /.*/`. A `v`-prefixed tag triggers nothing.
- There is no `latest` tag and no build on regular commits.
- The tag is resolved by the existing `resolve_tag`: `$CIRCLE_TAG` in CI,
  else the trimmed content of `shell/linux/VERSION`. In CI,
  `verify_version_pin` fails the job before building or publishing when the
  two differ. The CLI reads the same file for its default image tag, so the
  CLI and the image always agree.
- **Every release tag publishes the image.** Like `rubycritic` and
  `js_complexity`, the `php_complexity` image has **no change detection**:
  `build`, `smoke-test`, `scan` and `publish` never skip. Skipping would
  leave `tingle_php_complexity:X.Y.Z` missing while the CLI `X.Y.Z` points at
  it.

## 3. Platforms

One multi-platform manifest per tag covering `linux/amd64` and
`linux/arm64`, built through the shared buildx builder (`tingle-builder`,
QEMU for the foreign platform). No per-architecture tags are published. The
local per-platform images used by the smoke test
(`darthjee/tingle_php_complexity:<tag>-<arch>`) are loaded, never pushed.
`publish` fails unless `docker buildx imagetools inspect` lists every
platform in `$PLATFORMS`.

Every base image (`php`, `composer` and, from #352, `node`) has both
platforms in its index (README §10), and no stage compiles anything: the
Composer stage only unpacks PHP packages, and the Node stage only unpacks
jscpd's prebuilt binary. The emulated build was checked in the grounding run
([image.md](image.md#10-grounding-run)).

## 4. Pipeline

### `scripts/release_image.sh`

The script gains a fourth image selector:

```
scripts/release_image.sh <subcommand> [linux|rubycritic|js_complexity|php_complexity]
```

`select_image()` gets a `php_complexity` case:

| Setting | `js_complexity` (existing) | `php_complexity` (new) |
|---------|----------------------------|------------------------|
| Image name | `darthjee/tingle_js_complexity` | `darthjee/tingle_php_complexity` |
| Dockerfile | `docker/js_complexity/Dockerfile` | `docker/php_complexity/Dockerfile` |
| Build context | `docker/js_complexity` | `docker/php_complexity` |
| Change detection | none, always runs | none, always runs |
| Smoke test | `smoke_test_js_complexity` | `smoke_test_php_complexity` |
| Short description | `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` | `docker/php_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` |
| Full description | `docker/js_complexity/DOCKERHUB_DESCRIPTION.md` | `docker/php_complexity/DOCKERHUB_DESCRIPTION.md` |

- The `USAGE` line, the per-subcommand usage comments and the settings table
  in the header comment list the new selector, its settings and the
  "no change detection" rule.
- `setup-builder` still ignores the selector.

### Compatibility (normative)

- Calling `scripts/release_image.sh` with no selector still means `linux`.
- The `linux`, `rubycritic` and `js_complexity` selectors behave exactly as
  before: same settings, same smoke tests, same skips. `php_complexity` is
  only added.
- An unknown selector still prints the usage line on stderr and exits 1.

### Steps for `php_complexity`

1. **setup-builder:** unchanged.
2. **build:** `verify_version_pin`, then one `docker buildx build --load` per
   platform, tagged `darthjee/tingle_php_complexity:<tag>-<arch>`, with
   `-f docker/php_complexity/Dockerfile docker/php_complexity`.
3. **smoke-test:** for each platform, `smoke_test_php_complexity` (below).
4. **scan:** the pinned Trivy image against each local `<tag>-<arch>` image,
   report-only.
5. **publish:** `verify_version_pin`, `docker login`, one
   `docker buildx build --push` for all of `$PLATFORMS`, tagged
   `darthjee/tingle_php_complexity:<tag>`, then the platform verification.
6. **update-description:** the same PATCH as the other images, with the
   `php_complexity` description files, against
   `https://hub.docker.com/v2/repositories/darthjee/tingle_php_complexity/`.

### `smoke_test_php_complexity`

Laid out like `smoke_test_js_complexity`:

- `PHP_COMPLEXITY_FIXTURE_DIR="docker/php_complexity/fixture"`;
- `PHP_COMPLEXITY_FIXTURE_FILES`: the 19 fixture files of
  [image.md](image.md#9-smoke-test-fixture), in that order;
- `PHP_COMPLEXITY_HOSTILE_LINES=("" /etc/passwd ../outside.php Calculator.php missing.php notes.txt)`.

For each platform it:

1. pipes the fixture files then the hostile lines (each followed by `\n`)
   into the canonical run line with `--platform <platform>` and
   `--user "$FOREIGN_USER"` (`501:20`):

   ```
   docker run --rm -i --pull never --network none --security-opt no-new-privileges \
     --platform <platform> --user 501:20 \
     -v "$PWD/docker/php_complexity/fixture:/src:ro" -w /src <image>:<tag>-<arch>
   ```

2. fails when the exit status is not 0;
3. checks stdout with `python3`, as for `js_complexity`: one JSON object;
   the tool versions; 25 `files` entries whose `path` is input line `i`; the
   per-file expectations and the exact `warnings` of
   [image.md](image.md#9-smoke-test-fixture) (`min_mi` compared with
   `round(..., 1)`);
4. runs `command -v git` with `--entrypoint sh` and fails if it succeeds;
5. pipes empty stdin and checks `"files": []` and `"warnings": []`, exit 0.

Any failed check prints `<reason> on <platform>` on stderr and exits 1
(`smoke_fail`). #347 checks the #346 expectations (`functions`,
`duplication` and `tool_versions.jscpd` all `null`). #351 and #352 change the
checks for their keys in the same PR as their image change (for #352:
`tool_versions.jscpd == "5.4.1"`, `13` for `dup_a.php`/`dup_b.php`, `0` for
the other normal rows and for `bootstrap.php`/`empty.php`, `null` for the
parse errors and refused lines, no `jscpd` warning).

### CircleCI

`.circleci/config.yml` gains two jobs in the `release` workflow, mirroring
the `js_complexity` ones, with the same tag filter and
`branches: ignore: /.*/`:

| Job | Executor | Steps | Requires |
|-----|----------|-------|----------|
| `build-and-publish-php-complexity-image` | `machine: image: ubuntu-2404:current` | `checkout`, then `scripts/release_image.sh <step> php_complexity` for `setup-builder`, `build`, `smoke-test`, `scan`, `publish` (step names `Set up builder`, `Build image`, `Smoke test`, `Scan image`, `Publish image`) | none |
| `update-php-complexity-description` | `machine: true` | `checkout`, `scripts/release_image.sh update-description php_complexity` | `build-and-publish-php-complexity-image` |

- `build-and-publish-release` (the CLI zip) now requires
  `build-and-publish-linux-image`, `build-and-publish-rubycritic-image`,
  `build-and-publish-js-complexity-image` **and**
  `build-and-publish-php-complexity-image`, so a CLI release is never
  published without its images.
- The four image jobs run in parallel, each with its own `setup-builder`.
- The existing jobs keep their calls unchanged.
- The `test` workflow is unchanged: no image is built on regular commits.

## 5. Docker Hub

- New files, owned by the `shell` agent with the rest of
  `docker/php_complexity/`:
  - `docker/php_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt`: one line, 1 to
    100 characters after trimming, for example
    `PDepend complexity metrics as JSON for tingle code_check php_complexity.`
    (#352 adds jscpd to it).
  - `docker/php_complexity/DOCKERHUB_DESCRIPTION.md`: what the image is for,
    the stdin/stdout contract, the canonical run line, the pinned PHP,
    PDepend (and, from #352, jscpd) versions, the tag strategy (same tag as
    tingle, no `latest`) and a link to the tingle repository.
- The `.dockerignore` from [image.md](image.md#1-location-and-files) also
  excludes both description files.
- `update-description php_complexity` validates the two files like the
  other images (missing file, empty or too-long summary → exit 1).
- The Docker Hub repository `darthjee/tingle_php_complexity` is created by
  the first `publish`; `update-description` runs after it.
- Until #352 lands, the descriptions list PHP and PDepend only. #352 updates
  them in its own PR.

## 6. Implementation doc

#347 adds `docs/agents/tingle-php-complexity-image.md` (owned by
`product-owner`), in the style of `docs/agents/tingle-js-complexity-image.md`:

1. **Header bullets:** image name, tag strategy (same semver as tingle,
   every tag published, no `latest`, `v` tags ignored, one amd64/arm64
   manifest), source (`docker/php_complexity/`, build context, the
   Composer/final stages and, from #352, the Node stage), and the pins (base
   digest, Composer stage, `composer.json`/`composer.lock`, versions table).
2. **Contract:** the canonical run line, stdin, the refused lines, the parse
   check, the staged tree, the merged JSON on stdout, stderr and exit status.
3. **Runtime user and hardening:** arbitrary uid, read-only `/src`, no
   network, no git, no Composer, no Node, writes only under `/tmp`.
4. **Release pipeline:** the selector, the steps, the smoke-test checks, the
   CircleCI jobs and their dependencies, the "no change detection" rule.
5. **Docker Hub description:** the two files and the update step.
6. **Local build:** `make php-complexity-image` and
   `--image tingle_php_complexity:dev`.
7. **Bumping versions:** from [image.md](image.md#13-bumping-versions).

`docs/agents/tingle-linux-image.md`, `docs/agents/tingle-rubycritic-image.md`
and `docs/agents/tingle-js-complexity-image.md` get a one-line pointer to the
new doc, and their note that a git tag `X.Y.Z` triggers the image jobs also
lists the `php_complexity` jobs.

## 7. Verification

- `bash -n scripts/release_image.sh` and `shellcheck` pass.
- `scripts/release_image.sh build php_complexity` and
  `scripts/release_image.sh smoke-test php_complexity` pass locally for both
  platforms (with `CIRCLE_TAG` unset, the tag comes from
  `shell/linux/VERSION`).
- `scripts/release_image.sh smoke-test bogus` prints the usage line and exits
  1; the three existing selectors still work unchanged.
