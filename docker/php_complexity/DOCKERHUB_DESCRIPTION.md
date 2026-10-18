# tingle_php_complexity

The PHP complexity image behind the `tingle code_check php_complexity`
command of [tingle](https://github.com/darthjee/tingle). It runs
PHP's own parser, [PDepend](https://pdepend.org/) and
[jscpd](https://github.com/kucherenko/jscpd) on a list of PHP files and
prints the results as one JSON object, so tingle can check code complexity
and duplication without a local PHP, Composer or Node setup.

Supported platforms: `linux/amd64`, `linux/arm64`.

## What it contains

| Component | Version |
|-----------|---------|
| PHP | `8.5.11` (`php:8.5.11-cli-trixie`, pinned by digest) |
| PDepend | `3.0.0` (Composer, pinned by `composer.lock`) |
| jscpd | `5.4.1` (native binary, pinned by `package-lock.json`) |

Composer and Node are only used in build stages: the image has no Composer,
no Node, no `node_modules` and no git. It runs as uid 1000 by default;
tingle always overrides the user.

## Contract

- **stdin:** one file path per line, relative to the working directory
  (`/src`). Nothing is trimmed. Only `.php` files are analysed (the
  extension is compared case-insensitively). Lines that are empty,
  absolute, contain a `..` segment, are duplicates, are not a regular file
  under `/src`, have an unsupported extension or are Blade templates
  (`.blade.php`) are refused and never analysed.
- **stdout:** exactly one JSON object:
  `{"tool_versions": {"php", "pdepend", "jscpd"}, "files": [...], "warnings": [...]}`.
  `files` has one entry per input line, in input order:
  `{"path", "parse_error", "pdepend", "functions", "duplication"}`, where
  `pdepend` is `{"ccn", "max_ccn", "max_npath", "min_mi", "lloc"}` (total
  CCN, highest per-unit CCN and NPath, lowest maintainability index and
  logical lines of code) or `null` (parse error, refused line, or a file
  with no class, trait or function). Files that PHP's own parser or PDepend
  rejects get `"parse_error": true`. `functions` lists the file's methods
  and functions as `{"name", "line", "ccn", "npath"}` entries in source
  order (`Class::method` or `function`, short names), the same units that
  add up to `pdepend.ccn`; it is `[]` for a file with none and `null` for
  a parse error or refused line. `duplication` is `{"lines": n}`, the
  number of distinct lines of the file inside exact clones (jscpd) among
  the sent files (`0` when none), or `null` for a parse error, a refused
  line or a file over 1 MiB. `tool_versions.jscpd` is `"5.4.1"`.
  `warnings` lists `{"tool", "path", "message"}` entries for refused lines
  (`entrypoint`) and parse errors (`php` or `pdepend`). If jscpd fails,
  every `duplication` is `null` and one `{"tool": "jscpd", "message"}`
  warning (no `path`) is added; the run does not fail. With empty stdin it
  prints empty `files` and `warnings`.
- **stderr:** PDepend's and jscpd's own output and any error message.
- **exit status:** `0` when the JSON was printed (even with parse errors,
  refused lines or a jscpd failure), non-zero otherwise.

The image works under any `--user <uid>:<gid>`, with no network and a
read-only `/src`. It only writes under `/tmp`: accepted files are copied to
a staging tree and PDepend and jscpd run there, never on `/src`.

## Usage

### Through `tingle code_check php_complexity` (preferred)

Install [tingle](https://github.com/darthjee/tingle) and run:

```bash
tingle code_check php_complexity <path>
```

### Directly with Docker

The canonical run line:

```bash
git ls-files '*.php' | docker run --rm -i --pull never --network none \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  -v "$PWD:/src:ro" -w /src darthjee/tingle_php_complexity:<tag>
```

## Tags

- Tags are plain semver (for example `1.0.0`): the same string as the
  matching tingle release and `X.Y.Z` git tag. tingle `X.Y.Z` uses
  `darthjee/tingle_php_complexity:X.Y.Z` by default.
- Every tingle release tag publishes this image, as one multi-platform
  manifest. There is no `latest` tag.
- The current tag is pinned in
  [`shell/linux/VERSION`](https://github.com/darthjee/tingle/blob/main/shell/linux/VERSION).

## Links

- [Repository](https://github.com/darthjee/tingle)
- [Dockerfile](https://github.com/darthjee/tingle/blob/main/docker/php_complexity/Dockerfile)
