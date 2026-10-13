# Spec: duplication via jscpd

Sub-issue: #324. Parent: #315. Shared contracts: [README.md](README.md).

#324 adds [jscpd](https://github.com/kucherenko/jscpd) to the image, fills
`files[].duplication` and `tool_versions.jscpd` in the merged JSON, and adds
the information-only `Dup` column to the report. The image change and the
Python change land in the same PR. The duplication data never sets a level
and never changes the exit code.

## 1. Image changes

- `docker/js_complexity/package.json` gets `"jscpd": "5.4.1"` (exact), and
  `package-lock.json` is regenerated (see
  [image.md](image.md#3-pinned-versions)). jscpd 5.4.1 is a Rust binary
  shipped as per-platform optional packages; the lock must list both
  `jscpd-linux-x64-gnu` and `jscpd-linux-arm64-gnu` `5.4.1`.
- `tool_versions.jscpd` becomes `"5.4.1"`, read from
  `node_modules/jscpd/package.json`.
- The Docker Hub description mentions jscpd.

## 2. jscpd invocation

After FTA, when at least one file is staged, the entrypoint runs, with the
working directory `/tmp`:

```
/opt/tingle_js_complexity/node_modules/.bin/jscpd /tmp/stage \
  --reporters json --output /tmp/jscpd --report-name jscpd \
  --silent --no-tips --no-colors \
  --min-tokens 50 --min-lines 5 --mode mild --kind exact \
  --format javascript,typescript,jsx,tsx \
  --formats-exts "javascript:js,mjs,cjs;typescript:ts,mts,cts;jsx:jsx;tsx:tsx" \
  --cross-formats js-ts \
  --no-gitignore --max-size 1mb
```

Every option that affects the result is pinned, even where it equals
jscpd's default (from `jscpd --debug`):

| Option | Value | jscpd 5.4.1 default | Why |
|--------|-------|---------------------|-----|
| `--min-tokens` | `50` | `50` | Smallest clone, in tokens. |
| `--min-lines` | `5` | `5` | Smallest clone, in lines. |
| `--mode` | `mild` | `mild` | Token filtering mode. |
| `--kind` | `exact` | all kinds the other options enable | Only exact (Type-1) clones. |
| `--format` | `javascript,typescript,jsx,tsx` | every format | Only the formats tingle sends. |
| `--formats-exts` | the map above | `.js`→javascript, `.ts`→typescript, ... | Without it, jscpd does not read `.mjs/.cjs/.mts/.cts`. |
| `--cross-formats` | `js-ts` | none | Without it, a clone between a `.js` and a `.ts` file is not found (checked: `1.mjs` vs `2.cts` gave no clone without it, one with it). |
| `--no-gitignore` | set | reads `.gitignore` | The staged tree has none; pinned so nothing can hide a file. |
| `--max-size` | `1mb` (1,048,576 bytes) | `1mb` | Larger files are skipped by jscpd (section 3). |
| `--reporters json`, `--output`, `--report-name` | `/tmp/jscpd/jscpd.json` | `console`, `report/` | The report is read from a file under `/tmp`. |
| `--silent --no-tips --no-colors` | set | | Less noise on stderr. |

- jscpd prints its summary line on **stdout** even with `--silent`. The
  entrypoint sends jscpd's stdout **and** stderr to its own stderr.
- jscpd exits 0 when it finds clones (no `--exit-code` is given).
- SFC virtual modules (#326) are staged as `.ts`/`.js` under
  `/tmp/stage/sfc/`, so they are read as TypeScript or JavaScript, not with
  jscpd's own Vue/Svelte/Astro support.

## 3. Per-file duplicated lines

jscpd's JSON report, trimmed (from the grounding run: the `fragment` text,
`startLoc`/`endLoc` details and the whole `statistics` block omitted):

```json
{
  "duplicates": [
    {
      "format": "javascript",
      "kind": "exact",
      "lines": 23,
      "tokens": 162,
      "firstFile": {"name": "plain/9.js", "start": 3, "end": 25},
      "secondFile": {"name": "plain/10.js", "start": 1, "end": 23}
    }
  ],
  "statistics": {"...": "omitted"}
}
```

| Field | JSON path | Notes |
|-------|-----------|-------|
| File | `duplicates[].firstFile.name`, `duplicates[].secondFile.name` | Relative to the scanned directory (`/tmp/stage`), POSIX separators. |
| Range | `.start`, `.end` | 1-based line numbers, both inclusive (`lines` = `end - start + 1`). |

**Computation.** For each staged file, the entrypoint collects the set of
line numbers covered by any range of any clone in which the file appears
(as `firstFile` or `secondFile`; a clone inside one file contributes both
ranges). `duplication.lines` is the size of that set, so each line counts
once, however many clones cover it. `format`, `kind`, `lines`, `tokens`,
`fragment` and `statistics` are not used.

| Case | `duplication` |
|------|---------------|
| Staged, read by jscpd, in no clone | `{"lines": 0}` |
| Staged, in one or more clones | `{"lines": <size of the set>}` |
| Staged but larger than 1,048,576 bytes (skipped by jscpd's `--max-size`) | `null` |
| `parse_error: true` (FTA cannot parse it, or not valid UTF-8) | `null` |
| Refused line (never staged) | `null` |
| jscpd failed (section 5) | `null` for every file |

A file FTA dropped (no code line) is still read by jscpd: it gets
`{"lines": 0}`.

**Within the selection only.** jscpd only sees the staged tree, which holds
exactly the selected files. Clones with excluded or ignored files (for
example under `node_modules`) are never counted.

**Line numbers.** The ranges are the file's own line numbers, with CRLF line
endings and with a UTF-8 BOM (checked: a 22-line clone at lines 3–26 in a
CRLF file and 4–27 in a file with a BOM). For an SFC, the virtual module
keeps the original line numbers (see [sfc.md](sfc.md#4-line-map)).

**Grounding results** (fixture in [image.md](image.md#9-smoke-test-fixture)):
one exact clone between `dup_a.js` (lines 3–25) and `dup_b.js` (lines 1–23),
so `duplication.lines` is 23 for both, and 0 for every other staged file. The
clone starts mid-line (column 31) on the function signature line of
`dup_a.js`, because the two function names differ; the whole line still
counts.

## 4. Report

The `Dup` column goes between `Lines` and `Assessment`
([subcommand.md](subcommand.md#6-report)):

- Header: `f"{'Status':<16} {'FTA':>5}  {'Cyclo':>5}  {'Lines':>5}  {'Dup':>5}  {'Assessment':<17}  File"`.
- Separator: `─` repeated 16, 5, 5, 5, 5, 17 and 50 times.
- Level row: `duplication.lines` as `{n:>5}`; `-` when `duplication` is
  `null`. `0` and `-` are different: `0` means "checked, no clone", `-`
  means "not available".
- `PARSE` row: `-`.
- The summary does not change: no duplication total.

Example (the [subcommand.md](subcommand.md#full-example) run with #324):

```
Status             FTA  Cyclo  Lines    Dup  Assessment         File
──────────────── ─────  ─────  ─────  ─────  ─────────────────  ──────────────────────────────────────────────────
🔴 ERROR           71.3    136    245      0  Needs improvement  fixture/complex.ts
✅ OK              37.4      3     18      0  OK                 fixture/component.tsx
✅ OK              35.1      9     23     23  OK                 fixture/dup_b.js
✅ OK              35.0      9     23     23  OK                 fixture/dup_a.js
...
✅ OK               0.0      -      -      0  -                  fixture/empty.js
⛔ PARSE              -      -      -      -  -                  fixture/broken.js
⛔ PARSE              -      -      -      -  -                  fixture/latin1.js
```

## 5. Failure handling

A jscpd failure never fails the run. It is any of:

- jscpd exits non-zero or is killed;
- `/tmp/jscpd/jscpd.json` is missing or is not valid JSON;
- `duplicates` is not a list, or an entry lacks `firstFile`/`secondFile`
  objects with `name` (str), `start` and `end` (ints);
- a `name` does not map to a staged file.

Then the entrypoint sets `duplication: null` on **every** file, keeps
`tool_versions.jscpd`, adds one `warnings` entry
`{"tool": "jscpd", "message": <one-line reason>}` (no `path`), and goes on.
Its exit status is unchanged.

Tingle prints, for each `jscpd` warning without a `path`:

```
Warning: jscpd failed in <image>; duplication data is not available: <message>
```

The `Dup` column then shows `-` on every row. The exit code is unchanged.

## 6. Smoke test, docs and tests

- The smoke test (see [image.md](image.md#9-smoke-test-fixture) and
  [release.md](release.md#steps-for-js_complexity)) also asserts
  `tool_versions.jscpd == "5.4.1"`, `duplication.lines >= 20` for
  `dup_a.js` and `dup_b.js`, `0` for `simple.js` and `empty.js`, and `null`
  for `broken.js`, `latin1.js` and the hostile lines.
- Docs: the `Dup` column in `docs/guides/code_check/js_complexity.md`, the
  `long_help` text, and `docs/agents/tingle-js-complexity-image.md`.
- Python tests: the column with a number, `0` and `null`; `PARSE` rows; the
  warning for a `jscpd` entry without a `path`; the exit code unchanged by
  it.
