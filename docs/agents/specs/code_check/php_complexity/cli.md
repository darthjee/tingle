# Spec: the `tingle code_check php_complexity` subcommand

Sub-issue: #348. Parent: #344. Shared contracts: [README.md](README.md).

This spec covers the subcommand core: the package on top of `docker_check`,
the flags added here, the Docker preflight and run, the merged JSON parsing,
the report, exit codes, edge cases and messages. File selection flags come
in #349 ([selection.md](selection.md)), the config section in #350
([config.md](config.md)), `--details` in #351 ([details.md](details.md)) and
the `Dup` column in #352 ([duplication.md](duplication.md)).

#348 depends on #345 only. The shared `python/code_check/docker_check/`
package (#317) is used as it is and is not changed. For manual end-to-end
tests #348 uses a local image from #346
(`--image tingle_php_complexity:dev`).

## 1. Dispatch and package

New package `python/code_check/php_complexity/`, laid out like
`js_complexity/`, each module a thin binding of `docker_check`:

| Module | Content | From `docker_check` |
|--------|---------|---------------------|
| `flags.py` | `FLAGS`, import-light (completion imports it). | — |
| `constants.py` | `Constants` (below). | `Constants.VERSION_FILE` |
| `errors.py` | `PhpComplexityError(DockerCheckError)`. | `errors.DockerCheckError` |
| `docker_runner.py` | `DockerRunner(docker_check_runner.DockerRunner)` binding `error_class=PhpComplexityError`, `COMMAND = "tingle code_check php_complexity"`, `TOOL = "PDepend"`; re-exports `DOCKER`, `decode`, `write_stderr`; keeps `shutil` and `subprocess` importable for the tests. | `docker_runner` |
| `image.py` | `resolve_image(cli_image, version_file=None)` binding `Constants.IMAGE_REPO` and `PhpComplexityError`. | `image.resolve_image` |
| `selection.py` | `select_files` binding the extension, the default excludes and the skip rules ([selection.md](selection.md)). | `selection.select_files`, `Selection`, `build_selection`, `unsendable_reason` |
| `output_parser.py` | `parse(stdout, sent_lines)`, `ParsedOutput`, `FileResult`, `OutputFormatError` (section 5). | — |
| `reporter.py` | `Reporter`, the table and summary (section 6). | — |
| `config.py` | `SCHEMA`, `validate` (#350; before #350 a stub that accepts nothing, as in `js_complexity` before #322). | — |
| `executor.py` | `CheckPhpComplexity(DockerCheck)`, `PROG = "tingle code_check php_complexity"`, `CONFIG_SECTION = "php_complexity"`. | `executor.DockerCheck` |

`CheckPhpComplexity` sets the `DockerCheck` class attributes like
`CheckJsComplexity`: `PROG`, `FLAGS`, `CONFIG_SECTION`, `SINGLE_DEFAULTS`
(`warn` 20, `error` 40, `critical` 60, `top` 0, `fail_on` `None`,
`min_level` `"ok"`, `image` `None`, and from #351 `details` `None`),
`LIST_KEYS = ("ignore", "include")`, `THRESHOLD_KEYS = ("warn", "error",
"critical")`, `DEFAULT_EXCLUDES = Constants.DEFAULT_EXCLUDES`,
`NO_FILES_MESSAGE = "No PHP files found for analysis."` and
`error_class = PhpComplexityError`. Its hooks are `validate_config`,
`_load_section`, `_select_files`, `_selection_options` (adds
`skip_bootstrap_cache`, see [selection.md](selection.md#4-skip-rules)),
`_gate_value` (the total CCN) and `_execute`.

`constants.py`:

```python
class Constants:
    DEFAULT_WARN: ClassVar[float] = 20
    DEFAULT_ERROR: ClassVar[float] = 40
    DEFAULT_CRITICAL: ClassVar[float] = 60
    DEFAULT_DETAILS: ClassVar[int] = 5          # from #351
    DEFAULT_EXCLUDES: ClassVar[list[str]] = [
        *FileSizeConstants.DEFAULT_EXCLUDES, "var", "storage", ".phpunit.cache",
    ]
    EXTENSIONS: ClassVar[list[str]] = [".php"]
    BLADE_SUFFIX: ClassVar[str] = ".blade.php"
    BOOTSTRAP_CACHE: ClassVar[tuple[str, str]] = ("bootstrap", "cache")
    IMAGE_REPO: ClassVar[str] = "darthjee/tingle_php_complexity"
    VERSION_FILE: ClassVar[Path] = DockerCheckConstants.VERSION_FILE
```

Registration:

- `python/code_check/executor.py`: add
  `"php_complexity": (CheckPhpComplexity, "PHP code complexity via PDepend (Docker).")`
  to `SUBCOMMANDS`, after `js_complexity`.
- `python/code_check/subcommands.py`: `SUBCOMMAND_NAMES` becomes
  `("file_size", "rubycritic", "js_complexity", "php_complexity")`.
- `commands/python.json`: the `code_check` `short_help` becomes
  `Code evaluation checks (subcommands: file_size, rubycritic, js_complexity, php_complexity).`;
  `long_help` lists `php_complexity   PHP code complexity via PDepend (Docker).`
  under "Subcommands" and gets a `php_complexity` part in the same shape as
  the `js_complexity` one (usage, file selection, thresholds, display, CI
  gate, image, exit codes, examples). #349, #350, #351 and #352 extend it.
- `python/code_check/completion.py`: `php_complexity` gets the same
  completion as `js_complexity`, from `code_check.php_complexity.flags.FLAGS`:
  flag names, the `choices` of choice flags, nothing for free-form values,
  and the file sentinel for the path.

Docs in the same PR (each owned by its agent):

- the guide `docs/guides/code_check/php_complexity.md`, with: the total-CCN
  metric and the calibration behind `20/40/60` (README §3); the columns; the
  enum and anonymous-class undercount and the property-hook limitation
  (README deviations 7 and 8); `PARSE` rows for PHP and PDepend rejections,
  with the hint to try a newer image through `--image` (README deviation 2);
  the `--ignore`/`--exclude` advice for tests and generated code; the Podman
  note (Podman aliased as `docker` may work but is not supported);
- its entry in `docs/guides/code_check.md`;
- `docs/agents/architecture.md` (the new package);
- the `README.md` table of commands.

## 2. Flags and levels

Flags added by #348 (see [README.md](README.md#3-cli-and-flags) for the full
table):

| Flag | Type | Default | Help |
|------|------|---------|------|
| `path` | str | required | `PHP file or directory to analyse (recursive)` |
| `--warn N` | float ≥ 0 | `20` | `Warn threshold on the file's total CCN (default: 20)` |
| `--error N` | float ≥ 0 | `40` | `Error threshold on the file's total CCN (default: 40)` |
| `--critical N` | float ≥ 0 | `60` | `Critical threshold on the file's total CCN (default: 60)` |
| `--top N` | int ≥ 0 | `0` (all) | `Show only the top N most complex files (default: 0 = all)` |
| `--min-level LEVEL` | `ok\|warn\|error\|critical` | `ok` | `Show only files at this level or higher (default: ok)` |
| `--fail-on LEVEL` | `warn\|error\|critical` | none | `Exit with status 2 if any file reaches this level or higher` |
| `--image IMAGE` | non-empty str | `darthjee/tingle_php_complexity:<tingle version>` | `Docker image to run (default: darthjee/tingle_php_complexity:<tingle version>)` |

- Single-value flags default to `None` in `FLAGS`; the built-in defaults are
  applied after the (later) config merge.
- A negative threshold or `--top`, or an empty `--image`, is a usage error
  with `docker_check`'s texts (section 10). Exit 1. Argparse's usage errors
  are remapped from 2 to 1.
- The thresholds are not checked against each other.

**Score.** The score `s` of a file is its **total CCN**,
`files[].pdepend.ccn`, an integer. Tingle uses `s` everywhere: the level,
the sort, the `--fail-on` gate, the display and the summary. A file with
`pdepend: null` and `parse_error: false` (no class, trait or function, or a
refused line) has `s = 0`.

**Levels.** With `file_size`'s `FileAnalyzer.classify` comparisons:

| Condition (checked in this order) | Level | Label |
|-----------------------------------|-------|-------|
| `s >= critical` | `critical` | `🟣 CRITICAL` |
| `s >= error` | `error` | `🔴 ERROR` |
| `s >= warn` | `warn` | `⚠️  WARN` |
| otherwise | `ok` | `✅ OK` |

`Max`, `NPath`, `MI`, `Lines`, `Dup` and the per-function data are
information only and never set the level or the exit status.

## 3. Run order, preflight and pulling

`run(args)` is `DockerCheck.run`, the same order as `js_complexity`:

1. No arguments: print the help, exit 0.
2. Parse the flags (usage errors exit 1).
3. Load the config (#350; before #350 there is no config).
4. Resolve `<path>`: missing → `Error: path not found: <resolved>`;
   unreadable → `Error: path not readable: <resolved>`; a mount root
   containing `:` → `Error: cannot mount <root>: Docker volume paths cannot contain ':'`.
   Exit 1. The mount root is `<resolved>` for a directory, its parent for a
   file.
5. Resolve the image (section 4).
6. Print the header (section 6).
7. Select the files (section 7). If none are left, print
   `No PHP files found for analysis.` (yellow, stdout) and exit 0, **without
   any Docker call**.
8. **Preflight** (`DockerRunner.preflight`): `docker` not on PATH, or
   `docker info` failing or timing out (30 s), exits 1 (section 10).
9. **Pull when missing** (`DockerRunner.ensure_image`): `Pulling <image> ...`
   (dim, stderr), then `docker pull`; a failed pull exits 1.
10. **Run** the container (section 4) and parse its stdout (section 5).
11. Print the warnings (section 10, "Order").
12. Print the report (section 6), then exit 2 if the `--fail-on` gate
    failed, else 0.

## 4. The docker run line

- **Image:** `--image` (or, from #350, the `image` config key) wins.
  Otherwise `resolve_image` returns
  `darthjee/tingle_php_complexity:<version>`, `<version>` being
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
- **Outcome** (`DockerRunner.check_outcome` with `tool="PDepend"`):

| Case | Behaviour |
|------|-----------|
| `status == 125` and stderr contains `mounts denied` or `not shared from the host` (case-insensitive) | Container stderr to tingle's stderr, then the mount error with the Docker Desktop hint. Exit 1. |
| any other non-zero `status` | Container stderr to tingle's stderr, then `Error: PDepend failed in <image> (exit <status>)`. Exit 1. |
| `status == 0`, stdout fails the checks in section 5 | Container stderr to tingle's stderr, then `Error: could not parse the output of <image>: <reason>`. Exit 1. |
| `status == 0`, stdout valid | The container stderr is discarded. Continue. |

## 5. Merged JSON parsing and path mapping

The image prints the merged JSON defined in
[image.md](image.md#7-merged-json). `output_parser.parse(stdout, sent_lines)`
validates the **whole** shape from #348 on, including `functions`,
`duplication` and `tool_versions.jscpd` that #348 itself does not display,
so later sub-issues never change the checks.

**Checks.** The output is unparsable when any of these fail; `<reason>`
names the first failure:

| Check | Reason |
|-------|--------|
| stdout is valid JSON | `invalid JSON: <error>` |
| it is an object | `expected a JSON object` |
| `tool_versions` is an object with `php` and `pdepend` (str) and `jscpd` (str or `null`) | `unexpected tool_versions` |
| `files` is a list with exactly one entry per sent line | `files do not match the sent lines` |
| each `files[i]` is an object whose `path` equals sent line `i`; `parse_error` is a bool; `pdepend` is `null` or an object with `ccn` (int ≥ 0), `max_ccn` and `max_npath` (int ≥ 1 or `null`), `min_mi` (number or `null`) and `lloc` (int ≥ 0); `functions` is `null` or a list of objects with `name` (str), `line`, `ccn` and `npath` (ints ≥ 1); `duplication` is `null` or `{"lines": int ≥ 0}`; and, when `parse_error` is `true`, `pdepend`, `functions` and `duplication` are `null` | `unexpected files entry: <i>` |
| `warnings` is a list of objects with `tool` (one of `entrypoint`, `php`, `pdepend`, `jscpd`) and `message` (str), and an optional `path` (str) | `unexpected warnings` |

JSON booleans are not numbers here. Ints may be larger than 2^53
(`max_npath`, `npath`). Unknown extra keys are ignored. There is no version
field and no negotiation.

**Path mapping.** The entrypoint never rewrites paths: `files[i].path` is
sent line `i`, and the checks above enforce it. Tingle maps entry `i` to
sent line `i`, and turns each line back into its host path (`<root>/<line>`)
for the report. Warnings are matched to files by exact `path`.

**Result per file** (`FileResult`): `parse_error: true` → a `PARSE` file.
Otherwise a level row with `s` (section 2) and `max_ccn`, `max_npath`,
`min_mi`, `lloc` from `pdepend`, or `s = 0` and `None` for the rest when
`pdepend` is `null`. `functions` and `duplication` are kept as they are for
#351 and #352.

## 6. Report

The report goes to stdout and mirrors `js_complexity`'s `Reporter`.

### Header

`DockerCheck._print_header`, unchanged:

```
Analyzing: <resolved path>
Thresholds: warn=<w> | error=<e> | critical=<c>
Image: <image>
Config: <config file>        (only when a config section was loaded, #350)
<blank line>
```

`Analyzing:` is cyan and bold; the other lines are dim. Thresholds print with
`format(value, "g")` (`warn=20 | error=40 | critical=60`).

### Table

- Header:
  `f"{'Status':<16} {'CCN':>5}  {'Max':>5}  {'NPath':>7}  {'MI':>5}  {'Lines':>5}  File"`.
- Separator: `─` repeated 16, 5, 5, 7, 5, 5 and 50 times, with the same
  spacing.
- #352 inserts the `Dup` column after `Lines`: `{'Dup':>5}  ` in the header
  and a 5-wide separator (see [duplication.md](duplication.md#4-report)).
- Level row: the label padded to 16 and coloured like `file_size`
  (`Palette.level_color`), then:

| Column | Value | Format | When `None` |
|--------|-------|--------|-------------|
| `CCN` | `s` | `{s:>5}` | never (`0`) |
| `Max` | `max_ccn` | `>5` | `-` |
| `NPath` | `max_npath` | `>7` (a minimum: larger numbers are printed in full) | `-` |
| `MI` | `min_mi` | `format(min_mi, ".0f")`, then `>5` | `-` |
| `Lines` | `lloc` | `>5` | `-` |
| `File` | the display path | as is | — |

- `PARSE` row: `⛔ PARSE` padded to 16 (gray), `-` in every value column.
- File: `js_complexity`'s display rule: the path relative to the target's
  parent for a directory `<path>`, the file name for a single-file `<path>`.
- Order: level rows sorted by `s`, highest first, ties by sent line
  (ascending); then the `PARSE` rows, sorted by sent line.

**Display filters.** `--min-level` keeps level rows at that level or higher,
then `--top N` (when N > 0) keeps the first N. `PARSE` rows are always
shown, below the level rows, and are not counted by `--top`. When no row at
all is left, the table is replaced by `No files at or above <LEVEL>.`.

### Summary

It always counts every selected file, whatever `--min-level` and `--top`
are:

```
<blank line>
────────────────────────────────────────────────────────────────────────────── (78 × ─, gray)
Summary: <N> file(s) | <a> OK | <b> WARN | <c> ERROR | <d> CRITICAL[ | <k> skipped (parse error)]
CCN: avg <avg> | max <max>
```

- `<N>` counts every selected file, `PARSE` files included. `<a>` to `<d>`
  count the level rows (files with `pdepend: null` count as `OK`).
- `| <k> skipped (parse error)` (gray) is appended only when `<k>` > 0.
- `<avg>` and `<max>` are the mean and the maximum of `s` over the level
  rows (files with `pdepend: null` count with 0; `PARSE` files are left
  out), printed with 2 decimals. When there is no level row, the line is
  `CCN: n/a`. `CCN:` is bold, like `FTA score:`.

### Full example

`tingle code_check php_complexity fixture` on the grounding fixture
([image.md](image.md#9-smoke-test-fixture)), no colours, #348 only. The
values are the real output of the grounding image; `welcome.blade.php` is
not selected (Blade skip) and `notes.txt` is not `.php`:

```
Analyzing: /home/me/fixture
Thresholds: warn=20 | error=40 | critical=60
Image: darthjee/tingle_php_complexity:0.9.0

Status             CCN    Max    NPath     MI  Lines  File
──────────────── ─────  ─────  ───────  ─────  ─────  ──────────────────────────────────────────────────
✅ OK                11      7       36     54     22  fixture/Calculator.php
✅ OK                 6      2        2     78     11  fixture/Shapes.php
✅ OK                 4      3        4     66     12  fixture/helpers.php
✅ OK                 3      3        4     58      9  fixture/dup_a.php
✅ OK                 3      3        4     58      9  fixture/dup_b.php
✅ OK                 2      2        4     66      6  fixture/Anon.php
✅ OK                 2      2        2     80      2  fixture/CVS/legacy.php
✅ OK                 2      1        1     79     11  fixture/Modern.php
✅ OK                 2      2        2     78      2  fixture/UPPER.PHP
✅ OK                 2      2        2     80      2  fixture/bom.php
✅ OK                 2      2        2     80      2  fixture/crlf.php
✅ OK                 2      2        2     90      4  fixture/page.php
✅ OK                 1      1        1     83      2  fixture/latin1.php
✅ OK                 0      -        -      -      -  fixture/bootstrap.php
✅ OK                 0      -        -      -      -  fixture/empty.php
⛔ PARSE              -      -        -      -      -  fixture/attr_anon.php
⛔ PARSE              -      -        -      -      -  fixture/broken.php
⛔ PARSE              -      -        -      -      -  fixture/lenient.php

──────────────────────────────────────────────────────────────────────────────
Summary: 18 file(s) | 15 OK | 0 WARN | 0 ERROR | 0 CRITICAL | 3 skipped (parse error)
CCN: avg 2.80 | max 11.00
```

The three `cannot parse` warnings (section 8.1) go to stderr before the
report body:

```
Warning: cannot parse fixture/attr_anon.php: Unexpected token: #[, line: 14, col: 20
Warning: cannot parse fixture/broken.php: syntax error, unexpected token ":", expecting variable on line 10
Warning: cannot parse fixture/lenient.php: syntax error, unexpected token ";" on line 5
```

With `--warn 4 --error 6 --critical 10 --min-level warn` the same data gives
(table and summary only):

```
Status             CCN    Max    NPath     MI  Lines  File
──────────────── ─────  ─────  ───────  ─────  ─────  ──────────────────────────────────────────────────
🟣 CRITICAL          11      7       36     54     22  fixture/Calculator.php
🔴 ERROR              6      2        2     78     11  fixture/Shapes.php
⚠️  WARN             4      3        4     66     12  fixture/helpers.php
⛔ PARSE              -      -        -      -      -  fixture/attr_anon.php
⛔ PARSE              -      -        -      -      -  fixture/broken.php
⛔ PARSE              -      -        -      -      -  fixture/lenient.php

──────────────────────────────────────────────────────────────────────────────
Summary: 18 file(s) | 12 OK | 1 WARN | 1 ERROR | 1 CRITICAL | 3 skipped (parse error)
CCN: avg 2.80 | max 11.00
```

## 7. File selection in #348

#348 selects, through `php_complexity.selection.select_files` (on top of
`docker_check.selection.select_files`):

- for a directory `<path>`: the regular files under it ending in `.php`
  (case-insensitive), minus the default excludes, minus Blade templates,
  minus the `bootstrap/cache` rule, with symlink confinement;
- for a single-file `<path>`: that file if it ends in `.php` and is not a
  Blade template, else nothing.

There is no binary check (`binary_check=False`). Unsendable names are
dropped with a warning (section 8.13). #349 adds the selection flags; see
[selection.md](selection.md).

## 8. Edge cases

The numbering follows #344's "Edge cases"; 8.17 onwards come from #345.

### 8.1 Syntax errors

- **PHP or PDepend cannot parse a file:** `parse_error: true`. Tingle
  prints `Warning: cannot parse <file>: <message>` on stderr (`<file>` as
  displayed in the table; `<message>` from the `warnings` entry with that
  `path` and `tool` `php` or `pdepend`, else `unknown error`). The row is
  `⛔ PARSE`; it counts as skipped, is never in the level counts, the
  average or the maximum, and never triggers `--fail-on`.
- PDepend's partial data for a file it rejected is never shown (the image
  discards it, README deviation 3).

### 8.2 jscpd fails

From #352. The rows, levels and exit code do not change; `Dup` shows `-`
and one warning naming jscpd goes to stderr. See
[duplication.md](duplication.md#5-failure-handling). Only a PDepend or
entrypoint failure is fatal.

### 8.3 Files with no function or method

Top-level-only files, empty files and files holding only enums or
interfaces come back with `pdepend: null` and are shown as `OK` with CCN 0
and `-` elsewhere, so the file count matches the selection (README
deviation 6). A file with classes but no method has a `pdepend` object with
`ccn` 0 and `null` maxima: `OK`, `0`, `-`, `-`, `-` and its `lloc`.

### 8.4 Mixed HTML/PHP

PDepend parses the PHP blocks; the inline HTML and top-level control flow
are not counted (`page.php`: one inline function, total CCN 2).

### 8.5 Several classes in one file

Every method of every class and trait in the file, and every function, adds
up (`Shapes.php`: total 6).

### 8.6 New or unsupported PHP syntax

Code PHP 8.5 rejects is a `PARSE` row with PHP's message. Valid code PDepend
3.0.0 rejects (attributes on anonymous classes) is a `PARSE` row with
PDepend's message (README deviation 2). Enum methods and property hooks
parse but are not counted (README deviations 7 and 8). The guide suggests a
newer image through `--image` for PDepend rejections.

### 8.7 Symlinks

Symlinks resolving outside the mount root, or dangling, are skipped silently
on the host. A kept symlink is sent and shown as its target. See
[selection.md](selection.md#7-symlinks-and-single-files).

### 8.8 Single-file `<path>`

The mount root is the file's parent (after resolving a symlink); stdin holds
only the file name; the display is the file name. A file that does not end
in `.php`, or a `*.blade.php`, leaves nothing to analyse
(`No PHP files found for analysis.`, exit 0).

### 8.9 `<path>` missing or unreadable

Section 3, step 4. Exit 1.

### 8.10 Nothing selected

Header, then `No PHP files found for analysis.` (yellow), exit 0. No Docker
command runs.

### 8.11 Docker Desktop file sharing

Detected as in section 4 (exit 125 plus `mounts denied` or `not shared from
the host`). Docker's stderr is passed through, then the mount error with the
file-sharing hint. Exit 1.

### 8.12 No daemon, or inside the `darthjee/tingle` container

The preflight fails with exit 1 when `docker` is not on PATH (as inside the
`darthjee/tingle` container) or `docker info` fails. Docker-in-Docker is out
of scope. Podman aliased as `docker` may work but is not supported.

### 8.13 Unusual file names

Spaces, tabs and unicode are sent as they are. A relative path containing
`\n` is skipped with `Warning: skipping file with a newline in its name:
<repr>`; one that is not valid UTF-8 with `Warning: skipping file whose name
is not valid UTF-8: <repr>`. They are not counted anywhere.

### 8.14 Large repositories

The file list goes through stdin and PDepend reads a staged directory, so
there is no argument-length limit, and the run has no timeout. The
container needs as much space in `/tmp` as the selected files, and PDepend's
memory grows with the selection (about 2 GB for `laravel/framework`'s 3,028
files, [image.md](image.md#11-runtime-environment)). If Docker kills the
container, the non-zero status gives `Error: PDepend failed in <image> (exit
<status>)`; the guide suggests raising Docker's memory limit or narrowing
the selection.

### 8.15 Generated code and tests

Not special-cased. The guide documents `--ignore`/`--exclude` for them (for
example `--ignore 'tests/**'`), since a large test class scores a high total
CCN with simple methods (README §3).

### 8.16 Duplication across the selection only

From #352: jscpd only sees the staged (selected, PHP-parsable) files. See
[duplication.md](duplication.md#3-per-file-duplicated-lines).

### 8.17 Refused lines

The image refuses absolute paths, `..` segments, empty and duplicate lines,
paths that are not a regular file under `/src`, unsupported extensions and
Blade templates (see [image.md](image.md#4-entrypoint-input)). Tingle's
selection never sends such lines, but a file deleted between the selection
and the run is refused as `not a regular file under /src`. Each refused line
prints `Warning: the image skipped <line>: <message>` (`<line>` as sent) and
is shown as `OK` with CCN 0.

### 8.18 Encodings and line endings

CRLF line endings and a UTF-8 BOM give the same results as LF without a BOM.
A file that is not valid UTF-8 (for example ISO-8859-1) is analysed
normally: PHP source has no encoding requirement (unlike `js_complexity`,
where it is a `PARSE` row).

### 8.19 Path-less PDepend messages

A line in PDepend's error block that names no staged file becomes a
path-less `pdepend` warning; tingle prints
`Warning: PDepend reported: <message>` and goes on.

## 9. Exit codes

| Code | Causes |
|------|--------|
| `0` | Report printed and the gate passed or was not set; nothing selected; `--help`. `PARSE` rows, refused lines and jscpd warnings do not change it. |
| `1` | Usage error; `<path>` missing or unreadable; mount root with `:`; tingle version unreadable without `--image`; config error (#350); `docker` not on PATH; `docker info` failed or timed out; image pull failed; mount failure; any non-zero container status (PDepend or entrypoint failure); unparsable container output. |
| `2` | `--fail-on LEVEL` is set and at least one level row (files with `pdepend: null` included, `PARSE` rows excluded) reaches `LEVEL`. |

The gate uses every selected file, not only the displayed rows.

## 10. Messages

Errors are `Error: <message>` in red on stderr, then exit 1. Warnings are
`Warning: <message>` in yellow on stderr. The Docker messages come from
`docker_check` with `command="tingle code_check php_complexity"` and
`tool="PDepend"`.

| Case | Text |
|------|------|
| `docker` not found | `Error: docker not found on PATH; tingle code_check php_complexity needs Docker to run PDepend` |
| Daemon not responding | `Error: the Docker daemon is not responding (docker info failed); start Docker and retry` |
| Pull progress (dim, not an error) | `Pulling <image> ...` |
| Pull failure | `Error: could not pull image <image>` |
| `docker` cannot be started | `Error: could not run docker: <exception>` |
| Mount failure | `Error: Docker could not mount <root>; on Docker Desktop, share it (or a parent folder) under Settings > Resources > File sharing, then retry` |
| Container failure (after the container stderr) | `Error: PDepend failed in <image> (exit <status>)` |
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
| Path-less PDepend message | `Warning: PDepend reported: <message>` |
| Nothing selected (stdout, yellow) | `No PHP files found for analysis.` |
| No row left after the display filters (stdout) | `No files at or above <LEVEL>.` |

**Order** of the warnings printed after the run: the refused-line warnings
(in `warnings` order), then the `cannot parse` warnings (sorted by sent
line), then the path-less `pdepend` warnings (in `warnings` order), then the
jscpd warning of #352. Config errors use `file_size`'s wording; see
[config.md](config.md#5-error-handling).

## 11. Tests

Tests live under `python/tests/code_check/php_complexity/`. `docker` is
never run: `shutil.which` and `subprocess.run` are mocked, and the container
stdout is built from the merged JSON in [image.md](image.md#7-merged-json).
Coverage stays at or above 75%. They cover at least:

- dispatch, the subcommand list, `long_help` mentioning `php_complexity`,
  and completion;
- flags: defaults, float thresholds, negative values, bad choices and an
  empty `--image` exiting 1;
- levels: each boundary (`s == warn`, `s == error`, `s == critical`), and a
  decimal threshold (`--warn 2.5`: CCN 2 is `OK`, 3 is `WARN`);
- image resolution and the exact `docker run` arguments and stdin, for a
  directory and a single file;
- preflight, pull and container outcomes (mount failure, non-zero status
  with the `PDepend failed` message, each unparsable-output reason, success);
- parsing: the full shape (with `functions` and `duplication` filled and
  `null`), `files` length and path mismatches, `parse_error` with a non-null
  `pdepend`, booleans as numbers, an unknown `warnings[].tool`, an
  `max_npath` above 2^53;
- report: layout and widths, sort and ties, `--top`, `--min-level`,
  `No files at or above <LEVEL>.`, `PARSE` rows and their warnings (both
  `php` and `pdepend`), `pdepend: null` rows, a `pdepend` object with `null`
  maxima, `MI` rounding (`79.502…` → `80`), the summary with and without the
  skipped part, `CCN: n/a`;
- `--fail-on`: exit 2 when reached, never because of `PARSE`;
- selection: `.php` in any case, `*.blade.php` skipped (any case, also as a
  single file), the default excludes, the `bootstrap/cache` rule, unsendable
  names, `<path>` missing or unreadable, a mount root with `:`.
