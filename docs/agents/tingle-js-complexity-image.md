# `tingle_js_complexity` Docker image

This is the implementation view of the image that runs FTA for
`tingle code_check js_complexity`. Tingle sends a list of files on stdin and
reads one JSON object on stdout. The `darthjee/tingle` image (`tingle linux`)
is described in [tingle-linux-image.md](tingle-linux-image.md) and the
`darthjee/tingle_rubycritic` image in
[tingle-rubycritic-image.md](tingle-rubycritic-image.md). All three images
are released by the same script and the same CircleCI workflow.

The image currently runs FTA only. jscpd (#324), typhonjs-escomplex (#325)
and SFC extraction (#326) are added by those sub-issues; until then their
JSON keys are `null` and `.vue` files are refused. The full specs still live
under [specs/code_check/js_complexity/](specs/code_check/js_complexity/)
(see [image.md](specs/code_check/js_complexity/image.md) and
[release.md](specs/code_check/js_complexity/release.md)).

- **Image**: `darthjee/tingle_js_complexity` on Docker Hub.
- **Tag strategy**: the published Docker tag is exactly the plain semver git
  tag, the same string as `darthjee/tingle:X.Y.Z`,
  `darthjee/tingle_rubycritic:X.Y.Z` and the CLI release. Pushing git tag
  `X.Y.Z` publishes `darthjee/tingle_js_complexity:X.Y.Z`.
  **Every release tag publishes the image** (there is no change detection,
  see [Release pipeline](#release-pipeline)), so `tingle_js_complexity:X.Y.Z`
  always exists for CLI `X.Y.Z`. There is no `latest` tag and no build on
  regular commits. A `v`-prefixed tag triggers no release. Each published tag
  is one multi-platform manifest covering `linux/amd64` and `linux/arm64`. No
  per-architecture tags are published.
- **Default tag in the CLI**: the trimmed content of `shell/linux/VERSION`,
  the same file the release reads, so the CLI and the image always agree.
- **Source**: `docker/js_complexity/` (owned by the `shell` agent):

  | Path | Content |
  |------|---------|
  | `Dockerfile` | The three-stage image (`fta`, `deps`, final). |
  | `package.json` | `"private": true` and the Node engine (`24.21.0`). It lists no npm tool yet: `jscpd` comes with #324, `typhonjs-escomplex` with #325. |
  | `package-lock.json` | The resolved lock (lockfile v3), committed. |
  | `entrypoint.js` | The entrypoint (see [Contract](#contract)). |
  | `lib/` | Entrypoint helpers: `input.js` (stdin), `selection.js` (refused lines), `staging.js` (staged tree), `fta.js` (FTA run and parsing), `errors.js` (fatal errors). |
  | `fixture/` | The smoke-test fixture (see [Smoke test](#smoke-test)). |
  | `DOCKERHUB_SHORT_DESCRIPTION.txt`, `DOCKERHUB_DESCRIPTION.md` | The Docker Hub description (see [Docker Hub description](#docker-hub-description)). |
  | `.dockerignore` | Excludes `fixture/` and both Docker Hub description files from the build context. |

  The build context is `docker/js_complexity/` itself, not the repo root
  (`docker buildx build -f docker/js_complexity/Dockerfile docker/js_complexity`),
  so every `COPY` source is relative to that folder.
  - The `fta` stage (from `RUST_IMAGE`) builds FTA from the `fta` crate:
    `cargo install fta --version 3.1.0 --locked --root /opt/fta`. FTA is not
    installed from the `fta-cli` npm package, whose arm64 binary needs musl.
    The result, `/opt/fta/bin/fta`, links only against glibc (`libgcc_s`,
    `libm`, `libc`). The Rust toolchain never reaches the final image.
  - The `deps` stage (from `BASE_IMAGE`) copies `package.json` and
    `package-lock.json` to `/opt/tingle_js_complexity/` and runs
    `npm ci --omit=dev --no-audit --no-fund`. `npm ci` fails when the lock
    does not match `package.json`.
  - The final stage starts again from `BASE_IMAGE`, copies
    `/opt/fta/bin/fta` to `/usr/local/bin/fta`, `/opt/tingle_js_complexity/`
    from `deps`, then `entrypoint.js` and `lib/` into
    `/opt/tingle_js_complexity/`. It installs no apt package.
  - `USER 1000:1000` (the base image's `node` user), then
    `ENTRYPOINT ["node", "/opt/tingle_js_complexity/entrypoint.js"]`, no
    `CMD`.
- **Reproducible pins**: the same Dockerfile builds the same image later.
  - The base is pinned by its multi-platform index digest in a top-level
    `ARG BASE_IMAGE`
    (`node:24.21.0-slim@sha256:d6aa754f16b3197301076f047b5def2f02ea1dbbc2ca920407d46d7ec7f87b20`,
    Debian 12 bookworm, glibc), which resolves on `linux/amd64` and
    `linux/arm64`. It is not Alpine.
  - The Rust build image is pinned the same way in `ARG RUST_IMAGE`
    (`rust:1.99.0-slim-bookworm@sha256:2c3a22f0a5533ea2dd5a16627bc841228151faa2d4de2644ac9987e4a2f1f2fa`).
    `--locked` makes cargo use the crate's own `Cargo.lock`, so every Rust
    dependency is pinned.
  - The npm tools are pinned by `package.json` and `package-lock.json`.

  | Component | Version | Pinned by |
  |-----------|---------|-----------|
  | Node | `24.21.0` (`node:24.21.0-slim`, digest above) | `ARG BASE_IMAGE` |
  | Rust toolchain (build only) | `1.99.0` | `ARG RUST_IMAGE` |
  | FTA | `3.1.0` (crate `fta`) | `cargo install --version 3.1.0 --locked` |

## Contract

Tingle (and the smoke test) runs the image with the canonical line:

```sh
docker run --rm -i --pull never --network none --security-opt no-new-privileges \
  --user <uid>:<gid> -v <root>:/src:ro -w /src <image>
```

`<root>` is the resolved path for a directory, or its parent directory for a
single file.

- **stdin**: the files to analyse, one path per line, relative to `/src`.
  The entrypoint reads all of stdin; stdin that is not valid UTF-8 is a
  failure (exit 1). It splits on `\n`; a final `\n` does not start an extra
  line. Nothing is trimmed: a `\r` or a space is part of the name. Each line
  is one input line, numbered from 1. The entrypoint takes no arguments.
- **Refused lines**: every line is checked in this order; the first rule
  that matches refuses it:

  | Rule | Warning message |
  |------|-----------------|
  | The line is empty. | `empty line` |
  | The line starts with `/`. | `absolute path` |
  | A `/`-separated segment is `..`. | `path has a '..' segment` |
  | The same line appeared earlier (refused or not). | `duplicate line` |
  | `/src/<line>` does not exist, is not a regular file, or its real path (symlinks resolved) is not inside `/src`. | `not a regular file under /src` |
  | Its extension (after the last `.` of the name, lower-cased) is not one of `js mjs cjs jsx ts mts cts tsx`. | `unsupported extension` |

  A refused line is never staged and never reaches FTA. It still gets its
  `files` entry, in its position, with `parse_error: false` and `fta: null`,
  plus a warning `{"tool": "entrypoint", "path": <line>, "message": <message>}`.
  The image does not skip `.d.ts` or minified files; that is the host's job.
- **Staged tree**: each accepted line `<n>` is read from its real path and
  copied to `/tmp/stage/plain/<n>.<ext>` (`<ext>` lower-cased). FTA runs on
  `/tmp/stage`, never on `/src`. The opaque names avoid FTA's built-in
  filters (directories named `dist`, `bin` and `build`, `.d.ts`, `.min.js`,
  `.bundle.js`, hidden files, upper-case extensions), and the files are
  copied because FTA does not follow symlinks. FTA reports paths relative to
  `/tmp/stage` (`plain/6.ts`); the entrypoint parses `<n>` from the name and
  fills the `files` entry of line `<n>`. A reported path that does not map to
  a staged file is a failure (exit 1).
- **Encoding check**: before staging, the file is decoded as UTF-8 with a
  fatal decoder (a leading BOM is accepted). A file that is not valid UTF-8
  is not staged; it gets `parse_error: true` and the warning
  `{"tool": "fta", "path": <line>, "message": "file is not valid UTF-8"}`.
- **FTA run**: only when at least one file was staged. The entrypoint writes
  `/tmp/fta.json` (`{"extensions": [".mjs", ".cjs", ".mts", ".cts"]}`) and
  runs, in `/tmp` and with `DEBUG` removed from the environment:

  ```
  fta /tmp/stage --json --config-path /tmp/fta.json --score-cap 1000000000 --exclude-under 0 --include-comments false
  ```

  FTA logs files it cannot parse on stderr and drops them. Every stderr line
  matching `Failed to analyze /tmp/stage/(plain|sfc)/(\d+)\.\S*: (.*)$` sets
  `parse_error: true` on line `<n>` and adds
  `{"tool": "fta", "path": <line>, "message": <error>}` to `warnings`.
  `tool_versions.fta` comes from `fta --version` (`fta 3.1.0` gives
  `"3.1.0"`).
- **stdout**: exactly one JSON object followed by `\n`, the merged JSON:

  ```json
  {
    "tool_versions": {"fta": "3.1.0", "jscpd": null, "escomplex": null},
    "files": [
      {
        "path": "simple.js",
        "parse_error": false,
        "fta": {"score": 7.690944198185733, "cyclo": 1, "lines": 6, "assessment": "OK"},
        "duplication": null,
        "functions": null
      },
      {"path": "broken.js", "parse_error": true, "fta": null, "duplication": null, "functions": null},
      {"path": "../outside.js", "parse_error": false, "fta": null, "duplication": null, "functions": null}
    ],
    "warnings": [
      {"tool": "entrypoint", "path": "../outside.js", "message": "path has a '..' segment"},
      {"tool": "fta", "path": "broken.js", "message": "<FTA's error>"}
    ]
  }
  ```

  - `files` has exactly one entry per input line, in input order;
    `files[].path` is the input line as received.
  - `files[].fta` is `{"score", "cyclo", "lines", "assessment"}` (FTA's
    `fta_score`, `cyclo`, `line_count` and `assessment`), or `null` when the
    file is a parse error, was refused, or was dropped by FTA (a file with no
    code line, like `empty.js`).
  - `tool_versions.jscpd`, `tool_versions.escomplex`, `files[].duplication`
    and `files[].functions` are always `null` until #324 and #325.
  - With empty stdin, no tool runs and the entrypoint prints empty `files`
    and `warnings` (with `tool_versions` filled) and exits 0.
  - Nothing else is ever written to stdout. The key types and the per-file
    states are pinned in
    [image.md §7](specs/code_check/js_complexity/image.md#7-merged-json).
- **stderr**: FTA's stderr is passed through, plus the failure reason.
- **Exit status**:

  | Status | When |
  |--------|------|
  | `0` | The JSON was printed, including when some or all files are parse errors, dropped or refused. |
  | FTA's status (non-zero) | FTA exited non-zero. Nothing is printed on stdout. |
  | `1` | Any other failure: stdin not valid UTF-8, `fta --version` failing, FTA killed by a signal, FTA's stdout not a JSON array, an FTA path that does not map to a staged file, or an unexpected error. A one-line reason prefixed with `tingle_js_complexity: ` goes to stderr. Nothing is printed on stdout. |

## Runtime user and hardening

- **Arbitrary uid**: the image ends with `USER 1000:1000`, but tingle always
  overrides it with `--user <uid>:<gid>` (the smoke test uses `501:20`). The
  entrypoint calls `/usr/local/bin/fta` directly and never uses `npx`, which
  would write to `$HOME/.npm` (with a foreign uid, `HOME` is `/`).
- **Read-only `/src`**: the sources are mounted with `:ro`. The entrypoint
  writes only under `/tmp`: the staged tree, `/tmp/fta.json` and FTA's
  output.
- **No network**: the canonical line uses `--network none`; the image needs
  no network at runtime. `--security-opt no-new-privileges` is always set.
- **No git**: no stage installs git and the base image has none
  (`command -v git` fails). The final stage also has no Rust toolchain and
  no apt package.

## Release pipeline

The image is released by `scripts/release_image.sh`, the same script as the
other two images, through the image selector:

```sh
scripts/release_image.sh <subcommand> [linux|rubycritic|js_complexity]
```

- With no selector the script still uses `linux`. `setup-builder` ignores
  the selector (the buildx builder `tingle-builder` is shared). An unknown
  selector prints the usage line on stderr and exits 1.
- Per-image settings:

  | Setting | `linux` | `rubycritic` | `js_complexity` |
  |---------|---------|--------------|-----------------|
  | Image name | `darthjee/tingle` | `darthjee/tingle_rubycritic` | `darthjee/tingle_js_complexity` |
  | Dockerfile | `shell/linux/Dockerfile` | `docker/rubycritic/Dockerfile` | `docker/js_complexity/Dockerfile` |
  | Build context | `.` (repo root) | `docker/rubycritic` | `docker/js_complexity` |
  | Change detection | `shell/linux/` since the previous tag | none, always runs | none, always runs |
  | Smoke test | `smoke_test_image` | `smoke_test_rubycritic` | `smoke_test_js_complexity` |
  | Short description | `DOCKERHUB_SHORT_DESCRIPTION.txt` | `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt` | `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` |
  | Full description | `DOCKERHUB_DESCRIPTION.md` | `docker/rubycritic/DOCKERHUB_DESCRIPTION.md` | `docker/js_complexity/DOCKERHUB_DESCRIPTION.md` |

- **Tag**: `$CIRCLE_TAG` in CI, else the trimmed content of
  `shell/linux/VERSION`. In CI, `verify_version_pin` fails the job before
  building if `shell/linux/VERSION` differs from `$CIRCLE_TAG`.
- **No change detection**: for `js_complexity`, `build`, `smoke-test`, `scan`
  and `publish` never skip, even when `docker/js_complexity/` did not change
  since the previous tag. Skipping would leave `tingle_js_complexity:X.Y.Z`
  missing while CLI `X.Y.Z` points at it.
- **Platforms**: the `PLATFORMS` env var (default `linux/amd64 linux/arm64`),
  as for the other images. The `fta` stage compiles Rust, so the emulated
  platform builds much more slowly under QEMU than the native one; that is
  accepted.

### Steps

1. `setup-builder`: unchanged from the linux image (see
   [tingle-linux-image.md](tingle-linux-image.md)).
2. `build`: `verify_version_pin`, then one `docker buildx build --load` per
   platform, tagged `darthjee/tingle_js_complexity:<tag>-<arch>`, with
   `-f docker/js_complexity/Dockerfile docker/js_complexity`. These local
   tags are never pushed.
3. `smoke-test`: `smoke_test_js_complexity`, per platform (see
   [Smoke test](#smoke-test)).
4. `scan`: the pinned Trivy image against each local `<tag>-<arch>` image,
   report-only, as for the other images.
5. `publish`: `verify_version_pin`, `docker login`, one
   `docker buildx build --push` for all of `$PLATFORMS` tagged
   `darthjee/tingle_js_complexity:<tag>`, then
   `docker buildx imagetools inspect`. The job fails unless the manifest
   lists every platform. The first `publish` creates the Docker Hub
   repository.
6. `update-description`: see [Docker Hub description](#docker-hub-description).

### Smoke test

For each platform, `smoke_test_js_complexity` runs the local `<tag>-<arch>`
image with the canonical run line plus `--platform <platform>`
(`--pull never --network none --security-opt no-new-privileges`,
`--user 501:20`, `-v docker/js_complexity/fixture:/src:ro -w /src`). On
stdin it pipes the 21 fixture files, one per line, in this order:

`simple.js`, `complex.ts`, `component.tsx`, `widget.jsx`, `dup_a.js`,
`dup_b.js`, `broken.js`, `empty.js`, `short.js`, `bundle.min.js`,
`build/out.js`, `ext/a.mjs`, `ext/b.cjs`, `ext/c.mts`, `ext/d.cts`,
`ext/UPPER.JS`, `ext/types.d.ts`, `crlf.js`, `bom.ts`, `latin1.js`,
`Cart.vue`

followed by five hostile lines: an empty line, `/etc/passwd`,
`../outside.js`, a second `simple.js` and `missing.js`. The output is
checked with `python3`. The fixture:

| File | Content | Expected in the output |
|------|---------|------------------------|
| `simple.js` | Two one-line exported functions. | Normal row, `score` below 20, `assessment` `"OK"`. |
| `complex.ts` | About 260 lines of branchy TypeScript (reducer, class, rule functions). | Normal row, `score` above 60, `assessment` `"Needs improvement"`. |
| `component.tsx`, `widget.jsx` | React components with JSX. | Normal rows. |
| `dup_a.js`, `dup_b.js` | The same 20-line function body, renamed. | Normal rows. |
| `broken.js` | A syntax error. | `parse_error: true`, `fta: null`, at least one `fta` warning. |
| `empty.js` | Empty (0 bytes). | `parse_error: false`, `fta: null` (dropped by FTA). |
| `short.js` | One statement. | Normal row, `fta.lines` `1` (proves `--exclude-under 0`). |
| `bundle.min.js` | One minified line. | Normal row, `fta.lines` `1` (minified files are not skipped). |
| `build/out.js` | A small function under `build/`. | Normal row (FTA's `build` filter is bypassed). |
| `ext/a.mjs`, `ext/b.cjs`, `ext/c.mts`, `ext/d.cts`, `ext/UPPER.JS` | The same small function in each extension. | Normal rows. |
| `ext/types.d.ts` | Only `declare` statements. | Normal row (`.d.ts` is not skipped). |
| `crlf.js` | A small function with CRLF line endings. | Normal row, same `score` as `ext/a.mjs`. |
| `bom.ts` | A small function with a UTF-8 BOM. | Normal row, same `score` as `ext/c.mts`. |
| `latin1.js` | ISO-8859-1 bytes. | `parse_error: true`, `fta: null`, an `fta` warning `file is not valid UTF-8`. |
| `Cart.vue` | A Vue SFC. | Refused: `parse_error: false`, `fta: null`, an `entrypoint` warning `unsupported extension` (until #326). |

A **normal row** has `parse_error: false`, an `fta` object whose `score` is
a number (not a boolean), and no warning for its path (the `duplicate line`
warning of the hostile `simple.js` line is not counted against the fixture
row).

It asserts that:

- the fixture run exits 0;
- stdout parses as JSON and is an object;
- `tool_versions.fta` is `"3.1.0"`, and `tool_versions.jscpd` and
  `tool_versions.escomplex` are `null`;
- `files` is a list of objects and the list of `files[].path` equals the
  input lines, in order (so there is one entry per input line);
- `warnings` is a list of objects;
- the per-file expectations in the table hold;
- each of the last five entries (the hostile lines) has
  `parse_error: false`, `fta: null` and an `entrypoint` warning with the
  message from [Contract](#contract): `empty line`, `absolute path`,
  `path has a '..' segment`, `duplicate line` and
  `not a regular file under /src`;
- `command -v git` fails inside the image (run with `--network none`,
  `--platform <platform>` and `--entrypoint sh`);
- empty stdin exits 0 and prints a JSON object with `"files": []` and
  `"warnings": []`.

Any failed check prints `<reason> on <platform>` on stderr and exits 1. The
checks for jscpd (#324), escomplex (#325) and `Cart.vue` as a normal row
(#326) are added by those sub-issues, in the same PR as the image change.

### CircleCI

Two jobs in the `release` workflow, with the same tag filter as the other
image jobs (`/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/`) and
`branches: ignore: /.*/`:

| Job | Executor | Steps | Requires |
|-----|----------|-------|----------|
| `build-and-publish-js-complexity-image` | `machine: image: ubuntu-2404:current` | `checkout`, then `scripts/release_image.sh <step> js_complexity` for `setup-builder`, `build`, `smoke-test`, `scan`, `publish` | none |
| `update-js-complexity-description` | `machine: true` | `checkout`, `scripts/release_image.sh update-description js_complexity` | `build-and-publish-js-complexity-image` |

- `build-and-publish-js-complexity-image` runs in parallel with
  `build-and-publish-linux-image` and `build-and-publish-rubycritic-image`;
  each runs its own `setup-builder` (which ignores the `js_complexity`
  argument).
- `build-and-publish-release` (the CLI release zip) requires
  `build-and-publish-linux-image`, `build-and-publish-rubycritic-image`
  **and** `build-and-publish-js-complexity-image`, so a CLI release is never
  published without its images.
- The `test` workflow is unchanged: no image is built on regular commits.
- This pipeline must be merged before the tingle release tag that ships the
  `js_complexity` subcommand (#320) is pushed, because the CLI defaults to
  `darthjee/tingle_js_complexity:<tingle version>`.

## Docker Hub description

- `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt`: one line, 1 to
  100 characters after trimming.
- `docker/js_complexity/DOCKERHUB_DESCRIPTION.md`: what the image is for,
  the stdin/stdout contract, the canonical run line, the pinned Node and FTA
  versions, the tag strategy (same tag as tingle, no `latest`) and a link to
  the tingle repository. Links must be absolute URLs, because Docker Hub
  cannot resolve paths relative to the repository. Until #324 and #325 land,
  both files describe FTA only; each of those sub-issues updates them in its
  own PR.
- Both files are excluded from the build context by
  `docker/js_complexity/.dockerignore`.
- `scripts/release_image.sh update-description js_complexity` pushes both in
  one PATCH to
  `https://hub.docker.com/v2/repositories/darthjee/tingle_js_complexity/`,
  through the `update-js-complexity-description` CircleCI job. It validates
  the files as for the other images: a missing file, an empty or too-long
  short description, or a failed HTTP call exits 1. It runs after `publish`,
  so the repository exists by then.

## Local build

The root `Makefile` has a `js-complexity-image` target:

```sh
make js-complexity-image
# runs: docker build -t tingle_js_complexity:dev docker/js_complexity
```

It builds `tingle_js_complexity:dev` for the host architecture. Use it for
end-to-end tests before the image is published:

```sh
tingle code_check js_complexity <path> --image tingle_js_complexity:dev
```

To run the release steps locally without emulation, limit the platforms, for
example `PLATFORMS=linux/arm64 scripts/release_image.sh build js_complexity`
on Apple silicon.

## Bumping versions

Nothing bumps the pins automatically. Each bump is a deliberate change:

1. **Node**: update `ARG BASE_IMAGE` (tag and multi-platform index digest,
   from `docker buildx imagetools inspect node:<version>-slim`). Stay on the
   active LTS line and on Debian slim.
2. **FTA**: update `--version` in the `cargo install` line (and
   `ARG RUST_IMAGE` if the crate needs a newer Rust). Check FTA's built-in
   filters and the `Failed to analyze` log line format again.
3. **npm tools** (from #324/#325: jscpd, typhonjs-escomplex,
   `@babel/parser`): update `package.json`, then regenerate
   `package-lock.json` inside the base image with
   `npm install --package-lock-only`.
4. Re-run the smoke test on both platforms
   (`scripts/release_image.sh build js_complexity` then
   `smoke-test js_complexity`). If a tool's output shape, a pinned option or
   a fixture result changed, update this doc, the entrypoint, the Python
   parser and the smoke-test checks in the same change. Update the versions
   table in this doc.
5. Release as usual: bump with `scripts/bump-version.sh X.Y.Z` and push git
   tag `X.Y.Z`. The js_complexity image is published on every release tag,
   whether or not `docker/js_complexity/` changed.
