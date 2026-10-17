# `tingle_php_complexity` Docker image

This is the implementation view of the image that runs PHP's own parser and
PDepend for `tingle code_check php_complexity`. A caller sends a list of
files on stdin and reads one JSON object on stdout. The `darthjee/tingle`
image (`tingle linux`) is described in
[tingle-linux-image.md](tingle-linux-image.md), the
`darthjee/tingle_rubycritic` image in
[tingle-rubycritic-image.md](tingle-rubycritic-image.md) and the
`darthjee/tingle_js_complexity` image in
[tingle-js-complexity-image.md](tingle-js-complexity-image.md). All four
images are released by the same script and the same CircleCI workflow.

The image currently runs PHP's parser (the parse check) and PDepend
(complexity). It has no per-function data and no duplication data yet:
`functions`, `duplication` and `tool_versions.jscpd` are always `null` (see
[Merged JSON](#merged-json)).

- **Image**: `darthjee/tingle_php_complexity` on Docker Hub.
- **Tag strategy**: the published Docker tag is exactly the plain semver git
  tag, the same string as `darthjee/tingle:X.Y.Z`,
  `darthjee/tingle_rubycritic:X.Y.Z`, `darthjee/tingle_js_complexity:X.Y.Z`
  and the CLI release. Pushing git tag `X.Y.Z` publishes
  `darthjee/tingle_php_complexity:X.Y.Z`.
  **Every release tag publishes the image** (there is no change detection,
  see [Release pipeline](#release-pipeline)), so
  `tingle_php_complexity:X.Y.Z` always exists for CLI `X.Y.Z`. There is no
  `latest` tag and no build on regular commits. A `v`-prefixed tag triggers
  no release. Each published tag is one multi-platform manifest covering
  `linux/amd64` and `linux/arm64`. No per-architecture tags are published.
- **Source**: `docker/php_complexity/` (owned by the `shell` agent):

  | Path | Content |
  |------|---------|
  | `Dockerfile` | The two-stage image (`deps`, final). |
  | `composer.json` | `"pdepend/pdepend": "3.0.0"` (exact) and `config.platform.php` `8.5.11`. |
  | `composer.lock` | The resolved lock, committed. |
  | `entrypoint.php` | The entrypoint (see [Contract](#contract)). |
  | `lib/` | Entrypoint helpers: `input.php` (stdin and refused lines), `staging.php` (parse check and staged tree), `pdepend.php` (PDepend run, error block and summary XML), `output.php` (merged JSON encoding), `errors.php` (fatal errors). |
  | `fixture/` | The smoke-test fixture (see [Smoke test](#smoke-test)). Its `.gitattributes` (`* -text`) keeps the CRLF, BOM and ISO-8859-1 bytes as written. |
  | `DOCKERHUB_SHORT_DESCRIPTION.txt`, `DOCKERHUB_DESCRIPTION.md` | The Docker Hub description (see [Docker Hub description](#docker-hub-description)). |
  | `.dockerignore` | Excludes `fixture/`, `vendor/` and both Docker Hub description files from the build context. |

  The build context is `docker/php_complexity/` itself, not the repo root
  (`docker buildx build -f docker/php_complexity/Dockerfile docker/php_complexity`),
  so every `COPY` source is relative to that folder.
  - The `deps` stage (from `COMPOSER_IMAGE`) copies `composer.json` and
    `composer.lock` to `/opt/tingle_php_complexity/` and runs
    `composer validate --no-check-publish` then
    `composer install --no-dev --no-interaction --no-progress --classmap-authoritative`.
    `composer install` alone only warns about a stale lock;
    `composer validate` fails the build instead. The base image has no `zip`
    extension and no `unzip`, so Composer cannot install there. The
    installed tree is pure PHP: no stage compiles anything.
  - The final stage starts from `BASE_IMAGE`, copies
    `/opt/tingle_php_complexity/` (with `vendor/`) from `deps`, then
    `entrypoint.php` and `lib/` into `/opt/tingle_php_complexity/`. It
    installs no apt package.
  - `USER 1000:1000` (no such user exists in the base image; the number is
    enough), then
    `ENTRYPOINT ["php", "/opt/tingle_php_complexity/entrypoint.php"]`, no
    `CMD`.
- **Reproducible pins**: the same Dockerfile builds the same image later.
  - The base is pinned by its multi-platform index digest in a top-level
    `ARG BASE_IMAGE`
    (`php:8.5.11-cli-trixie@sha256:01a109229f4465bc9ef042d9198f09a4d9da7775a825dbd8572dcdbd8756c4d3`,
    Debian 13 trixie, glibc), which resolves on `linux/amd64` and
    `linux/arm64`. It is not Alpine.
  - The Composer build image is pinned the same way in `ARG COMPOSER_IMAGE`
    (`composer:2.10.3@sha256:af98f42dfff7c68ba8d53c2164fd9fde1087b7d449514baa38c418b1f6bc4bac`,
    PHP 8.5.11).
  - PDepend and its dependencies are pinned by `composer.json` and
    `composer.lock`, resolved for `config.platform.php` `8.5.11`.

  | Component | Version | Pinned by |
  |-----------|---------|-----------|
  | PHP | `8.5.11` (`php:8.5.11-cli-trixie`, digest above) | `ARG BASE_IMAGE` |
  | Composer (build only) | `2.10.3` | `ARG COMPOSER_IMAGE` |
  | PDepend | `3.0.0` (Composer `pdepend/pdepend`) | `composer.json` and `composer.lock` |

## Contract

The image is run (by the smoke test, and by any caller) with the canonical
line:

```sh
docker run --rm -i --pull never --network none --security-opt no-new-privileges \
  --user <uid>:<gid> -v <root>:/src:ro -w /src <image>
```

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
  | Its extension (after the last `.` of the name, lower-cased) is not `php`. | `unsupported extension` |
  | Its name, lower-cased, ends with `.blade.php`. | `Blade template` |

  A refused line is never read, never staged and never reaches PDepend. It
  still gets its `files` entry, in its position, with `parse_error: false`,
  `pdepend: null`, `functions: null` and `duplication: null`, plus a
  warning `{"tool": "entrypoint", "path": <line>, "message": <message>}`.
- **Parse check**: each accepted file is read once, from its real path, as
  bytes, and checked in-process with PHP's own parser
  (`token_get_all($code, TOKEN_PARSE)`). When it throws a `CompileError`,
  the file is a parse error: `parse_error: true`, everything else `null`, a
  warning `{"tool": "php", "path": <line>, "message": "<message> on line <line>"}`,
  and the file is **not staged**. PDepend 3.0.0 accepts some invalid code
  without any message (`return $x /;`), so this check is what makes such a
  file a parse error. The parser is the image's PHP 8.5.11. There is no
  UTF-8 check on the file content: an ISO-8859-1 file is analysed normally.
- **Staged tree**: the bytes of each accepted, parsable line `<n>` are
  copied (never symlinked) to `/tmp/stage/<n>.php`. PDepend runs on
  `/tmp/stage`, never on `/src`. The opaque names bypass PDepend's own
  filters (the case-sensitive `php,php5` suffix list, which drops
  `UPPER.PHP`, and the always-ignored `.git`, `.svn` and `CVS` directories)
  and avoid argument-length limits. The entrypoint parses `<n>` from the
  reported name and fills the `files` entry of line `<n>`; it never derives
  a path by stripping a prefix.
- **PDepend run**: only when at least one file was staged. The entrypoint
  deletes `/tmp/pdepend/summary.xml` if it exists, creates `/tmp/pdepend/`
  and `/tmp/pdepend-cache/`, and runs, with `proc_open` and an argument
  array (no shell), in `/tmp` and with `XDG_CACHE_HOME=/tmp/pdepend-cache`
  added to the environment:

  ```
  /opt/tingle_php_complexity/vendor/bin/pdepend --quiet --summary-xml=/tmp/pdepend/summary.xml /tmp/stage
  ```

  No `--suffix`, `--ignore`, `--exclude`, `--configuration` or
  `--coderank-mode` is given: staging makes the filters irrelevant. The
  working directory `/tmp` means no file of the analysed tree is read as
  configuration. `XDG_CACHE_HOME` makes PDepend's cache location
  deterministic under a foreign uid (`HOME` is `/`).
- **Files PDepend rejects**: PDepend may reject a file PHP accepted. It
  still exits 0 and prints an error block on stdout, starting with
  `The following error occurred:` or `The following errors occurred:` and
  ending at the next empty line. In the block, stack frames (`^#\d+ `) are
  skipped, and a line matching
  `^(.*?),? (?:in )?file: /tmp/stage/(\d+)\.php\.$` for a staged `<n>` makes
  line `<n>` a parse error (all its XML data discarded) with a warning
  `{"tool": "pdepend", "path": <line>, "message": <group 1>}`, for example
  `Unexpected token: #[, line: 14, col: 20`. Any other line in the block
  becomes a path-less warning `{"tool": "pdepend", "message": <line>}`; it
  is not fatal.
- **Summary XML**: for each staged line that is not a parse error, the
  counted units are every `method` of a `class` or `trait` whose `file` is
  `/tmp/stage/<n>.php` and every `function` with that `file`. Bare `method`
  elements without a `file` (enum methods, some anonymous-class methods) are
  never counted. When the file has a `metrics/files/file` entry, `pdepend`
  is:

  | Key | Value |
  |-----|-------|
  | `ccn` | Sum of the counted units' `ccn` (the total CCN; `0` with no unit). |
  | `max_ccn` | Highest `ccn` of a counted unit; `null` with no unit. |
  | `max_npath` | Highest `npath` of a counted unit; `null` with no unit. Written as a JSON integer of any size (it can exceed 2^53). |
  | `min_mi` | Lowest finite `mi` of a counted unit (unrounded); `null` with no unit or no finite value. |
  | `lloc` | The file entry's `lloc`. |

  Without a file entry (top-level code only, an empty file, only enums or
  interfaces), `pdepend` is `null`.
- **stdout**: exactly one JSON object followed by `\n`, the merged JSON,
  encoded with `JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE`:

  ```json
  {
    "tool_versions": {"php": "8.5.11", "pdepend": "3.0.0", "jscpd": null},
    "files": [
      {
        "path": "Calculator.php",
        "parse_error": false,
        "pdepend": {"ccn": 11, "max_ccn": 7, "max_npath": 36, "min_mi": 53.875623305512, "lloc": 22},
        "functions": null,
        "duplication": null
      },
      {"path": "bootstrap.php", "parse_error": false, "pdepend": null, "functions": null, "duplication": null},
      {"path": "broken.php", "parse_error": true, "pdepend": null, "functions": null, "duplication": null}
    ],
    "warnings": [
      {"tool": "php", "path": "broken.php", "message": "syntax error, unexpected token \":\", expecting variable on line 10"}
    ]
  }
  ```

  With empty stdin, PDepend does not run and the entrypoint prints empty
  `files` and `warnings` (with `tool_versions` filled) and exits 0. Nothing
  else is ever written to stdout. The key types and the per-file states are
  pinned in [Merged JSON](#merged-json).
- **stderr**: PDepend's stdout, then its stderr, are passed through, plus
  the failure reason.
- **Exit status**:

  | Status | When |
  |--------|------|
  | `0` | The JSON was printed, including when some or all files are parse errors or refused. |
  | PDepend's status (non-zero) | PDepend exited non-zero (`tingle_php_complexity: pdepend exited with status <n>` on stderr). Nothing is printed on stdout. |
  | `1` | Any other failure: stdin not valid UTF-8, the PDepend version unreadable, PDepend killed by a signal, the summary XML missing (PDepend exits 0 when it cannot write it) or not well-formed, an unknown path or a malformed entry in it, or an unexpected error. A one-line reason prefixed with `tingle_php_complexity: ` goes to stderr. Nothing is printed on stdout. |

### Merged JSON

**Keys and types**:

| Key | Type | Rule |
|-----|------|------|
| `tool_versions` | object | Always present. |
| `tool_versions.php` | str | `PHP_VERSION` (`"8.5.11"`). |
| `tool_versions.pdepend` | str | `Composer\InstalledVersions::getPrettyVersion('pdepend/pdepend')` (`"3.0.0"`). The XML's own `pdepend` attribute is not used. |
| `tool_versions.jscpd` | `null` | Always `null` in this version (reserved). |
| `files` | list | Exactly one entry per input line, in input order. |
| `files[].path` | str | The input line, exactly as received. |
| `files[].parse_error` | bool | `true` when PHP's parser or PDepend rejected the file. |
| `files[].pdepend` | object or `null` | See [Contract](#contract). `null` when `parse_error` is `true`, when the line was refused, or when PDepend listed no file entry for it. |
| `files[].functions` | `null` | Always `null` in this version (reserved). |
| `files[].duplication` | `null` | Always `null` in this version (reserved). |
| `warnings` | list | The `entrypoint` and `php` warnings in input order, then the `pdepend` warnings (per-file ones in input order, then path-less ones in output order). |
| `warnings[].tool` | str | `"entrypoint"`, `"php"` or `"pdepend"`. |
| `warnings[].message` | str | One line. |
| `warnings[].path` | str (optional) | The input line the warning is about. Absent for a path-less `pdepend` warning. |

Rules:

- **`null` means not available; `[]` or `0` means available and empty.**
- When `parse_error` is `true`, `pdepend`, `functions` and `duplication` are
  all `null`.
- **No version field, no negotiation.** The image and the CLI share the
  tingle tag. Every key above is always present.

**Per-file states**:

| State | `parse_error` | `pdepend` | `warnings` entry for the path |
|-------|---------------|-----------|-------------------------------|
| Normal | `false` | object | none |
| Rejected by PHP | `true` | `null` | `tool: "php"` |
| Rejected by PDepend | `true` | `null` | `tool: "pdepend"` |
| No class, trait or function | `false` | `null` | none |
| Refused line | `false` | `null` | `tool: "entrypoint"` |

## Runtime user and hardening

- **Arbitrary uid**: the image ends with `USER 1000:1000`, but callers
  override it with `--user <uid>:<gid>` (the smoke test uses `501:20`). The
  entrypoint calls `/opt/tingle_php_complexity/vendor/bin/pdepend` by
  absolute path and never calls Composer.
- **Read-only `/src`**: the sources are mounted with `:ro`. The entrypoint
  writes only under `/tmp`: the staged tree (`/tmp/stage/`), PDepend's
  report and captured output (`/tmp/pdepend/`) and its cache
  (`/tmp/pdepend-cache/`). The image also works with a read-only root file
  system (`--read-only --tmpfs /tmp`). The staged copies need as much space
  in `/tmp` as the selected files.
- **No network**: the canonical line uses `--network none`; the image needs
  no network at runtime. `--security-opt no-new-privileges` is always set.
- **No git, no Composer, no Node**: the final stage has no git, no Composer,
  no `zip`/`unzip`, no Node and no apt package (`command -v git` fails).

## Release pipeline

The image is released by `scripts/release_image.sh`, the same script as the
other three images, through the image selector:

```sh
scripts/release_image.sh <subcommand> [linux|rubycritic|js_complexity|php_complexity]
```

- With no selector the script still uses `linux`. `setup-builder` ignores
  the selector (the buildx builder `tingle-builder` is shared). An unknown
  selector prints the usage line on stderr and exits 1. The `linux`,
  `rubycritic` and `js_complexity` selectors are unchanged.
- Settings of the `php_complexity` selector (the other selectors are
  described in [tingle-linux-image.md](tingle-linux-image.md),
  [tingle-rubycritic-image.md](tingle-rubycritic-image.md#release-pipeline)
  and [tingle-js-complexity-image.md](tingle-js-complexity-image.md#release-pipeline)):

  | Setting | `php_complexity` |
  |---------|------------------|
  | Image name | `darthjee/tingle_php_complexity` |
  | Dockerfile | `docker/php_complexity/Dockerfile` |
  | Build context | `docker/php_complexity` |
  | Change detection | none, always runs |
  | Smoke test | `smoke_test_php_complexity` |
  | Short description | `docker/php_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` |
  | Full description | `docker/php_complexity/DOCKERHUB_DESCRIPTION.md` |

- **Tag**: `$CIRCLE_TAG` in CI, else the trimmed content of
  `shell/linux/VERSION`. In CI, `verify_version_pin` fails the job before
  building or publishing if `shell/linux/VERSION` differs from
  `$CIRCLE_TAG`.
- **No change detection**: for `php_complexity`, `build`, `smoke-test`,
  `scan` and `publish` never skip, even when `docker/php_complexity/` did
  not change since the previous tag. Skipping would leave
  `tingle_php_complexity:X.Y.Z` missing while CLI `X.Y.Z` points at it.
- **Platforms**: the `PLATFORMS` env var (default `linux/amd64 linux/arm64`),
  as for the other images. The foreign platform is built under QEMU.

### Steps

1. `setup-builder`: unchanged from the linux image (see
   [tingle-linux-image.md](tingle-linux-image.md)).
2. `build`: `verify_version_pin`, then one `docker buildx build --load` per
   platform, tagged `darthjee/tingle_php_complexity:<tag>-<arch>`, with
   `-f docker/php_complexity/Dockerfile docker/php_complexity`. These local
   tags are never pushed.
3. `smoke-test`: `smoke_test_php_complexity`, per platform (see
   [Smoke test](#smoke-test)).
4. `scan`: the pinned Trivy image against each local `<tag>-<arch>` image,
   report-only, as for the other images.
5. `publish`: `verify_version_pin`, `docker login`, one
   `docker buildx build --push` for all of `$PLATFORMS` tagged
   `darthjee/tingle_php_complexity:<tag>`, then
   `docker buildx imagetools inspect`. The job fails unless the manifest
   lists every platform. The first `publish` creates the Docker Hub
   repository.
6. `update-description`: see [Docker Hub description](#docker-hub-description).

### Smoke test

For each platform, `smoke_test_php_complexity` runs the local
`<tag>-<arch>` image with the canonical run line plus `--platform <platform>`:

```sh
docker run --rm -i --pull never --network none --security-opt no-new-privileges \
  --platform <platform> --user 501:20 \
  -v "$PWD/docker/php_complexity/fixture:/src:ro" -w /src <image>:<tag>-<arch>
```

On stdin it pipes the 19 fixture files of `PHP_COMPLEXITY_FIXTURE_FILES`,
one per line, in this order:

`Anon.php`, `CVS/legacy.php`, `Calculator.php`, `Modern.php`, `Shapes.php`,
`UPPER.PHP`, `attr_anon.php`, `bom.php`, `bootstrap.php`, `broken.php`,
`crlf.php`, `dup_a.php`, `dup_b.php`, `empty.php`, `helpers.php`,
`latin1.php`, `lenient.php`, `page.php`, `welcome.blade.php`

followed by the six `PHP_COMPLEXITY_HOSTILE_LINES`: an empty line,
`/etc/passwd`, `../outside.php`, a second `Calculator.php`, `missing.php`
(does not exist) and `notes.txt` (a fixture file that is not PHP). The
output is checked with `python3`. The fixture:

| File | What it proves | `parse_error` | `pdepend` (`ccn`, `max_ccn`, `max_npath`, `round(min_mi, 1)`, `lloc`) |
|------|----------------|---------------|------------------------------------------------------------------------|
| `Anon.php` | A method returning an anonymous class: the bare `label` is not counted. | `false` | 2, 2, 4, 66.3, 6 |
| `CVS/legacy.php` | PDepend's `CVS` filter is bypassed. | `false` | 2, 2, 2, 79.5, 2 |
| `Calculator.php` | A class with methods of CCN 1, 3 and 7. | `false` | 11, 7, 36, 53.9, 22 |
| `Modern.php` | PHP 8.3 syntax (enum, readonly class, typed constant); enum methods not counted. | `false` | 2, 1, 1, 79.3, 11 |
| `Shapes.php` | An interface, two classes and a trait in one file. | `false` | 6, 2, 2, 77.6, 11 |
| `UPPER.PHP` | Upper-case extension; PDepend's suffix filter is bypassed. | `false` | 2, 2, 2, 77.7, 2 |
| `attr_anon.php` | Valid PHP that PDepend rejects. | `true` | `null` |
| `bom.php` | UTF-8 BOM. | `false` | 2, 2, 2, 79.5, 2 |
| `bootstrap.php` | Top-level code only. | `false` | `null` |
| `broken.php` | A syntax error. | `true` | `null` |
| `crlf.php` | CRLF line endings. | `false` | 2, 2, 2, 79.5, 2 |
| `dup_a.php`, `dup_b.php` | Two near-identical functions. | `false` | 3, 3, 4, 58.1, 9 |
| `empty.php` | Empty (0 bytes). | `false` | `null` |
| `helpers.php` | Two functions plus top-level closures (not counted). | `false` | 4, 3, 4, 66.5, 12 |
| `latin1.php` | ISO-8859-1 bytes. | `false` | 1, 1, 1, 83.1, 2 |
| `lenient.php` | Invalid PHP that PDepend accepts. | `true` | `null` |
| `page.php` | Mixed HTML/PHP with one inline function. | `false` | 2, 2, 2, 89.7, 4 |
| `welcome.blade.php` | A Blade template, refused. | `false` | `null` |
| the six hostile lines | Refused. | `false` | `null` |

It asserts that:

- the fixture run exits 0;
- stdout parses as JSON and is an object;
- `tool_versions.php` is `"8.5.11"`, `tool_versions.pdepend` is `"3.0.0"`
  and `tool_versions.jscpd` is present and `null`;
- `files` is a list of 25 objects and the list of `files[].path` equals the
  input lines, in order;
- the per-file `parse_error` and `pdepend` values in the table hold: the
  `pdepend` object has exactly the keys `ccn`, `max_ccn`, `max_npath`,
  `min_mi` and `lloc`, the ints are ints (not booleans), and `min_mi` is
  compared with `round(..., 1)`;
- `functions` and `duplication` are present and `null` on every entry;
- `warnings` is exactly this list, in this order:

  | `tool` | `path` | `message` |
  |--------|--------|-----------|
  | `php` | `broken.php` | `syntax error, unexpected token ":", expecting variable on line 10` |
  | `php` | `lenient.php` | `syntax error, unexpected token ";" on line 5` |
  | `entrypoint` | `welcome.blade.php` | `Blade template` |
  | `entrypoint` | (empty line) | `empty line` |
  | `entrypoint` | `/etc/passwd` | `absolute path` |
  | `entrypoint` | `../outside.php` | `path has a '..' segment` |
  | `entrypoint` | `Calculator.php` | `duplicate line` |
  | `entrypoint` | `missing.php` | `not a regular file under /src` |
  | `entrypoint` | `notes.txt` | `unsupported extension` |
  | `pdepend` | `attr_anon.php` | `Unexpected token: #[, line: 14, col: 20` |

- `command -v git` fails inside the image (run with `--network none`,
  `--platform <platform>` and `--entrypoint sh`);
- empty stdin exits 0 and prints a JSON object with `"files": []` and
  `"warnings": []`.

Any failed check prints `<reason> on <platform>` on stderr and exits 1.

### CircleCI

Two jobs in the `release` workflow, with the same tag filter as the other
image jobs (`/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/`) and
`branches: ignore: /.*/`:

| Job | Executor | Steps | Requires |
|-----|----------|-------|----------|
| `build-and-publish-php-complexity-image` | `machine: image: ubuntu-2404:current` | `checkout`, then `scripts/release_image.sh <step> php_complexity` for `setup-builder`, `build`, `smoke-test`, `scan`, `publish` (step names `Set up builder`, `Build image`, `Smoke test`, `Scan image`, `Publish image`) | none |
| `update-php-complexity-description` | `machine: true` | `checkout`, `scripts/release_image.sh update-description php_complexity` (step `Update Docker Hub description`) | `build-and-publish-php-complexity-image` |

- `build-and-publish-php-complexity-image` runs in parallel with
  `build-and-publish-linux-image`, `build-and-publish-rubycritic-image` and
  `build-and-publish-js-complexity-image`; each runs its own
  `setup-builder` (which ignores the `php_complexity` argument).
- `build-and-publish-release` (the CLI release zip) requires
  `build-and-publish-linux-image`, `build-and-publish-rubycritic-image`,
  `build-and-publish-js-complexity-image` **and**
  `build-and-publish-php-complexity-image`, so a CLI release is never
  published without its images.
- The `test` workflow builds no image: nothing is built on regular commits.

## Docker Hub description

- `docker/php_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt`: one line, 1 to
  100 characters after trimming
  (`PDepend complexity metrics as JSON for tingle code_check php_complexity.`).
- `docker/php_complexity/DOCKERHUB_DESCRIPTION.md`: what the image is for,
  the supported platforms, the pinned PHP and PDepend versions, the
  stdin/stdout contract (refused lines, the `pdepend` object, the reserved
  `null` keys, warnings, exit status), the canonical run line, the tag
  strategy (same tag as tingle, no `latest`) and links to the tingle
  repository and the Dockerfile. Links must be absolute URLs, because Docker
  Hub cannot resolve paths relative to the repository.
- Both files are excluded from the build context by
  `docker/php_complexity/.dockerignore`.
- `scripts/release_image.sh update-description php_complexity` pushes both
  in one PATCH to
  `https://hub.docker.com/v2/repositories/darthjee/tingle_php_complexity/`,
  through the `update-php-complexity-description` CircleCI job. It validates
  the files as for the other images: a missing file, an empty or too-long
  short description, or a failed HTTP call exits 1. It runs after `publish`,
  so the repository exists by then.

## Local build

The root `Makefile` has a `php-complexity-image` target:

```sh
make php-complexity-image
# runs: docker build -t tingle_php_complexity:dev docker/php_complexity
```

It builds `tingle_php_complexity:dev` for the host architecture. Use it for
end-to-end tests before the image is published, for example with the
canonical run line:

```sh
git ls-files '*.php' | docker run --rm -i --pull never --network none \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  -v "$PWD:/src:ro" -w /src tingle_php_complexity:dev
```

To run the release steps locally without emulation, limit the platforms, for
example `PLATFORMS=linux/arm64 scripts/release_image.sh build php_complexity`
on Apple silicon.

## Bumping versions

Nothing bumps the pins automatically. Each bump is a deliberate change:

1. **PHP**: update `ARG BASE_IMAGE` (tag and multi-platform index digest,
   from `docker buildx imagetools inspect php:<version>-cli-trixie`). Keep
   the Debian variant with amd64 and arm64. A new PHP minor changes what the
   parse check accepts.
2. **Composer**: update `ARG COMPOSER_IMAGE` (tag and digest).
3. **PDepend**: update the version in `composer.json` and the
   `config.platform.php` value, then regenerate `composer.lock` inside the
   pinned Composer image, from `docker/php_complexity/`, with
   `--no-install` so that no `vendor/` is written into the repository:

   ```sh
   docker run --rm --user "$(id -u):$(id -g)" -e COMPOSER_HOME=/tmp/composer \
     -v "$PWD/docker/php_complexity:/app" -w /app \
     composer:2.10.3@sha256:af98f42dfff7c68ba8d53c2164fd9fde1087b7d449514baa38c418b1f6bc4bac \
     sh -c 'composer init --no-interaction --name=tingle/php_complexity --type=project \
       && composer config platform.php 8.5.11 \
       && composer require --no-interaction --no-progress --no-install pdepend/pdepend:3.0.0'
   ```

   Check the summary XML shape, the error block format and the bare-method
   behaviour (see [Contract](#contract)) again.
4. Re-run the smoke test on both platforms
   (`scripts/release_image.sh build php_complexity` then
   `smoke-test php_complexity`). If a tool's output shape, a pinned option or
   a fixture result changed, update this doc, the entrypoint and the
   smoke-test checks in the same change. Update the versions table in this
   doc.
5. Release as usual: bump with `scripts/bump-version.sh X.Y.Z` and push git
   tag `X.Y.Z`. The php_complexity image is published on every release tag,
   whether or not `docker/php_complexity/` changed.
