# Spec: the `tingle_js_complexity` Docker image

Sub-issue: #318 (FTA only). Extended by #324 (jscpd), #325 (escomplex) and
#326 (SFC extraction). Parent: #315. Shared contracts: [README.md](README.md).

The image runs FTA, and later jscpd and typhonjs-escomplex, for
`tingle code_check js_complexity`. Tingle sends a list of files on stdin and
reads one JSON document on stdout. This spec covers the image source, the
entrypoint contract, the merged JSON and the local build. Publishing is in
[release.md](release.md).

## 1. Location and files

The image lives in `docker/js_complexity/`, owned by the **`shell`** agent,
like `docker/rubycritic/`. #318 adds the folder to
`docs/agents/folder-structure.md` and to the `shell` agent's scope in
`.claude/agents/shell.md`.

| Path | Content | Added by |
|------|---------|----------|
| `docker/js_complexity/Dockerfile` | The image (section 2). | #318 |
| `docker/js_complexity/package.json` | `"private": true`, the Node engine, and the exact (`=`) versions of the npm tools: none in #318, `jscpd` from #324, `typhonjs-escomplex` from #325. | #318 |
| `docker/js_complexity/package-lock.json` | The resolved lock (section 3), committed. | #318 |
| `docker/js_complexity/entrypoint.js` | The entrypoint (sections 4 to 8). It may `require` helper modules from `docker/js_complexity/lib/`. | #318 |
| `docker/js_complexity/fixture/` | The smoke-test fixture (section 9). | #318 |
| `docker/js_complexity/.dockerignore` | Excludes `fixture/` (and, from #319, the Docker Hub description files) from the build context. | #318 |

The build context is `docker/js_complexity/` itself:

```
docker buildx build -t <tag> docker/js_complexity
```

## 2. Dockerfile

- **Base image:** `node:24.21.0-slim`, Debian 12 (bookworm), glibc. Node 24
  ("Krypton") is the active LTS line at the time of writing (24.21.0,
  released 2026-09-07; Node 26 is not LTS yet). It is pinned by its
  multi-platform index digest in a top-level `ARG BASE_IMAGE`:

  ```
  ARG BASE_IMAGE=node:24.21.0-slim@sha256:d6aa754f16b3197301076f047b5def2f02ea1dbbc2ca920407d46d7ec7f87b20
  ```

  The index resolves on `linux/amd64` and `linux/arm64`. It is **not**
  Alpine (see [README.md](README.md#11-deviations-from-315), item 1).
- **FTA stage.** FTA is built from the `fta` crate, not installed from the
  `fta-cli` npm package, whose arm64 binary needs musl (README deviation 1):

  ```
  ARG RUST_IMAGE=rust:1.99.0-slim-bookworm@sha256:2c3a22f0a5533ea2dd5a16627bc841228151faa2d4de2644ac9987e4a2f1f2fa
  FROM ${RUST_IMAGE} AS fta
  RUN cargo install fta --version 3.1.0 --locked --root /opt/fta
  ```

  `--locked` uses the crate's own `Cargo.lock`, so every Rust dependency is
  pinned. The result, `/opt/fta/bin/fta`, links only against glibc
  (`libgcc_s`, `libm`, `libc`), which the Debian base provides. The Rust
  toolchain never reaches the final image. Grounding build times: 29 s native
  (arm64), 100 s emulated (amd64 on an arm64 host).
- **npm stage** (`deps`, from `BASE_IMAGE`): copies `package.json` and
  `package-lock.json` to `/opt/tingle_js_complexity/` and runs
  `npm ci --omit=dev --no-audit --no-fund`. `npm ci` fails when the lock does
  not match `package.json`, so the image holds exactly the locked versions.
- **Final stage** (from `BASE_IMAGE`): copies `/opt/fta/bin/fta` to
  `/usr/local/bin/fta`, `/opt/tingle_js_complexity/` from `deps`, and the
  entrypoint (with `lib/`). It installs no apt package.
- **No git.** No stage installs git and the base image has none
  (`command -v git` fails).
- **User:** the image ends with `USER 1000:1000` (the base image's `node`
  user). Tingle always overrides it with `--user <uid>:<gid>`.
- **Entrypoint:** `ENTRYPOINT ["node", "/opt/tingle_js_complexity/entrypoint.js"]`
  and no `CMD`. The entrypoint takes no arguments.
- The entrypoint calls each tool's binary directly
  (`/usr/local/bin/fta`, `node_modules/.bin/jscpd`, its own escomplex
  wrapper). It never uses `npx`, which writes to `$HOME/.npm` (with a
  foreign uid, `HOME` is `/` and not writable).

## 3. Pinned versions

| Component | Version | Pinned by | Added by |
|-----------|---------|-----------|----------|
| Node | `24.21.0` (npm `11.19.0`) | `ARG BASE_IMAGE` (tag + digest) | #318 |
| Rust toolchain (build only) | `1.99.0` | `ARG RUST_IMAGE` (tag + digest) | #318 |
| FTA | `3.1.0` (crate `fta`) | `cargo install --version 3.1.0 --locked` | #318 |
| jscpd | `5.4.1`, with `jscpd-linux-x64-gnu` and `jscpd-linux-arm64-gnu` `5.4.1` | `package.json` (`5.4.1`) + `package-lock.json` | #324 |
| typhonjs-escomplex | `0.1.0`, with `@typhonjs/babel-parser` `0.2.0` and `@babel/parser` `7.29.9` | `package.json` (`0.1.0`) + `package-lock.json` | #325 |

- `package-lock.json` (lockfile v3) is generated inside the base image with
  `npm install --package-lock-only`. jscpd 5.4.1 is a Rust binary shipped as
  per-platform optional dependencies; the lock lists all of them, and
  `npm ci` installs only the one for the build platform. The lock must keep
  both `jscpd-linux-x64-gnu` and `jscpd-linux-arm64-gnu`.
- typhonjs-escomplex 0.1.0 (2018) depends on `@babel/parser` with a `^7`
  range. The lock fixes it (`7.29.9` at the time of writing). Bumping it is a
  deliberate change, like a tool bump.

## 4. Entrypoint input

The entrypoint (Node, standard library plus the locked tools) is the only
process tingle talks to. It runs in `/src`, which is read-only.

### Lines

- It reads all of stdin as bytes. Stdin that is not valid UTF-8 is an
  entrypoint failure (exit 1, section 8).
- It splits stdin on `\n`. A final `\n` does not start an extra line. Each
  resulting line is one **input line**, numbered from 1 (`<n>`). Nothing is
  trimmed: a `\r` or a space is part of the name.
- It receives no arguments.

### Refused lines (defence in depth)

Tingle's host-side selection never sends any of these lines. The entrypoint
still checks every line, in this order; the first rule that matches refuses
it:

| Rule | Warning message |
|------|-----------------|
| The line is empty. | `empty line` |
| The line starts with `/`. | `absolute path` |
| A `/`-separated segment is `..`. | `path has a '..' segment` |
| The same line appeared earlier (refused or not). | `duplicate line` |
| `/src/<line>` does not exist, is not a regular file, or its real path (symlinks resolved) is not inside `/src`. | `not a regular file under /src` |
| Its extension (the part after the last `.` of the name, lower-cased) is not in the image's list: `js mjs cjs jsx ts mts cts tsx`, plus `vue svelte astro` from #326. | `unsupported extension` |

A refused line is never staged and never reaches a tool. It still gets its
`files` entry, in its position, with `parse_error: false`, `fta: null`,
`duplication: null` and `functions: null`, plus one `warnings` entry
`{"tool": "entrypoint", "path": <line>, "message": <message>}`. So "one
entry per input line" always holds. Tingle reports such a file as `OK` with
score 0 (see [subcommand.md](subcommand.md#8-edge-cases)).

The image does not skip `.d.ts` or minified files: that is the host's job
([file-selection.md](file-selection.md)). A declaration file that reaches
the image is analysed like any `.ts` file.

## 5. Staged tree

FTA walks a directory and takes no file list, so the entrypoint stages the
accepted lines and runs **every tool on the staged tree, never on `/src`**.
That way each tool sees exactly the selected files.

- **Copies.** Each accepted line `<n>` is read from `/src/<line>` (its real
  path) and written to `/tmp/stage/plain/<n>.<ext>`, `<ext>` being the
  lower-cased extension. FTA does not follow symlinks (a tree of symlinks
  gave `[]` in the grounding run), so the files are copied.
- **Opaque names.** The relative path is not kept: FTA always drops
  directories named `dist`, `bin` and `build`, names ending in `.d.ts`,
  `.min.js` or `.bundle.js`, hidden files, and extensions in upper case, and
  none of this can be turned off (README deviation 2). `plain/<n>.<ext>`
  avoids all of it.
- **SFC subtree** (#326): the virtual module of an SFC on line `<n>` is
  written to `/tmp/stage/sfc/<n>.<ext>.ts` (or `.js`), `<ext>` being `vue`,
  `svelte` or `astro`. It is never staged in `plain/`, so a real `Cart.vue.ts`
  and the virtual module of `Cart.vue` can never collide. See
  [sfc.md](sfc.md#3-virtual-module).
- **Mapping back.** Every tool reports paths relative to the directory it
  scanned (`plain/6.ts`, `sfc/5.vue.ts`). The entrypoint parses `<n>` from
  that name and writes the result on the `files` entry of input line `<n>`.
  It never derives a path by stripping a prefix. A tool path that does not
  map to a staged file is an entrypoint failure (exit 1).
- **Encoding check.** Before staging, the entrypoint decodes the file as
  UTF-8 with a fatal decoder (`new TextDecoder("utf-8", {fatal: true})`); a
  leading BOM is accepted. A file that is not valid UTF-8 is **not staged**.
  It gets `parse_error: true` and a `warnings` entry
  `{"tool": "fta", "path": <line>, "message": "file is not valid UTF-8"}`.
  FTA itself drops such a file without any message (section 10), so this
  check is what makes it a `PARSE` row.
- **Only `/tmp`.** The entrypoint writes only under `/tmp`: the staged tree,
  the FTA config file and the tool reports. It works with a read-only root
  file system (checked with `--read-only --tmpfs /tmp`).

## 6. FTA invocation

The entrypoint writes `/tmp/fta.json`:

```json
{"extensions": [".mjs", ".cjs", ".mts", ".cts"]}
```

and runs, with the working directory `/tmp` and the variable `DEBUG` removed
from the environment (FTA switches to debug logging when it is set):

```
fta /tmp/stage --json --config-path /tmp/fta.json --score-cap 1000000000 --exclude-under 0 --include-comments false
```

| Option | Value | Why |
|--------|-------|-----|
| `--config-path /tmp/fta.json` | the file above | FTA's own list is `.js .jsx .ts .tsx`; a config file **adds** to it. With an explicit path FTA never reads an `fta.json` from the scanned tree. |
| `--score-cap` | `1000000000` | FTA exits 1 when a file scores above the cap (default 1000). |
| `--exclude-under` | `0` | FTA drops files with at most this many code lines (default 6). With `0` only files with no code line are dropped. |
| `--include-comments` | `false` | FTA's default, pinned: comment lines are not counted in `line_count`. |
| `--json` | | JSON on stdout. `--output-limit` only applies to the table output. |

- FTA is run only when at least one file was staged. With nothing staged,
  every `fta` is `null`.
- FTA's stdout is captured and parsed. FTA's stderr is captured, scanned
  (below), then written to the entrypoint's stderr.
- **Parse errors.** FTA does not list them in its JSON. For each file it
  cannot parse (it tries TS, then TSX, or the reverse for `.jsx`/`.tsx`), it
  logs a line ending in
  `Failed to analyze /tmp/stage/<plain|sfc>/<n>.<rest>: <error>` on stderr,
  drops the file and still exits 0. The entrypoint matches every stderr line
  against `Failed to analyze /tmp/stage/(plain|sfc)/(\d+)\.\S*: (.*)$`, sets
  `parse_error: true` on line `<n>`, and adds
  `{"tool": "fta", "path": <line>, "message": <error>}` to `warnings`.
- **FTA failure.** A non-zero FTA status, or stdout that is not a JSON array,
  is fatal (section 8).
- `tool_versions.fta` is the version printed by `fta --version`
  (`fta 3.1.0` → `"3.1.0"`), run once per invocation.

The jscpd options are pinned in
[duplication.md](duplication.md#2-jscpd-invocation) (#324) and the
escomplex options in [details.md](details.md#2-escomplex-wrapper) (#325).
Both run on the same staged tree, after FTA.

## 7. Merged JSON

On success, stdout holds exactly one JSON object followed by `\n`. Nothing
else is written to stdout.

```json
{
  "tool_versions": {"fta": "3.1.0", "jscpd": null, "escomplex": null},
  "files": [ <one entry per input line, in input order> ],
  "warnings": [ <warning entries> ]
}
```

### Keys and types

| Key | Type | Rule |
|-----|------|------|
| `tool_versions` | object | Always present. |
| `tool_versions.fta` | str | FTA's version. |
| `tool_versions.jscpd` | str or `null` | jscpd's version (`"5.4.1"`) from #324; `null` before. |
| `tool_versions.escomplex` | str or `null` | typhonjs-escomplex's version (`"0.1.0"`) from #325; `null` before. |
| `files` | list | Exactly one entry per input line, in input order. |
| `files[].path` | str | The input line, exactly as received. |
| `files[].parse_error` | bool | `true` when FTA could not parse the file, the file is not valid UTF-8, or (from #326) the SFC cannot be extracted. |
| `files[].fta` | object or `null` | `null` when `parse_error` is `true`, when FTA dropped the file, or when the line was refused. |
| `files[].fta.score` | number | FTA's `fta_score`, as reported (unrounded). |
| `files[].fta.cyclo` | int ≥ 0 | FTA's `cyclo`. |
| `files[].fta.lines` | int ≥ 0 | FTA's `line_count`: non-blank, non-comment lines. |
| `files[].fta.assessment` | str | FTA's `assessment`: `"OK"`, `"Could be better"` or `"Needs improvement"`. |
| `files[].duplication` | object or `null` | `{"lines": <int ≥ 0>}` from #324; `null` before #324, when jscpd failed, when the file was not analysed by jscpd, or when `parse_error` is `true`. See [duplication.md](duplication.md#3-per-file-duplicated-lines). |
| `files[].functions` | list or `null` | From #325, a list of `{"name": str, "line": int ≥ 1, "cyclo": int ≥ 1, "sloc": int ≥ 1}` in source order; `[]` when the file has no function. `null` before #325, when escomplex failed on the file, or when `parse_error` is `true`. See [details.md](details.md#3-functions). |
| `warnings` | list | Entries in the order they were produced. |
| `warnings[].tool` | str | `"entrypoint"`, `"fta"`, `"jscpd"` or `"escomplex"`. |
| `warnings[].message` | str | One line. |
| `warnings[].path` | str (optional) | The input line the warning is about. Absent for a warning about a whole tool run. |

Rules:

- **`null` means not available; `[]` or `0` means available and empty.**
  `"duplication": {"lines": 0}` means jscpd ran on the file and found no
  clone. `"functions": []` means escomplex parsed the file and found no
  function.
- When `parse_error` is `true`, `fta`, `duplication` and `functions` are all
  `null`.
- **No version field, no negotiation.** The image and the CLI share the
  tingle tag. For tingle, a missing key or a value of the wrong type is an
  unparsable-output error (exit 1). Unknown extra keys are ignored by tingle.
- #318 emits every key above. #324 and #325 only fill in their parts. They
  never add or rename a key.

### Per-file states

| State | `parse_error` | `fta` | `warnings` entry for the path | Report |
|-------|---------------|-------|-------------------------------|--------|
| Normal | `false` | object | none (or a secondary-tool one) | normal row |
| Parse error | `true` | `null` | `tool: "fta"` (or `"entrypoint"` for an SFC that cannot be extracted) | `⛔ PARSE` row |
| Dropped by FTA (no code line) | `false` | `null` | none | `OK`, score 0 |
| Refused line (section 4) | `false` | `null` | `tool: "entrypoint"` | `OK`, score 0 |

### Example

From the grounding run (FTA part only, as #318 emits it):

```json
{
  "tool_versions": {"fta": "3.1.0", "jscpd": null, "escomplex": null},
  "files": [
    {
      "path": "complex.ts",
      "parse_error": false,
      "fta": {"score": 71.25291592210418, "cyclo": 136, "lines": 245, "assessment": "Needs improvement"},
      "duplication": null,
      "functions": null
    },
    {
      "path": "simple.js",
      "parse_error": false,
      "fta": {"score": 7.690944198185733, "cyclo": 1, "lines": 6, "assessment": "OK"},
      "duplication": null,
      "functions": null
    },
    {"path": "broken.js", "parse_error": true, "fta": null, "duplication": null, "functions": null},
    {"path": "latin1.js", "parse_error": true, "fta": null, "duplication": null, "functions": null},
    {"path": "empty.js", "parse_error": false, "fta": null, "duplication": null, "functions": null},
    {"path": "../outside.js", "parse_error": false, "fta": null, "duplication": null, "functions": null}
  ],
  "warnings": [
    {"tool": "entrypoint", "path": "../outside.js", "message": "path has a '..' segment"},
    {"tool": "fta", "path": "latin1.js", "message": "file is not valid UTF-8"},
    {"tool": "fta", "path": "broken.js", "message": "Error { error: (36..37, Expected(\",\", \"numeric literal (1, 1)\")) }"}
  ]
}
```

## 8. Exit status, empty input and encoding

| Status | When |
|--------|------|
| `0` | The JSON was printed, including when some or all files are parse errors, dropped or refused, and when jscpd or escomplex failed. |
| FTA's status (non-zero) | FTA exited non-zero. Nothing is printed on stdout. |
| `1` | Any other entrypoint failure: stdin not valid UTF-8, `fta --version` failing, FTA killed by a signal, FTA's stdout not a JSON array, an FTA entry that does not map to a staged file, or an unexpected error. A one-line reason prefixed with `tingle_js_complexity: ` goes to stderr. Nothing is printed on stdout. |

- With empty stdin (no input line), no tool runs and the entrypoint prints
  `{"tool_versions": {...}, "files": [], "warnings": []}` (with the versions
  filled as usual) and exits 0. Tingle never starts the container with an
  empty list, but the image must handle it.
- A jscpd or escomplex failure is never fatal. Its handling is in
  [duplication.md](duplication.md#5-failure-handling) and
  [details.md](details.md#6-failure-handling).

### Encoding and line endings

Recorded in the grounding run (section 10):

- **CRLF** (`crlf.js`) and **UTF-8 BOM** (`bom.ts`): FTA, jscpd and
  escomplex handle both. FTA gave the same score and `line_count` as for the
  same code with LF and no BOM (`7.27`, 6 lines). jscpd clone ranges and
  escomplex function lines are the same line numbers as in an editor, also
  with CRLF and a BOM.
- **Not valid UTF-8** (`latin1.js`): FTA drops the file silently
  (`read_to_string` fails, no log line); escomplex, reading it with
  replacement characters, still returns functions. The entrypoint's own
  check (section 5) makes it a `PARSE` row, so no tool's data is shown for
  it.
- Line counts follow FTA's `line_count` as reported. Tingle never recounts.

## 9. Smoke-test fixture

`docker/js_complexity/fixture/` holds the grounding set. #318 creates every
file; the expectations of later sub-issues are checked once they land.

| File | Content | Expected (#318: `fta`) | Expected from #324 (`duplication.lines`) | Expected from #325 (`functions`) |
|------|---------|------------------------|-------------------------------------------|----------------------------------|
| `simple.js` | Two one-line exported functions (7 physical lines). | score < 20, `"OK"` | `0` | 2 entries |
| `complex.ts` | ~260 lines: a reducer with a `switch`, a `Store` class with try/catch, a scoring loop and 12 branchy rule functions. Uses types, interfaces, generics and `??`, but no `<T>value` type assertion. | score > 60, `"Needs improvement"` | `0` | ≥ 20 entries, one named `reducer`, some named `Store.<method>` |
| `component.tsx` | A React function component with a hook and JSX. | normal row | `0` | ≥ 1 |
| `widget.jsx` | A React component with JSX and a ternary. | normal row | `0` | 1 |
| `dup_a.js`, `dup_b.js` | The same 20-line function body (renamed), at different offsets. | normal rows | ≥ 20 on both | 3 each |
| `broken.js` | `export function broken( {` … (syntax error). | `parse_error: true`, a `tool: "fta"` warning | `null` | `null` |
| `empty.js` | Empty (0 bytes). | `parse_error: false`, `fta: null` (dropped) | `0` | `[]` |
| `short.js` | One statement (`export const s = 1;`). | normal row, `lines` 1 (proves `--exclude-under 0`) | `0` | `[]` |
| `bundle.min.js` | One minified line with three functions. | normal row, `lines` 1 (the image does not skip minified files) | `0` | 3 entries |
| `build/out.js` | A small function under `build/`. | normal row (proves FTA's `/build` filter is bypassed) | `0` | 1 |
| `ext/a.mjs`, `ext/b.cjs`, `ext/c.mts`, `ext/d.cts` | The same small function in each extension. | normal rows | `0` | 1 each |
| `ext/UPPER.JS` | The same small function, upper-case extension. | normal row | `0` | 1 |
| `ext/types.d.ts` | Only `declare` statements. | normal row (the image does not skip `.d.ts`) | `0` | `[]` |
| `crlf.js` | A small function, CRLF line endings. | normal row, same score as `ext/a.mjs` | `0` | 1, at line 1 |
| `bom.ts` | A small function, UTF-8 BOM. | normal row, same score as `ext/c.mts` | `0` | 1, at line 1 |
| `latin1.js` | ISO-8859-1 bytes in a comment and a string. | `parse_error: true`, warning `file is not valid UTF-8` | `null` | `null` |
| `Cart.vue` | `<template>`, `<script setup lang="ts">` with a `computed` (lines 8–21), `<style scoped>`. | refused: `unsupported extension` (until #326); from #326 a normal row | from #326: `0` | from #326: 1 entry at line 13 |

The smoke test pipes this list into the canonical run line, followed by five
hostile lines: an empty line, `/etc/passwd`, `../outside.js`, a second
`simple.js` and `missing.js`. It runs with `-v <fixture>:/src:ro` and
`--user 501:20`, and asserts that:

- the exit status is 0, and stdout parses as one JSON object;
- `tool_versions.fta` is `"3.1.0"` (and, from #324/#325, `jscpd` is
  `"5.4.1"` and `escomplex` is `"0.1.0"`; before, both are `null`);
- `files` has one entry per input line, and `files[i].path` is input line
  `i`;
- the per-file expectations in the table hold;
- each hostile line has `fta: null`, `parse_error: false` and an
  `entrypoint` warning with the message from section 4;
- `command -v git` fails inside the image (with `--entrypoint sh`);
- empty stdin prints `"files": []` and `"warnings": []`, with exit 0.

## 10. Grounding run

The run behind these specs was throwaway: a scratch directory and a
throwaway image, nothing committed. Repeat it when bumping a version.

**Versions:** `node:24.21.0-slim` (digest above, Debian 12.15), npm
`11.19.0`, FTA `3.1.0` (crate, built with Rust `1.99.0`; cross-checked
against `fta-cli` 3.1.0's amd64 binary: identical results on every file),
jscpd `5.4.1`, typhonjs-escomplex `0.1.0` with `@babel/parser` `7.29.9`.

**Environment:** the tools were installed in a networked build step, then
every run used

```
docker run --rm -i --network none --read-only --tmpfs /tmp:exec \
  --user 501:20 -v <fixture>:/src:ro -w /src <throwaway image> sh /run.sh < stdin.txt
```

All three tools worked with no network, a read-only `/src`, a read-only
root file system and a foreign uid (`HOME=/`). None tried to reach the
network or wrote outside `/tmp` (checked with `find / -xdev -newer`).

**Commands:**

```
fta /tmp/stage --json --config-path /tmp/fta.json --score-cap 1000000000 --exclude-under 0 --include-comments false
jscpd /tmp/stage <options from duplication.md>
node <escomplex wrapper from details.md> <staged files>
```

Each run staged the 21 fixture files (stdin order: `bom.ts`, `broken.js`,
`build/out.js`, `bundle.min.js`, `Cart.vue`, `complex.ts`, …) as
`/tmp/stage/plain/<n>.<ext>`.

**FTA output** (trimmed: one entry, the `halstead` block omitted; the file
is `complex.ts`, input line 6). It is a JSON array sorted by score, one
object per analysed file, `file_name` relative to the scanned directory:

```json
[
  {
    "file_name": "plain/6.ts",
    "cyclo": 136,
    "halstead": {"...": "omitted"},
    "line_count": 245,
    "fta_score": 71.25291592210418,
    "assessment": "Needs improvement"
  }
]
```

| Report item | FTA JSON path | Type |
|-------------|---------------|------|
| `FTA` (level) | `[i].fta_score` | float |
| `Cyclo` | `[i].cyclo` | int |
| `Lines` | `[i].line_count` | int |
| `Assessment` | `[i].assessment` | str |
| path | `[i].file_name` | str, relative to the scanned directory |

**Assessment bands** (FTA 3.1.0 `get_assessment`): `> 60` "Needs
improvement", `> 50` "Could be better", else "OK". They confirm the
`50/60` defaults; `75` is tingle's.

**Per-fixture results** (FTA score rounded to 2 decimals; Dup from jscpd with
the pinned options; Functions = escomplex entries):

| File | FTA score | Assessment | Cyclo | Lines | Parse error | Dropped | Dup lines | Functions |
|------|-----------|------------|-------|-------|-------------|---------|-----------|-----------|
| `simple.js` | 7.69 | OK | 1 | 6 | no | no | 0 | 2 |
| `complex.ts` | 71.25 | Needs improvement | 136 | 245 | no | no | 0 | 20 |
| `component.tsx` | 37.43 | OK | 3 | 18 | no | no | 0 | 3 |
| `widget.jsx` | 31.02 | OK | 3 | 11 | no | no | 0 | 1 |
| `dup_a.js` | 35.03 | OK | 9 | 23 | no | no | 22 | 3 |
| `dup_b.js` | 35.10 | OK | 9 | 23 | no | no | 22 | 3 |
| `broken.js` | – | – | – | – | yes (FTA warning) | – | 0 | escomplex error |
| `empty.js` | – | – | – | – | no | yes | 0 | 0 |
| `short.js` | 3.48 | OK | 1 | 1 | no | no | 0 | 0 |
| `bundle.min.js` | 6.19 | OK | 5 | 1 | no | no | 0 | 3 |
| `build/out.js` | 7.27 | OK | 2 | 6 | no | no | 0 | 1 |
| `ext/a.mjs`, `ext/b.cjs`, `ext/c.mts`, `ext/d.cts`, `ext/UPPER.JS` | 7.27 | OK | 2 | 6 | no | no | 0 | 1 |
| `ext/types.d.ts` | 6.82 | OK | 1 | 6 | no | no | 0 | 0 |
| `crlf.js` | 7.27 | OK | 2 | 6 | no | no | 0 | 1 |
| `bom.ts` | 7.27 | OK | 2 | 6 | no | no | 0 | 1 |
| `latin1.js` | – | – | – | – | silently dropped by FTA | – | 0 | 1 |
| `Cart.vue` (as a padded virtual module, #326) | 30.66 | OK | 3 | 11 | no | no | 0 | 1 (line 13) |

With the relative-path layout instead of `plain/<n>.<ext>`, FTA also dropped
`build/out.js`, `bundle.min.js`, `ext/types.d.ts` and `ext/UPPER.JS`, and,
with FTA's default `--exclude-under 6`, every file under 7 code lines.

## 11. Runtime environment

Tingle runs the image with the canonical line from
[README.md](README.md#9-image-contract-summary). The image must work under
that line for any `<uid>:<gid>`, with no network and with `/src` read-only.
It writes only under `/tmp`.

## 12. Local build

The root `Makefile` gets a `js-complexity-image` target next to
`rubycritic-image` (added to `.PHONY`), with one recipe line:

```sh
docker build -t tingle_js_complexity:dev docker/js_complexity
```

It builds `tingle_js_complexity:dev` for the host architecture, used with
`tingle code_check js_complexity <path> --image tingle_js_complexity:dev`
before the image is published.

Verification for #318: `docker buildx build --platform linux/amd64
docker/js_complexity` and the same for `linux/arm64` succeed, and the smoke
test passes against `tingle_js_complexity:dev`.

## 13. Bumping versions

Nothing bumps the pins automatically. Each bump is a deliberate change:

1. **Node:** update `ARG BASE_IMAGE` (tag and index digest, from
   `docker buildx imagetools inspect node:<version>-slim`). Stay on the
   active LTS line and on Debian slim.
2. **FTA:** update `--version` in the `cargo install` line (and
   `ARG RUST_IMAGE` if the crate needs a newer Rust). Check FTA's built-in
   filters and log line format (section 6) again.
3. **jscpd / typhonjs-escomplex / `@babel/parser`:** update `package.json`,
   then regenerate `package-lock.json` inside the base image with
   `npm install --package-lock-only`.
4. Re-run the grounding commands (section 10) and the smoke test on both
   platforms. If a tool's output shape, a pinned option or a result in the
   fixture table changed, update this spec (or, once the specs are removed,
   `docs/agents/tingle-js-complexity-image.md`), the entrypoint and the
   Python parser in the same change.
