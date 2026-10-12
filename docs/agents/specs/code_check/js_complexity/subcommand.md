# Spec: the `tingle code_check js_complexity` subcommand

Sub-issue: #320. Parent: #315. Shared contracts: [README.md](README.md).

This spec covers the subcommand core: dispatch, the flags added here, the
Docker preflight and run (through `docker_check`, see
[docker-check.md](docker-check.md)), the merged JSON parsing, the report,
exit codes and edge cases. File selection flags come in #321
([file-selection.md](file-selection.md)), the config section in #322
([config.md](config.md)), the minified skip in #323, the `Dup` column in
#324 ([duplication.md](duplication.md)), `--details` in #325
([details.md](details.md)) and SFC support in #326 ([sfc.md](sfc.md)).

#320 depends on #317. For manual end-to-end tests it uses a local image from
#318 (`--image tingle_js_complexity:dev`).

## 1. Dispatch and package

- New package `python/code_check/js_complexity/`, laid out like
  `rubycritic/`:
  - `flags.py`: `FLAGS`, import-light (completion imports it);
  - `constants.py`: `DEFAULT_WARN = 50`, `DEFAULT_ERROR = 60`,
    `DEFAULT_CRITICAL = 75`, `DEFAULT_EXCLUDES`, `EXTENSIONS`,
    `DECLARATION_SUFFIXES`, `IMAGE_REPO = "darthjee/tingle_js_complexity"`,
    `VERSION_FILE` (from `docker_check`);
  - `errors.py`: `JsComplexityError(DockerCheckError)`;
  - `selection.py`: `select_files` binding the extensions and skip rules
    (see [file-selection.md](file-selection.md));
  - `output_parser.py`: the merged JSON contract (section 5);
  - `reporter.py`: the table and summary (section 6);
  - `executor.py`: `CheckJsComplexity(DockerCheck)`,
    `PROG = "tingle code_check js_complexity"`,
    `CONFIG_SECTION = "js_complexity"`.
- `python/code_check/executor.py`: add
  `"js_complexity": (CheckJsComplexity, "JavaScript/TypeScript code complexity via FTA (Docker).")`
  to `SUBCOMMANDS`, after `rubycritic`.
- `python/code_check/subcommands.py`: `SUBCOMMAND_NAMES` becomes
  `("file_size", "rubycritic", "js_complexity")`.
- `commands/python.json`: the `code_check` `short_help` becomes
  `Code evaluation checks (subcommands: file_size, rubycritic, js_complexity).`;
  `long_help` lists the new subcommand and gets a `js_complexity` part in the
  same shape as the `rubycritic` one (usage, flags, examples, exit status).
- `python/code_check/completion.py`: `js_complexity` gets the same completion
  as `rubycritic`, from `code_check.js_complexity.flags.FLAGS`: flag names,
  the `choices` of choice flags, nothing for free-form values, and the file
  sentinel for the path.
- Docs in the same PR: the guide `docs/guides/code_check/js_complexity.md`
  (with the Podman note: Podman aliased as `docker` may work but is not
  supported, and the `--ignore`/`--exclude` advice for generated code and
  unnamed minified bundles), its entry in `docs/guides/code_check.md`,
  `docs/agents/architecture.md`, and the `README.md` table.

## 2. Flags and levels

Flags added by #320 (see [README.md](README.md#3-cli-and-flags) for the full
table):

| Flag | Type | Default | Help |
|------|------|---------|------|
| `path` | str | required | `JavaScript/TypeScript file or directory to analyse (recursive)` |
| `--warn N` | float ≥ 0 | `50` | `Warn threshold on the file's FTA score (default: 50)` |
| `--error N` | float ≥ 0 | `60` | `Error threshold on the file's FTA score (default: 60)` |
| `--critical N` | float ≥ 0 | `75` | `Critical threshold on the file's FTA score (default: 75)` |
| `--top N` | int ≥ 0 | `0` (all) | `Show only the top N most complex files (default: 0 = all)` |
| `--min-level LEVEL` | `ok\|warn\|error\|critical` | `ok` | `Show only files at this level or higher (default: ok)` |
| `--fail-on LEVEL` | `warn\|error\|critical` | none | `Exit with status 2 if any file reaches this level or higher` |
| `--image IMAGE` | non-empty str | `darthjee/tingle_js_complexity:<tingle version>` | `Docker image to run (default: darthjee/tingle_js_complexity:<tingle version>)` |

- Single-value flags default to `None` in `FLAGS`; the built-in defaults are
  applied after the (later) config merge.
- A negative threshold or `--top`, or an empty `--image`, is a usage error
  with `rubycritic`'s texts (section 10). Exit 1. Argparse's usage errors are
  remapped from 2 to 1.
- The thresholds are not checked against each other.

**Score.** The score `s` of a file is `files[].fta.score` rounded to one
decimal with Python's `round(score, 1)`. Tingle uses `s` everywhere: the
level, the sort, the `--fail-on` gate, the display and the summary. A file
with `fta: null` and `parse_error: false` (dropped or refused) has `s = 0.0`.

**Levels.** With `file_size`'s `FileAnalyzer.classify` comparisons:

| Condition (checked in this order) | Level | Label |
|-----------------------------------|-------|-------|
| `s >= critical` | `critical` | `🟣 CRITICAL` |
| `s >= error` | `error` | `🔴 ERROR` |
| `s >= warn` | `warn` | `⚠️  WARN` |
| otherwise | `ok` | `✅ OK` |

FTA's own bands are `> 50` "Could be better" and `> 60` "Needs improvement"
(see [image.md](image.md#10-grounding-run)). The defaults line up with them;
`critical=75` is tingle's own. `Cyclo`, `Lines`, `Dup`, `Assessment` and the
per-function data are information only and never set the level or the exit
status. FTA scores are not capped at 100: a very large file can score above
it, and is simply `CRITICAL`.

## 3. Run order, preflight and pulling

`run(args)` follows `rubycritic`'s order, through `DockerCheck`:

1. No arguments: print the help, exit 0.
2. Parse the flags (usage errors exit 1).
3. Load the config (#322; before #322 there is no config).
4. Resolve `<path>`: missing → `Error: path not found: <resolved>`;
   unreadable → `Error: path not readable: <resolved>`; a mount root
   containing `:` → `Error: cannot mount <root>: Docker volume paths cannot contain ':'`.
   Exit 1. The mount root is `<resolved>` for a directory, its parent for a
   file.
5. Resolve the image (section 4).
6. Print the header (section 6).
7. Select the files (section 7). If none are left, print
   `No JavaScript/TypeScript files found for analysis.` (yellow, stdout) and
   exit 0, **without any Docker call**.
8. **Preflight** (`DockerRunner.preflight`): `docker` not on PATH, or
   `docker info` failing or timing out (30 s), exits 1 (section 10).
9. **Pull when missing** (`DockerRunner.ensure_image`): `Pulling <image> ...`
   (dim, stderr), then `docker pull`; a failed pull exits 1.
10. **Run** the container (section 4) and parse its stdout (section 5).
11. Print the warnings (section 8.1 and the secondary-tool warnings of #324
    and #325), in the order given in section 10.
12. Print the report (section 6), then exit 2 if the `--fail-on` gate
    failed, else 0.

## 4. The docker run line

- **Image:** `--image` (or, from #322, the `image` config key) wins.
  Otherwise `docker_check.image.resolve_image` returns
  `darthjee/tingle_js_complexity:<version>`, `<version>` being
  `shell/linux/VERSION` with all whitespace removed. A missing, unreadable or
  empty file without `--image`:
  `Error: cannot read the tingle version from <file>; use --image to choose the image`.
- **Run line:** `DockerRunner.run_args`, unchanged:

  ```
  docker run --rm -i --pull never --network none
    --security-opt no-new-privileges
    --user <uid>:<gid>
    -v <root>:/src:ro
    -w /src
    <image>
  ```

  Stdin gets the selection's lines (paths relative to `<root>`, POSIX
  separators, UTF-8, one per line, each followed by `\n`, sorted). For a
  single-file `<path>`, the only line is the file name. No timeout.
- **Outcome** (`DockerRunner.check_outcome` with `tool="FTA"`):

| Case | Behaviour |
|------|-----------|
| `status == 125` and stderr contains `mounts denied` or `not shared from the host` (case-insensitive) | Container stderr to tingle's stderr, then the mount error with the Docker Desktop hint. Exit 1. |
| any other non-zero `status` | Container stderr to tingle's stderr, then `Error: FTA failed in <image> (exit <status>)`. Exit 1. |
| `status == 0`, stdout fails the checks in section 5 | Container stderr to tingle's stderr, then `Error: could not parse the output of <image>: <reason>`. Exit 1. |
| `status == 0`, stdout valid | The container stderr is discarded. Continue. |

## 5. Merged JSON parsing and path mapping

The image prints the merged JSON defined in
[image.md](image.md#7-merged-json). `output_parser.parse(stdout, sent_lines)`
validates the **whole** shape from #320 on, including `duplication`,
`functions` and the `jscpd`/`escomplex` versions that #320 itself does not
display, so later sub-issues never change the checks.

**Checks.** The output is unparsable when any of these fail; `<reason>`
names the first failure:

| Check | Reason |
|-------|--------|
| stdout is valid JSON | `invalid JSON: <error>` |
| it is an object | `expected a JSON object` |
| `tool_versions` is an object with `fta` (str), `jscpd` and `escomplex` (str or `null`) | `unexpected tool_versions` |
| `files` is a list with exactly one entry per sent line | `files do not match the sent lines` |
| each `files[i]` is an object whose `path` equals sent line `i`; `parse_error` is a bool; `fta` is `null` or an object with `score` (number), `cyclo`, `lines` (ints ≥ 0) and `assessment` (str); `duplication` is `null` or `{"lines": int ≥ 0}`; `functions` is `null` or a list of objects with `name` (str), `line`, `cyclo`, `sloc` (ints ≥ 1); and, when `parse_error` is `true`, `fta`, `duplication` and `functions` are `null` | `unexpected files entry: <i>` |
| `warnings` is a list of objects with `tool` (one of `entrypoint`, `fta`, `jscpd`, `escomplex`) and `message` (str), and an optional `path` (str) | `unexpected warnings` |

JSON booleans are not numbers here. Unknown extra keys are ignored. There is
no version field and no negotiation.

**Path mapping.** The entrypoint never rewrites paths: `files[i].path` is
sent line `i`, and the checks above enforce it. Tingle maps entry `i` to
sent line `i`, and turns each line back into its host path (`<root>/<line>`)
for the report. Warnings are matched to files by exact `path`.

**Result per file.** `parse_error: true` → a `PARSE` file. Otherwise a level
row with `s` (section 2), `cyclo`, `lines` and `assessment` from `fta`, or
`s = 0.0` and `-` for the rest when `fta` is `null`.

## 6. Report

The report goes to stdout and mirrors `rubycritic`'s `Reporter`.

### Header

```
Analyzing: <resolved path>
Thresholds: warn=<w> | error=<e> | critical=<c>
Image: <image>
Config: <config file>        (only when a config section was loaded, #322)
<blank line>
```

`Analyzing:` is cyan and bold; the other lines are dim. Thresholds print with
`format(value, "g")`.

### Table

- Header: `f"{'Status':<16} {'FTA':>5}  {'Cyclo':>5}  {'Lines':>5}  {'Assessment':<17}  File"`.
- Separator: `─` repeated 16, 5, 5, 5, 17 and 50 times, with the same
  spacing.
- #324 inserts the `Dup` column after `Lines`: `{'Dup':>5}  ` in the header
  and a 5-wide separator (see [duplication.md](duplication.md#4-report)).
- Level row: the label padded to 16 and coloured like `file_size`
  (`Palette.level_color`), then `s` as `{s:>5.1f}`, `cyclo` and `lines` as
  `>5` ints, `assessment` as `<17`, then the file. A dropped or refused file
  shows `  0.0` and `-` for `Cyclo`, `Lines` and `Assessment`.
- `PARSE` row: `⛔ PARSE` padded to 16 (gray), `-` in every value column.
- File: `rubycritic`'s display rule: the path relative to the target's parent
  for a directory `<path>`, the file name for a single-file `<path>`.
- Order: level rows sorted by `s`, highest first, ties by sent line
  (ascending); then the `PARSE` rows, sorted by sent line.

**Display filters.** `--min-level` keeps level rows at that level or higher,
then `--top N` (when N > 0) keeps the first N. `PARSE` rows are always shown,
below the level rows, and are not counted by `--top`. When no row at all is
left, the table is replaced by `No files at or above <LEVEL>.`.

### Summary

It always counts every selected file, whatever `--min-level` and `--top`
are:

```
<blank line>
────────────────────────────────────────────────────────────────────────────── (78 × ─, gray)
Summary: <N> file(s) | <a> OK | <b> WARN | <c> ERROR | <d> CRITICAL[ | <k> skipped (parse error)]
FTA score: avg <avg> | max <max>
```

- `<N>` counts every selected file, `PARSE` files included. `<a>` to `<d>`
  count the level rows (dropped and refused files count as `OK`).
- `| <k> skipped (parse error)` (gray) is appended only when `<k>` > 0.
- `<avg>` and `<max>` are the mean and the maximum of `s` over the level
  rows (dropped and refused files count with `0.0`; `PARSE` files are left
  out), printed with 2 decimals. When there is no level row,
  the line is `FTA score: n/a`. FTA has no project-wide score; tingle
  computes both.

### Full example

`tingle code_check js_complexity fixture` on the grounding fixture (no
colours), with #320 only: `build/` is a default exclude, `ext/types.d.ts` is
a declaration file, `Cart.vue` is not selected before #326, and the minified
skip does not exist before #323:

```
Analyzing: /home/me/fixture
Thresholds: warn=50 | error=60 | critical=75
Image: darthjee/tingle_js_complexity:0.9.0

Status             FTA  Cyclo  Lines  Assessment         File
──────────────── ─────  ─────  ─────  ─────────────────  ──────────────────────────────────────────────────
🔴 ERROR           71.3    136    245  Needs improvement  fixture/complex.ts
✅ OK              37.4      3     18  OK                 fixture/component.tsx
✅ OK              35.1      9     23  OK                 fixture/dup_b.js
✅ OK              35.0      9     23  OK                 fixture/dup_a.js
✅ OK              31.0      3     11  OK                 fixture/widget.jsx
✅ OK               7.7      1      6  OK                 fixture/simple.js
✅ OK               7.3      2      6  OK                 fixture/bom.ts
✅ OK               7.3      2      6  OK                 fixture/crlf.js
✅ OK               7.3      2      6  OK                 fixture/ext/UPPER.JS
✅ OK               7.3      2      6  OK                 fixture/ext/a.mjs
✅ OK               7.3      2      6  OK                 fixture/ext/b.cjs
✅ OK               7.3      2      6  OK                 fixture/ext/c.mts
✅ OK               7.3      2      6  OK                 fixture/ext/d.cts
✅ OK               6.2      5      1  OK                 fixture/bundle.min.js
✅ OK               3.5      1      1  OK                 fixture/short.js
✅ OK               0.0      -      -  -                  fixture/empty.js
⛔ PARSE              -      -      -  -                  fixture/broken.js
⛔ PARSE              -      -      -  -                  fixture/latin1.js

──────────────────────────────────────────────────────────────────────────────
Summary: 18 file(s) | 15 OK | 0 WARN | 1 ERROR | 0 CRITICAL | 2 skipped (parse error)
FTA score: avg 17.39 | max 71.30
```

The two `cannot parse` warnings (section 8.1) go to stderr before the report
body.

## 7. File selection in #320

#320 selects, through `docker_check.selection.select_files`:

- for a directory `<path>`: the regular files under it with a core extension
  (case-insensitive), minus the default excludes, minus declaration files,
  with symlink confinement;
- for a single-file `<path>`: that file if it has a core extension and is not
  a declaration file, else nothing.

There is no binary check (`binary_check=False`), so a file that is not valid
UTF-8 reaches the image and becomes a `PARSE` row. Unsendable names are
dropped with a warning (section 8.11). #321 adds the selection flags, #323
the minified skip and #326 the SFC extensions; see
[file-selection.md](file-selection.md).

## 8. Edge cases

The numbering follows #315's "Edge cases"; 8.17 onwards come from #316.

### 8.1 Syntax errors

- **FTA cannot parse a file** (or it is not valid UTF-8): `parse_error:
  true`. It prints `Warning: cannot parse <file>: <message>` on stderr
  (`<file>` as displayed in the table; `<message>` from the `warnings` entry
  with that `path` and `tool` `fta` or `entrypoint`, else `unknown error`).
  The row is `⛔ PARSE`; it counts as skipped, is never in the level counts,
  the average or the maximum, and never triggers `--fail-on`.
- **FTA parses a file but escomplex cannot:** the file keeps its row and
  level; under `--details` it shows `(per-function data unavailable)`. See
  [details.md](details.md#5-unavailable-data).

### 8.2 A secondary tool fails

jscpd or escomplex failing never changes the rows, the levels or the exit
code. The report is printed from FTA's data, `Dup` shows `-` or the function
lines are replaced by the unavailable note, and one warning naming the tool
goes to stderr. See [duplication.md](duplication.md#5-failure-handling) and
[details.md](details.md#6-failure-handling). Only an FTA failure is fatal.

### 8.3 Files FTA drops

FTA drops files with no code line (empty, blank-only or comment-only; see
[README.md](README.md#11-deviations-from-315), item 5). They come back with
`fta: null` and are shown as `OK` with `0.0`, so the file count matches the
selection.

### 8.4 Symlinks

Symlinks resolving outside the mount root, or dangling, are skipped silently
on the host. A kept symlink is sent and shown as its target. See
[file-selection.md](file-selection.md#7-symlinks-and-single-files).

### 8.5 Single-file `<path>`

The mount root is the file's parent (after resolving a symlink); stdin holds
only the file name; the display is the file name. A file with an extension
that is not supported, or a declaration file, leaves nothing to analyse
(`No JavaScript/TypeScript files found for analysis.`, exit 0).

### 8.6 `<path>` missing or unreadable

Section 3, step 4. Exit 1.

### 8.7 Nothing selected

Header, then `No JavaScript/TypeScript files found for analysis.` (yellow),
exit 0. No Docker command runs.

### 8.8 Docker Desktop file sharing

Detected as in section 4 (exit 125 plus `mounts denied` or `not shared from
the host`). Docker's stderr is passed through, then the mount error with the
file-sharing hint. Exit 1.

### 8.9 No daemon, rootless Docker or Podman

The preflight fails with exit 1 when `docker info` fails. Podman aliased as
`docker` may work but is not supported.

### 8.10 Inside the `darthjee/tingle` container

There is no `docker` there, so the preflight exits 1 with the "docker not
found" error. Docker-in-Docker is out of scope.

### 8.11 Unusual file names

Spaces, tabs and unicode are sent as they are. A relative path containing
`\n` is skipped with `Warning: skipping file with a newline in its name:
<repr>`; one that is not valid UTF-8 with `Warning: skipping file whose name
is not valid UTF-8: <repr>`. They are not counted anywhere.

### 8.12 Large repositories

The file list goes through stdin, so there is no argument-length limit, and
the run has no timeout. The entrypoint copies the selected files into
`/tmp` inside the container, so the container needs that much temporary
space.

### 8.13 Minified bundles

Skipped by name by default from #323. A minified file without `.min` in its
name is analysed and is probably `CRITICAL`; the guide suggests `--ignore`.
See [file-selection.md](file-selection.md#4-minified-bundles).

### 8.14 Generated code

Not special-cased. The guide documents `--ignore`/`--exclude` for it (for
example `--ignore '**/*.generated.ts'`).

### 8.15 Single-file components

From #326. See [sfc.md](sfc.md#6-edge-cases).

### 8.16 Duplication across the selection only

jscpd only sees the staged (selected) files. See
[duplication.md](duplication.md#3-per-file-duplicated-lines).

### 8.17 Refused lines

The image refuses absolute paths, `..` segments, empty and duplicate lines,
paths that are not a regular file under `/src` and unsupported extensions
(see [image.md](image.md#4-entrypoint-input)). Tingle's selection never
sends such lines, but a file deleted between the selection and the run is
refused as `not a regular file under /src`. Each refused line prints
`Warning: the image skipped <line>: <message>` (`<line>` as sent) and is
shown as `OK` with `0.0`.

### 8.18 Encodings and line endings

CRLF line endings and a UTF-8 BOM give the same results as LF without a BOM.
A file that is not valid UTF-8 is a `PARSE` row (8.1).

## 9. Exit codes

| Code | Causes |
|------|--------|
| `0` | Report printed and the gate passed or was not set; nothing selected; `--help`. `PARSE` rows, refused lines and secondary-tool warnings do not change it. |
| `1` | Usage error; `<path>` missing or unreadable; mount root with `:`; tingle version unreadable without `--image`; config error (#322); `docker` not on PATH; `docker info` failed or timed out; image pull failed; mount failure; any non-zero container status (FTA or entrypoint failure); unparsable container output. |
| `2` | `--fail-on LEVEL` is set and at least one level row (dropped and refused files included, `PARSE` rows excluded) reaches `LEVEL`. |

The gate uses every selected file, not only the displayed rows.

## 10. Messages

Errors are `Error: <message>` in red on stderr, then exit 1. Warnings are
`Warning: <message>` in yellow on stderr. The Docker messages come from
`docker_check` with `command="tingle code_check js_complexity"` and
`tool="FTA"`.

| Case | Text |
|------|------|
| `docker` not found | `Error: docker not found on PATH; tingle code_check js_complexity needs Docker to run FTA` |
| Daemon not responding | `Error: the Docker daemon is not responding (docker info failed); start Docker and retry` |
| Pull progress (dim, not an error) | `Pulling <image> ...` |
| Pull failure | `Error: could not pull image <image>` |
| `docker` cannot be started | `Error: could not run docker: <exception>` |
| Mount failure | `Error: Docker could not mount <root>; on Docker Desktop, share it (or a parent folder) under Settings > Resources > File sharing, then retry` |
| Container failure (after the container stderr) | `Error: FTA failed in <image> (exit <status>)` |
| Unparsable output | `Error: could not parse the output of <image>: <reason>` |
| `<path>` missing | `Error: path not found: <path>` |
| `<path>` unreadable | `Error: path not readable: <path>` |
| Mount root with `:` | `Error: cannot mount <root>: Docker volume paths cannot contain ':'` |
| Version file unreadable | `Error: cannot read the tingle version from <file>; use --image to choose the image` |
| Negative threshold | `Error: --warn must be a number >= 0` (`--error`, `--critical` likewise) |
| Negative `--top` | `Error: --top must be an integer >= 0` |
| Empty `--image` | `Error: --image must not be empty` |
| File name with a newline | `Warning: skipping file with a newline in its name: <repr>` |
| File name not valid UTF-8 | `Warning: skipping file whose name is not valid UTF-8: <repr>` |
| Refused line | `Warning: the image skipped <line>: <message>` |
| Unparsable file | `Warning: cannot parse <file>: <message>` |
| Nothing selected (stdout, yellow) | `No JavaScript/TypeScript files found for analysis.` |

Order of the warnings printed after the run: the refused-line warnings (in
`warnings` order), then the `cannot parse` warnings (sorted by sent line),
then the secondary-tool warnings of #324 and #325. Config errors use
`file_size`'s wording; see [config.md](config.md#5-error-handling).

## 11. Tests

Tests live under `python/tests/code_check/js_complexity/`. `docker` is never
run: `shutil.which` and `subprocess.run` are mocked, and the container stdout
is built from the merged JSON sample in [image.md](image.md#7-merged-json).
Coverage stays at or above 75%. They cover at least:

- dispatch, the subcommand list and completion;
- flags: defaults, float thresholds, negative values, bad choices and an
  empty `--image` exiting 1;
- levels: each boundary on the rounded score (`s == warn`, ...), and a raw
  score that rounds across a threshold (`59.96` → `60.0` → `ERROR`);
- image resolution and the exact `docker run` arguments and stdin, for a
  directory and a single file;
- preflight, pull and container outcomes (mount failure, non-zero status,
  each unparsable-output reason, success);
- parsing: the full shape (with `duplication` and `functions` filled and
  `null`), `files` length and path mismatches, `parse_error` with a non-null
  `fta`, booleans as numbers;
- report: layout, sort and ties, `--top`, `--min-level`,
  `No files at or above <LEVEL>.`, `PARSE` rows and their warnings, dropped
  and refused files, the summary with and without the skipped part,
  `FTA score: n/a`;
- `--fail-on`: exit 2 when reached, never because of `PARSE`;
- unsendable names, `<path>` missing or unreadable, a mount root with `:`.
