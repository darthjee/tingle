# Spec: duplication via jscpd

Sub-issue: #352. Parent: #344. Shared contracts: [README.md](README.md).

#352 adds [jscpd](https://github.com/kucherenko/jscpd) to the image, fills
`files[].duplication` and `tool_versions.jscpd` in the merged JSON, and adds
the information-only `Dup` column to the report. The image change and the
Python change land in the same PR. The duplication data never sets a level
and never changes the exit code. It mirrors `js_complexity`'s duplication
(#324), with the same jscpd version.

## 1. Image changes

- **Pin:** jscpd `5.4.1`, the version `docker/js_complexity/package.json`
  pins, so the two images stay aligned. New files
  `docker/php_complexity/package.json`:

  ```json
  {
    "name": "tingle_php_complexity",
    "private": true,
    "description": "Pinned npm tools for the tingle_php_complexity image (tingle code_check php_complexity).",
    "engines": {
      "node": "24.21.0"
    },
    "dependencies": {
      "jscpd": "5.4.1"
    }
  }
  ```

  and `package-lock.json` (lockfile v3), generated inside the Node image
  with `npm install --package-lock-only`. jscpd 5.4.1 is a Node launcher plus
  a Rust binary shipped as per-platform optional packages; the lock must
  list both `jscpd-linux-x64-gnu` and `jscpd-linux-arm64-gnu` `5.4.1`.
- **Node is build-only** (README deviation 13). The npm package's `jscpd`
  bin is `run-jscpd.js`, a Node script that spawns
  `node_modules/jscpd-linux-<arch>-gnu/bin/jscpd` with the same arguments.
  The native binary runs on its own: in the grounding image it linked only
  against `libgcc_s`, `libm` and `libc`, printed `jscpd 5.4.1` for
  `--version`, and produced the clone report below with no Node installed.
  The Dockerfile gets a stage on the same Node image as
  `docker/js_complexity/`:

  ```
  ARG NODE_IMAGE=node:24.21.0-slim@sha256:d6aa754f16b3197301076f047b5def2f02ea1dbbc2ca920407d46d7ec7f87b20
  FROM ${NODE_IMAGE} AS jscpd
  WORKDIR /opt/jscpd
  COPY package.json package-lock.json ./
  RUN npm ci --omit=dev --no-audit --no-fund \
   && test "$(ls -d node_modules/jscpd-linux-*-gnu | wc -l)" -eq 1 \
   && cp node_modules/jscpd-linux-*-gnu/bin/jscpd /opt/jscpd/jscpd
  ```

  `npm ci` fails when the lock does not match `package.json`, and installs
  only the platform package of the build platform; the `test` makes the
  build fail if that is not exactly one. The final stage adds:

  ```
  COPY --from=jscpd /opt/jscpd/jscpd /usr/local/bin/jscpd
  ```

  The final image has no Node and no `node_modules` (checked:
  `command -v node` fails).
- **Version:** `tool_versions.jscpd` is read once per run from
  `/usr/local/bin/jscpd --version`, whose output is `jscpd 5.4.1`, matched
  with `^jscpd (\S+)$` → `"5.4.1"`. A failing or unmatched `--version` is an
  entrypoint failure (exit 1, `tingle_php_complexity: cannot read the jscpd
  version`), as in `js_complexity`: the image itself is broken.
- `.dockerignore` also excludes `node_modules/`.
- The Docker Hub descriptions and
  `docs/agents/tingle-php-complexity-image.md` mention jscpd.

## 2. jscpd invocation

After PDepend, when at least one file is staged, the entrypoint removes
`/tmp/jscpd/` and runs, with the working directory `/tmp`, through
`proc_open` with an argument array:

```
/usr/local/bin/jscpd /tmp/stage \
  --reporters json --output /tmp/jscpd --report-name jscpd \
  --silent --no-tips --no-colors \
  --min-tokens 50 --min-lines 5 --mode mild --kind exact \
  --format php --formats-exts php:php \
  --no-gitignore --max-size 1mb
```

Every option that affects the result is pinned, the same values as
`js_complexity`'s except the format:

| Option | Value | Why |
|--------|-------|-----|
| `--min-tokens` | `50` | Smallest clone, in tokens (jscpd's default). |
| `--min-lines` | `5` | Smallest clone, in lines (jscpd's default). |
| `--mode` | `mild` | Token filtering mode (jscpd's default). |
| `--kind` | `exact` | Only exact (Type-1) clones. |
| `--format` | `php` | Only PHP; the staged tree holds nothing else. |
| `--formats-exts` | `php:php` | The staged files all end in `.php`. Pinned so a change of jscpd's own extension map cannot drop them. |
| `--no-gitignore` | set | The staged tree has none; pinned so nothing can hide a file. |
| `--max-size` | `1mb` (1,048,576 bytes) | Larger files are skipped by jscpd (section 3). |
| `--reporters json`, `--output`, `--report-name` | `/tmp/jscpd/jscpd.json` | The report is read from a file under `/tmp`. |
| `--silent --no-tips --no-colors` | set | Less noise on stderr. |

- jscpd prints its summary on **stdout** even with `--silent`
  (`Duplications detection: Found 1 exact clones with 13(5.58%) duplicated lines in 10 (1 formats) files.`
  and `JSON report saved to /tmp/jscpd/jscpd.json` in the grounding run).
  The entrypoint sends jscpd's stdout **and** stderr to its own stderr.
- jscpd exits 0 when it finds clones (no `--exit-code` is given).
- The staged tree holds exactly the selected files that PHP's parser
  accepted ([image.md](image.md#5-parse-check-and-staged-tree)). Files
  PDepend rejected are staged, so jscpd reads them; their clones count for
  the other file of the clone, while their own `duplication` is `null`.

## 3. Per-file duplicated lines

jscpd's JSON report, trimmed (real output of the grounding run on the
staged fixture: the `fragment` text and the `statistics.formats` block
omitted; `12.php` is `dup_a.php`, `13.php` is `dup_b.php`):

```json
{
  "duplicates": [
    {
      "format": "php",
      "kind": "exact",
      "lines": 13,
      "tokens": 129,
      "isNew": false,
      "firstFile": {
        "name": "12.php", "start": 3, "end": 15,
        "startLoc": {"line": 3, "column": 20, "position": 27},
        "endLoc": {"line": 15, "column": 1, "position": 426}
      },
      "secondFile": {
        "name": "13.php", "start": 3, "end": 15,
        "startLoc": {"line": 3, "column": 20, "position": 27},
        "endLoc": {"line": 15, "column": 1, "position": 426}
      },
      "fragment": "..."
    }
  ],
  "statistics": {
    "detectionDate": "...",
    "formats": {"...": "omitted"},
    "total": {"clones": 1, "duplicatedLines": 13, "duplicatedTokens": 129, "lines": 233, "newClones": 0, "newDuplicatedLines": 0, "percentage": 5.579399141630901, "percentageTokens": 11.365638766519824, "sources": 10, "tokens": 1135}
  }
}
```

| Field | JSON path | Notes |
|-------|-----------|-------|
| File | `duplicates[].firstFile.name`, `duplicates[].secondFile.name` | Relative to the scanned directory (`/tmp/stage`): `<n>.php`. |
| Range | `.start`, `.end` | 1-based line numbers, both inclusive (`lines` = `end - start + 1`). |

**Mapping back.** Each `name` must match `^(\d+)\.php$` for a staged `<n>`;
`<n>` is the input line. Anything else is a jscpd failure (section 5).

**Computation.** For each staged file, the entrypoint collects the set of
line numbers covered by any range of any clone in which the file appears
(as `firstFile` or `secondFile`; a clone inside one file contributes both
ranges). `duplication.lines` is the size of that set, so each line counts
once, however many clones cover it. `format`, `kind`, `lines`, `tokens`,
`startLoc`, `endLoc`, `fragment` and `statistics` are not used.

| Case | `duplication` |
|------|---------------|
| Staged, not a parse error, in no clone | `{"lines": 0}` |
| Staged, not a parse error, in one or more clones | `{"lines": <size of the set>}` |
| Staged but larger than 1,048,576 bytes (skipped by jscpd's `--max-size`) | `null` |
| `parse_error: true` (rejected by PHP, never staged; or by PDepend) | `null` |
| Refused line (never staged) | `null` |
| jscpd failed (section 5) | `null` for every file |

Files PDepend reported nothing for (`bootstrap.php`, `empty.php`) are still
read by jscpd: they get `{"lines": 0}`.

**Within the selection only.** jscpd only sees the staged tree, which holds
exactly the selected (and PHP-parsable) files. Clones with excluded or
ignored files (for example under `vendor/`) are never counted.

**Grounding results** (fixture in
[image.md](image.md#9-smoke-test-fixture)): one exact clone between
`dup_a.php` and `dup_b.php`, lines 3–15 in both, so `duplication.lines` is
13 for both, and 0 for every other analysed file. The clone starts mid-line
(column 20) on the function signature line, because the two function names
differ; the whole line still counts.

## 4. Report

The `Dup` column goes between `Lines` and `File`
([cli.md](cli.md#table)):

- Header:
  `f"{'Status':<16} {'CCN':>5}  {'Max':>5}  {'NPath':>7}  {'MI':>5}  {'Lines':>5}  {'Dup':>5}  File"`.
- Separator: `─` repeated 16, 5, 5, 7, 5, 5, 5 and 50 times.
- Level row: `duplication.lines` as `{n:>5}`; `-` when `duplication` is
  `null`. `0` and `-` are different: `0` means "checked, no clone", `-`
  means "not available".
- `PARSE` row: `-`.
- The summary does not change: no duplication total.

Example (the [cli.md](cli.md#full-example) run with #352, real values):

```
Status             CCN    Max    NPath     MI  Lines    Dup  File
──────────────── ─────  ─────  ───────  ─────  ─────  ─────  ──────────────────────────────────────────────────
✅ OK                11      7       36     54     22      0  fixture/Calculator.php
✅ OK                 6      2        2     78     11      0  fixture/Shapes.php
✅ OK                 4      3        4     66     12      0  fixture/helpers.php
✅ OK                 3      3        4     58      9     13  fixture/dup_a.php
✅ OK                 3      3        4     58      9     13  fixture/dup_b.php
...
✅ OK                 0      -        -      -      -      0  fixture/bootstrap.php
✅ OK                 0      -        -      -      -      0  fixture/empty.php
⛔ PARSE              -      -        -      -      -      -  fixture/attr_anon.php
⛔ PARSE              -      -        -      -      -      -  fixture/broken.php
⛔ PARSE              -      -        -      -      -      -  fixture/lenient.php
```

## 5. Failure handling

A jscpd failure never fails the run. It is any of:

- jscpd exits non-zero or is killed;
- `/tmp/jscpd/jscpd.json` is missing or is not valid JSON;
- `duplicates` is not a list, or an entry lacks `firstFile`/`secondFile`
  objects with `name` (str), `start` and `end` (ints, `1 <= start <= end`);
- a `name` does not map to a staged file.

Then the entrypoint sets `duplication: null` on **every** file, keeps
`tool_versions.jscpd`, adds one `warnings` entry
`{"tool": "jscpd", "message": <one-line reason>}` (no `path`), and goes on.
Its exit status is unchanged. The reasons are `js_complexity`'s:
`jscpd exited with status <s>`, `jscpd killed by <signal>`,
`jscpd report /tmp/jscpd/jscpd.json is missing`,
`jscpd report /tmp/jscpd/jscpd.json is not valid JSON`,
`jscpd report has no duplicates list`,
`jscpd report has a malformed duplicates entry`,
`jscpd reported an unknown path: <name>`.

Tingle prints, for each `jscpd` warning without a `path`:

```
Warning: jscpd failed in <image>; duplication data is not available: <message>
```

The `Dup` column then shows `-` on every row. The exit code is unchanged.
Only a PDepend or entrypoint failure is fatal (README §8).

## 6. Smoke test, docs and tests

- The smoke test (see [release.md](release.md#smoke_test_php_complexity))
  also asserts `tool_versions.jscpd == "5.4.1"`, `duplication.lines == 13`
  for `dup_a.php` and `dup_b.php`, `0` for every other normal row and for
  `bootstrap.php` and `empty.php`, `null` for the parse errors and the
  refused lines, no `jscpd` warning, and that `command -v node` fails in the
  image.
- Docs: the `Dup` column in `docs/guides/code_check/php_complexity.md`, the
  `long_help` text, and `docs/agents/tingle-php-complexity-image.md` (the
  Node stage, the jscpd pin and its bump procedure: update
  `package.json`, regenerate `package-lock.json` inside the Node image with
  `npm install --package-lock-only`, keep it equal to
  `docker/js_complexity/`'s version).
- Python tests: the column with a number, `0` and `null`; `PARSE` rows; the
  warning for a `jscpd` entry without a `path`; the exit code unchanged by
  it.
