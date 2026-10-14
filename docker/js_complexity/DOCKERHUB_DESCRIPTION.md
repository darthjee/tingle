# tingle_js_complexity

The JavaScript/TypeScript complexity image behind the
`tingle code_check js_complexity` command of
[tingle](https://github.com/darthjee/tingle). It runs
[FTA](https://ftaproject.dev/) (Fast TypeScript Analyzer) and
[jscpd](https://github.com/kucherenko/jscpd) (exact-clone duplication) and
[typhonjs-escomplex](https://github.com/typhonjs-node-escomplex/typhonjs-escomplex)
(per-function complexity) on a list of JS/TS files and prints the results as
one JSON object, so tingle can check code complexity and duplication, and
drill down to each file's most complex functions, without a local Node or
Rust setup.

Supported platforms: `linux/amd64`, `linux/arm64`.

## What it contains

| Component | Version |
|-----------|---------|
| Node.js | `24.21.0` (`node:24.21.0-slim`, pinned by digest) |
| FTA | `3.1.0` (built from the `fta` crate with `cargo install --locked`) |
| jscpd | `5.4.1` (npm, pinned by `package-lock.json`) |
| typhonjs-escomplex | `0.1.0` (npm, pinned by `package-lock.json`) |

The image has no git and no Rust toolchain. It runs as uid 1000 by default;
tingle always overrides the user.

## Contract

- **stdin:** one file path per line, relative to the working directory
  (`/src`). Nothing is trimmed. Supported extensions: `js mjs cjs jsx ts mts
  cts tsx`, plus the single-file components `vue svelte astro`
  (case-insensitive). Lines that are empty, absolute, contain a `..`
  segment, are duplicates, are not a regular file under `/src` or have an
  unsupported extension are refused and never analysed.
- **stdout:** exactly one JSON object:
  `{"tool_versions": {"fta", "jscpd", "escomplex"}, "files": [...], "warnings": [...]}`.
  `files` has one entry per input line, in input order:
  `{"path", "parse_error", "fta", "duplication", "functions"}`, where `fta`
  is `{"score", "cyclo", "lines", "assessment"}` or `null` (parse error,
  refused line, or no code line). Files FTA can't parse, or that are not
  valid UTF-8, get `"parse_error": true`. `duplication` is
  `{"lines": <n>}`, the number of distinct lines of the file inside exact
  clones (jscpd, at least 50 tokens and 5 lines, only between the files
  given on stdin), or `null` (parse error, refused line, file over 1 MiB, or
  jscpd failure). `warnings` lists `{"tool", "path", "message"}` entries for
  refused lines and parse errors; a jscpd failure adds one `jscpd` warning
  without `path` and does not change the exit status. `functions` is a list
  of `{"name", "line", "cyclo", "sloc"}` (per-function data from
  typhonjs-escomplex, in source order; `[]` when the file has no function)
  or `null` (parse error, refused line, or a file escomplex can't parse,
  which adds an `escomplex` warning with its `path`). An escomplex failure
  sets every `functions` to `null`, adds one `escomplex` warning without
  `path` and does not change the exit status. With empty stdin it prints
  empty `files` and `warnings`.
- **stderr:** FTA's, jscpd's and escomplex's own output and any error
  message.
- **exit status:** `0` when the JSON was printed (even with parse errors or
  refused lines), non-zero otherwise.

### Single-file components

For `.vue`, `.svelte` and `.astro` files, only the `<script>` blocks (and the
Astro frontmatter) are analysed; the template and the styles never are. All
the blocks of a file are combined into one module, so the file gets one row,
and every line number (`functions[].line`, duplication) is the line in the
original file. Blocks with a `src` attribute or a non-JavaScript `type` (for
example `application/ld+json`) are skipped. A component with no script is a
normal row with `fta: null` (OK, score 0), `duplication: {"lines": 0}` and
`functions: []`. An unknown `lang` (for example `coffee`) or an Astro
frontmatter with no closing `---` is a parse error with an `entrypoint`
warning (`unsupported <script lang="coffee">`, `unterminated frontmatter`).

The image works under any `--user <uid>:<gid>`, with no network and a
read-only `/src`. It only writes under `/tmp`: accepted files are copied to
a staging tree (the extracted scripts, for a component) and FTA, jscpd and escomplex run there, never on `/src`.

## Usage

### Through `tingle code_check js_complexity` (preferred)

Install [tingle](https://github.com/darthjee/tingle) and run:

```bash
tingle code_check js_complexity <path>
```

### Directly with Docker

The canonical run line:

```bash
git ls-files '*.js' '*.ts' | docker run --rm -i --pull never --network none \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  -v "$PWD:/src:ro" -w /src darthjee/tingle_js_complexity:<tag>
```

## Tags

- Tags are plain semver (for example `1.0.0`): the same string as the
  matching tingle release and `X.Y.Z` git tag. tingle `X.Y.Z` uses
  `darthjee/tingle_js_complexity:X.Y.Z` by default.
- Every tingle release tag publishes this image, as one multi-platform
  manifest. There is no `latest` tag.
- The current tag is pinned in
  [`shell/linux/VERSION`](https://github.com/darthjee/tingle/blob/main/shell/linux/VERSION).

## Links

- [Repository](https://github.com/darthjee/tingle)
- [Dockerfile](https://github.com/darthjee/tingle/blob/main/docker/js_complexity/Dockerfile)
