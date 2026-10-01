# `tingle_rubycritic` Docker image

This is the implementation view of the image that runs RubyCritic for
`tingle code_check rubycritic`. Tingle sends a list of files on stdin and
reads one JSON object on stdout. The `darthjee/tingle` image (`tingle linux`)
is described in [tingle-linux-image.md](tingle-linux-image.md); both images
are released by the same script and the same CircleCI workflow.

- **Image**: `darthjee/tingle_rubycritic` on Docker Hub.
- **Tag strategy**: the published Docker tag is exactly the plain semver git
  tag, the same string as `darthjee/tingle:X.Y.Z` and as the CLI release.
  Pushing git tag `X.Y.Z` publishes `darthjee/tingle_rubycritic:X.Y.Z`.
  **Every release tag publishes the image** (there is no change detection,
  see [Release pipeline](#release-pipeline)), so `tingle_rubycritic:X.Y.Z`
  always exists for CLI `X.Y.Z`. There is no `latest` tag and no build on
  regular commits. A `v`-prefixed tag triggers no release. Each published tag
  is one multi-platform manifest covering `linux/amd64` and `linux/arm64`. No
  per-architecture tags are published.
- **Default tag in the CLI**: the trimmed content of `shell/linux/VERSION`,
  the same file the release reads, so the CLI and the image always agree.
- **Source**: `docker/rubycritic/` (owned by the `shell` agent):

  | Path | Content |
  |------|---------|
  | `Dockerfile` | The two-stage image. |
  | `Gemfile` | `source "https://rubygems.org"` and `gem "rubycritic", "5.0.0"`, nothing else. |
  | `Gemfile.lock` | The resolved lock, committed. |
  | `entrypoint.rb` | The entrypoint wrapper (see [Contract](#contract)). |
  | `fixture/` | The smoke-test fixture (see [Smoke test](#smoke-test)). |
  | `DOCKERHUB_SHORT_DESCRIPTION.txt`, `DOCKERHUB_DESCRIPTION.md` | The Docker Hub description (see [Docker Hub description](#docker-hub-description)). |
  | `.dockerignore` | Excludes `fixture/` and both Docker Hub description files from the build context. |

  The build context is `docker/rubycritic/` itself, not the repo root
  (`docker buildx build -f docker/rubycritic/Dockerfile docker/rubycritic`),
  so every `COPY` source is relative to that folder.
  - A `build` stage installs `build-essential` (`--no-install-recommends`,
    version pinned, `12.12` at the time of writing) and runs
    `bundle install`. The build tools are needed because `prism` compiles a
    native extension.
  - The final stage starts again from `BASE_IMAGE`, copies the installed
    gems (`/usr/local/bundle`) and the Gemfile pair from `build`, and
    installs no apt package. It has no compiler.
  - Both stages set `BUNDLE_GEMFILE=/opt/tingle_rubycritic/Gemfile` and
    `BUNDLE_FROZEN=true`, so `bundle install` fails if the lock does not
    match the Gemfile, and the runtime loads exactly the locked versions.
  - `ENTRYPOINT ["ruby", "/opt/tingle_rubycritic/entrypoint.rb"]`, no `CMD`.
    The base image's `LANG=C.UTF-8` is kept, so sources are read as UTF-8.
- **Reproducible pins**: the same Dockerfile builds the same image later.
  - The base is pinned by its multi-platform index digest in a top-level
    `ARG BASE_IMAGE`
    (`ruby:3.3.12-slim@sha256:379ffc9ca20cae2655cb80cac53ee23e1e7d859c03a4cceb7f567d6ce4873cee`,
    Debian trixie), which resolves on `linux/amd64` and `linux/arm64`.
  - Every gem is pinned by `Gemfile.lock`. The lock lists the platforms
    `aarch64-linux` and `x86_64-linux`, and not `ruby`, so the same lock
    installs on both architectures.

  | Component | Version | Pinned by |
  |-----------|---------|-----------|
  | Ruby | `3.3.12` (`ruby:3.3.12-slim`, digest above) | `ARG BASE_IMAGE` |
  | Bundler | `2.5.22` (shipped with the base image) | `BUNDLED WITH` in `Gemfile.lock` |
  | `rubycritic` | `5.0.0` | `Gemfile` (`= 5.0.0`) and `Gemfile.lock` |
  | `flog` | `4.9.4` | `Gemfile.lock` |
  | `flay` | `2.14.4` | `Gemfile.lock` |
  | `reek` | `6.5.0` | `Gemfile.lock` |
  | `parser` | `3.3.12.0` | `Gemfile.lock` |
  | `prism` | `1.9.0` | `Gemfile.lock` |
  | `ruby_parser` | `3.22.0` | `Gemfile.lock` |

## Contract

Tingle (and the smoke test) runs the image with the canonical line:

```sh
docker run --rm -i --pull never --network none --security-opt no-new-privileges \
  --user <uid>:<gid> -v <root>:/src:ro -w /src <image>
```

`<root>` is the resolved path for a directory, or its parent directory for a
single file. Tingle pulls the image beforehand when it is missing.

- **stdin**: the files to analyse, one path per line, relative to `/src`,
  UTF-8. Blank lines are ignored. Duplicates are kept once, at their first
  position. The entrypoint takes no arguments.
- **stdout**: exactly one JSON object followed by `\n`: the object read from
  RubyCritic's `/tmp/out/report.json`, with one extra top-level key,
  `parse_errors`. Each `parse_errors` entry is
  `{"path": <the line as received>, "message": <first line of the error>}`,
  in input order. When no path survives the pre-parse (or stdin had no
  paths), RubyCritic is not run and the entrypoint prints
  `{"metadata":null,"analysed_modules":[],"score":null,"parse_errors":[...]}`.
  Nothing else is ever written to stdout.
- **stderr**: everything else. RubyCritic prints its progress lines, the
  "Churn will not be calculated" notice and `Score: NN.NN` on stdout, so the
  entrypoint redirects RubyCritic's stdout and stderr to its own stderr.
- **Exit status**:

  | Status | When |
  |--------|------|
  | `0` | The JSON was printed, including when some or all files are in `parse_errors`. |
  | RubyCritic's status (non-zero) | RubyCritic exited non-zero. Nothing is printed on stdout. |
  | `1` | `report.json` is missing or not valid JSON after a successful RubyCritic run, or any other entrypoint failure. A one-line reason goes to stderr. Nothing is printed on stdout. |

- **Run**: with at least one surviving path, the entrypoint runs
  `rubycritic --format json --no-browser -p /tmp/out <paths>` in `/src`,
  under the locked bundle, with the paths as separate arguments in input
  order. RubyCritic is never run with zero paths, because it would then
  analyse `.`.
- **Why the entrypoint pre-parses**: RubyCritic 5.0.0 aborts the whole run
  on the first file with a syntax error (Reek raises
  `Reek::Errors::SyntaxError`, RubyCritic exits 1 and writes no report). So
  the entrypoint first parses every path with the parser Reek uses,
  configured as Reek configures it
  (`Reek::Source::SourceCode.new(source: File.read(path), origin: path).syntax_tree`).
  Any `StandardError` or `ScriptError` (syntax errors, invalid UTF-8,
  unreadable or missing files) puts the path in `parse_errors`, and that path
  is not passed to RubyCritic. A file with a syntax error is therefore not a
  failure.
- The JSON field paths and meanings used by tingle are pinned in the
  `rubycritic` subcommand spec
  ([subcommand.md](specs/code_check/rubycritic/subcommand.md#5-rubycritic-json-contract)).

## Runtime user and hardening

- **Arbitrary uid**: the image ends with `USER 1000:1000`, but tingle always
  overrides it with `--user <uid>:<gid>` (the host user, for example `501:20`
  on macOS). The image works for any uid without a passwd entry: it writes
  only under `/tmp` (world-writable), and the run needs no extra environment
  (checked with `--user 501:20` and the inherited `HOME=/`).
- **Read-only `/src`**: the sources are mounted with `:ro`. RubyCritic writes
  its report to `/tmp/out` (`-p /tmp/out`), never under `/src`.
- **No network**: the canonical line uses `--network none`; the image needs
  no network at runtime. `--security-opt no-new-privileges` is always set.
- **No git**: neither stage installs git and the base image has none
  (`command -v git` fails). Without git, RubyCritic skips version control:
  it computes no churn, and git's "dubious ownership" error cannot happen
  under a foreign uid. RubyCritic then prints
  `RubyCritic can provide more feedback if you use a Git, Mercurial or Perforce repository. Churn will not be calculated.`
  on its stdout, which the entrypoint sends to stderr.

## Release pipeline

The image is released by `scripts/release_image.sh`, the same script as the
linux image, through an optional image selector:

```sh
scripts/release_image.sh <subcommand> [linux|rubycritic]
```

- The selector defaults to `linux`, so calls without it keep releasing
  `darthjee/tingle`. `setup-builder` ignores it (the buildx builder
  `tingle-builder` is shared). An unknown selector prints the usage line on
  stderr and exits 1.
- Per-image settings:

  | Setting | `linux` | `rubycritic` |
  |---------|---------|--------------|
  | Image name | `darthjee/tingle` | `darthjee/tingle_rubycritic` |
  | Dockerfile | `shell/linux/Dockerfile` | `docker/rubycritic/Dockerfile` |
  | Build context | `.` (repo root) | `docker/rubycritic` |
  | Change detection | `shell/linux/` since the previous tag | none, always runs |
  | Smoke test | `smoke_test_image` | `smoke_test_rubycritic` |
  | Short description | `DOCKERHUB_SHORT_DESCRIPTION.txt` | `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt` |
  | Full description | `DOCKERHUB_DESCRIPTION.md` | `docker/rubycritic/DOCKERHUB_DESCRIPTION.md` |

- **Tag**: `$CIRCLE_TAG` in CI, else the trimmed content of
  `shell/linux/VERSION`. In CI, `verify_version_pin` fails the job before
  building if `shell/linux/VERSION` differs from `$CIRCLE_TAG`.
- **No change detection**: for `rubycritic`, `build`, `smoke-test`, `scan`
  and `publish` never skip, even when `docker/rubycritic/` did not change
  since the previous tag. Skipping would leave `tingle_rubycritic:X.Y.Z`
  missing while CLI `X.Y.Z` defaults to it.
- **Platforms**: the `PLATFORMS` env var (default `linux/amd64 linux/arm64`),
  as for the linux image.

### Steps

1. `setup-builder`: unchanged from the linux image (see
   [tingle-linux-image.md](tingle-linux-image.md)).
2. `build`: `verify_version_pin`, then one `docker buildx build --load` per
   platform, tagged `darthjee/tingle_rubycritic:<tag>-<arch>`, with
   `-f docker/rubycritic/Dockerfile docker/rubycritic`. These local tags are
   never pushed.
3. `smoke-test`: `smoke_test_rubycritic`, per platform (see
   [Smoke test](#smoke-test)).
4. `scan`: the pinned Trivy image against each local `<tag>-<arch>` image,
   report-only, as for the linux image.
5. `publish`: `verify_version_pin`, `docker login`, one
   `docker buildx build --push` for all of `$PLATFORMS` tagged
   `darthjee/tingle_rubycritic:<tag>`, then
   `docker buildx imagetools inspect`. The job fails unless the manifest
   lists every platform. The first `publish` creates the Docker Hub
   repository.
6. `update-description`: see [Docker Hub description](#docker-hub-description).

### Smoke test

For each platform, `smoke_test_rubycritic` runs the local `<tag>-<arch>`
image with `--platform <platform>` and the canonical run line
(`--network none`, `-v docker/rubycritic/fixture:/src:ro`,
`--user 501:20`), pipes the fixture list on stdin (one file per line), and
checks the JSON with `python3`. The fixture:

| File | Content | Expected in the output |
|------|---------|------------------------|
| `simple.rb` | A class with one trivial method. | In `analysed_modules`, `complexity` below 5, `rating` `"A"`. |
| `complex.rb` | One method with nested conditionals, loops and a `case`. | In `analysed_modules`, `complexity` above 50. |
| `dup_a.rb`, `dup_b.rb` | Two classes with the same method body. | Both in `analysed_modules` with `duplication` above 0. |
| `broken.rb` | A method with an unclosed parameter list. | Only in `parse_errors`. |
| `empty.rb` | An empty file. | In `analysed_modules`, `complexity` `0.0`, `methods_count` `0`. |
| `constants_only.rb` | A module with two constants and no method. | In `analysed_modules`, `complexity` `0.0`, `methods_count` `0`. |

It asserts that:

- the exit status is 0 and stdout parses as one JSON object;
- `metadata.rubycritic.version` is `"5.0.0"`;
- the set of `analysed_modules[].path` is exactly the six non-broken files;
- `parse_errors[].path` is exactly `["broken.rb"]`;
- `score` is a number between 0 and 100;
- the per-file expectations in the table hold;
- `command -v git` fails inside the image (with `--entrypoint sh`);
- empty stdin prints the empty object (`metadata` null, empty
  `analysed_modules`, `score` null, empty `parse_errors`) with exit 0.

Any failed check prints `<reason> on <platform>` on stderr and exits 1.

### CircleCI

Two jobs in the `release` workflow, with the same tag filter as the existing
ones (`/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/`) and
`branches: ignore: /.*/`:

| Job | Executor | Steps | Requires |
|-----|----------|-------|----------|
| `build-and-publish-rubycritic-image` | `machine: image: ubuntu-2404:current` | `checkout`, then `scripts/release_image.sh <step> rubycritic` for `setup-builder`, `build`, `smoke-test`, `scan`, `publish` | none |
| `update-rubycritic-description` | `machine: true` | `checkout`, `scripts/release_image.sh update-description rubycritic` | `build-and-publish-rubycritic-image` |

- `build-and-publish-rubycritic-image` runs in parallel with
  `build-and-publish-linux-image`; each runs its own `setup-builder`.
- `build-and-publish-release` (the CLI release zip) requires **both**
  `build-and-publish-linux-image` and `build-and-publish-rubycritic-image`,
  so a CLI release is never published without its images.
- The existing linux jobs keep calling the script without a selector.
- The `test` workflow is unchanged: no image is built on regular commits.

## Docker Hub description

- `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt`: one line, 1 to 100
  characters after trimming.
- `docker/rubycritic/DOCKERHUB_DESCRIPTION.md`: what the image is for, the
  stdin/stdout contract, the canonical run line, the pinned Ruby and
  RubyCritic versions, the tag strategy (same tag as tingle, no `latest`) and
  a link to the tingle repository. Links must be absolute URLs, because
  Docker Hub cannot resolve paths relative to the repository.
- Both files are excluded from the build context by
  `docker/rubycritic/.dockerignore`.
- `scripts/release_image.sh update-description rubycritic` pushes both in one
  PATCH to `https://hub.docker.com/v2/repositories/darthjee/tingle_rubycritic/`,
  through the `update-rubycritic-description` CircleCI job. It validates the
  files as for the linux image: a missing file, an empty or too-long short
  description, or a failed HTTP call exits 1. It runs after `publish`, so the
  repository exists by then.

## Local build

The root `Makefile` has a `rubycritic-image` target:

```sh
make rubycritic-image
# runs: docker build -t tingle_rubycritic:dev docker/rubycritic
```

It builds `tingle_rubycritic:dev` for the host architecture. Use it for
end-to-end tests before the image is published:

```sh
tingle code_check rubycritic <path> --image tingle_rubycritic:dev
```

To run the release steps locally without emulation, limit the platforms, for
example `PLATFORMS=linux/arm64 scripts/release_image.sh build rubycritic` on
Apple silicon.

## Bumping versions

Nothing bumps the pins automatically. Bumping Ruby or RubyCritic is a
deliberate change:

1. **Ruby**: update `ARG BASE_IMAGE` (tag and multi-platform index digest,
   for example from `docker buildx imagetools inspect ruby:3.3.N-slim`).
   Check that the pinned `build-essential` version still resolves in the new
   base image.
2. **RubyCritic**: update the version in `Gemfile`, then regenerate
   `Gemfile.lock` inside the base image with
   `bundle lock --add-platform x86_64-linux aarch64-linux` and
   `bundle lock --remove-platform ruby`. Update the versions table in this
   doc.
3. Re-run the smoke test on both platforms (`scripts/release_image.sh build
   rubycritic` then `smoke-test rubycritic`). If the JSON shape changed,
   update the JSON contract (the subcommand spec, or this doc once the specs
   are removed), the Python parser and the smoke-test checks in the same
   change.
4. Release as usual: bump with `scripts/bump-version.sh X.Y.Z` and push git
   tag `X.Y.Z`. The rubycritic image is published on every release tag,
   whether or not `docker/rubycritic/` changed.
