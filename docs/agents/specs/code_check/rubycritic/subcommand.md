# Spec: the `tingle code_check rubycritic` subcommand

Sub-issue: #295. Parent: #290. Shared contracts: [README.md](README.md).

This spec covers the subcommand core: dispatch, the flags added here, the
Docker preflight and run, the RubyCritic JSON contract, the report, exit codes
and edge cases. File selection flags come in #296
([file-selection.md](file-selection.md)) and the config section in #297
([config.md](config.md)).

## 1. Dispatch and package

- New package `python/code_check/rubycritic/`, laid out like
  `python/code_check/file_size/`:
  - `flags.py`: `FLAGS`, import-light (completion imports it);
  - `constants.py`: thresholds, default excludes, image name, smell types;
  - `executor.py`: the orchestration class (`CheckRubycritic`, with
    `run(args)`), `PROG = "tingle code_check rubycritic"`;
  - one module each for the Docker runner, the JSON parsing and the reporter.
- `python/code_check/executor.py`: add
  `"rubycritic": (CheckRubycritic, "Ruby code complexity via RubyCritic (Docker).")`
  to `SUBCOMMANDS`, after `file_size`.
- `python/code_check/subcommands.py`: `SUBCOMMAND_NAMES` becomes
  `("file_size", "rubycritic")`.
- `commands/python.json`: the `code_check` `short_help` lists both
  subcommands, and `long_help` gets a `rubycritic` part in the same shape as
  the `file_size` one (usage, flags, examples, exit status).
- `python/code_check/completion.py`: `rubycritic` gets the same completion
  as `file_size`, from `code_check.rubycritic.flags.FLAGS`: flag names, the
  `choices` of choice flags, nothing for free-form values (`--image`,
  `--warn`, ...), and the file sentinel for the path.
- Docs in the same PR: a `rubycritic` page or section in
  `docs/guides/code_check.md` (with the Podman note: Podman aliased as
  `docker` may work but is not supported), `docs/agents/architecture.md`, and
  the `README.md` table.

## 2. Flags and levels

Flags added by #295 (see [README.md](README.md#3-cli-and-flags) for the full
table):

| Flag | Type | Default | Help |
|------|------|---------|------|
| `path` | str | required | `Ruby file or directory to analyse (recursive)` |
| `--warn N` | float ≥ 0 | `100` | `Warn threshold on the file's total Flog complexity (default: 100)` |
| `--error N` | float ≥ 0 | `200` | `Error threshold on the file's total Flog complexity (default: 200)` |
| `--critical N` | float ≥ 0 | `400` | `Critical threshold on the file's total Flog complexity (default: 400)` |
| `--top N` | int ≥ 0 | `0` (all) | `Show only the top N most complex files (default: 0 = all)` |
| `--min-level LEVEL` | `ok\|warn\|error\|critical` | `ok` | `Show only files at this level or higher (default: ok)` |
| `--fail-on LEVEL` | `warn\|error\|critical` | none | `Exit with status 2 if any file reaches this level or higher` |
| `--image IMAGE` | non-empty str | `darthjee/tingle_rubycritic:<tingle version>` | `Docker image to run (default: darthjee/tingle_rubycritic:<tingle version>)` |

- Single-value flags default to `None` in `FLAGS`; the built-in defaults are
  applied after the (later) config merge, as in `file_size`.
- `--warn`, `--error`, `--critical` parse as `float`. A negative value, a
  negative `--top` or an empty `--image` is a usage error:
  `Error: --warn must be a number >= 0` (the flag name varies),
  `Error: --top must be an integer >= 0`, `Error: --image must not be empty`.
  Exit 1. Argparse's own usage errors are remapped from 2 to 1, as in
  `file_size`.
- The thresholds are not checked against each other (as in `file_size`).

**Levels.** The level of a file comes from its complexity `c` (the
`complexity` field, section 5) with the same comparisons as `file_size`'s
`FileAnalyzer.classify`:

| Condition (checked in this order) | Level | Label |
|-----------------------------------|-------|-------|
| `c >= critical` | `critical` | `🟣 CRITICAL` |
| `c >= error` | `error` | `🔴 ERROR` |
| `c >= warn` | `warn` | `⚠️  WARN` |
| otherwise | `ok` | `✅ OK` |

`FileAnalyzer.classify`/`reaches` already work with floats and may be reused.
The rating (A–F) is shown for information only and never sets the level.

## 3. Run order, preflight and pulling

`run(args)` does, in this order:

1. No arguments: print the help, exit 0.
2. Parse the flags (usage errors exit 1).
3. Load the config (#297; before #297 there is no config).
4. Resolve `<path>` (`Path(path).resolve()`):
   - it does not exist: `Error: path not found: <resolved>`, exit 1;
   - it exists but cannot be read (`os.access` without `R_OK`, or a
     directory without `X_OK`): `Error: path not readable: <resolved>`,
     exit 1.
   - the mount root is `<resolved>` for a directory, its parent for a file.
     If the mount root contains `:`, Docker's `-v` cannot express it:
     `Error: cannot mount <root>: Docker volume paths cannot contain ':'`,
     exit 1.
5. Resolve the image (section 4).
6. Print the header (section 6).
7. Select the files (section 7). If none are left, print
   `No Ruby files found for analysis.` (yellow, stdout) and exit 0, **without
   any Docker call**, not even the preflight.
8. **Preflight**, in this order:
   - `shutil.which("docker")` is `None`: `Error: docker not found on PATH;
     tingle code_check rubycritic needs Docker to run RubyCritic`, exit 1.
     This is also what happens inside the `darthjee/tingle` container, which
     has no `docker` (Docker-in-Docker is out of scope).
   - `docker info`, with stdout and stderr discarded and a 30-second timeout.
     A non-zero status or a timeout: `Error: the Docker daemon is not
     responding (docker info failed); start Docker and retry`, exit 1.
9. **Pull when missing:** `docker image inspect <image>` (output discarded).
   When it fails, tingle prints `Pulling <image> ...` (dim, stderr) and runs
   `docker pull <image>` with its stdout and stderr sent to tingle's stderr,
   so the progress is visible. A failed pull: `Error: could not pull image
   <image>`, exit 1. Pinned tags never change, so an image that is present is
   never pulled again.
10. **Run** the container (section 4) and parse its stdout (section 5).
11. Print one warning per `parse_errors` entry (section 8.1).
12. Print the report (section 6), then exit 2 if the `--fail-on` gate failed,
    else 0.

## 4. The docker run line

**Image resolution.**

- `--image` (or, from #297, the `image` config key) wins when set.
- Otherwise the image is `darthjee/tingle_rubycritic:<version>`, where
  `<version>` is the content of `shell/linux/VERSION` with all whitespace
  removed, the way `shell/linux/docker_run.sh` and
  `scripts/release_image.sh` read it.
- `shell/linux/VERSION` is the runtime source of truth for the tingle
  version. It ships in the release zip (`shell/` is in the `INCLUDES` of
  `scripts/release_cli.sh`) and is kept in sync by `scripts/bump-version.sh`.
  It is found from the repo root, computed from the module's own path
  (`Path(__file__).resolve().parents[3]` for a module in
  `python/code_check/rubycritic/`), never from the current directory.
- If the file is missing, unreadable or empty (and no `--image` is given):
  `Error: cannot read the tingle version from <file>; use --image to choose
  the image`, exit 1.

**Run line.** The argument list is exactly:

```
docker run --rm -i --pull never --network none
  --security-opt no-new-privileges
  --user <uid>:<gid>
  -v <root>:/src:ro
  -w /src
  <image>
```

- `<uid>` and `<gid>` are `os.getuid()` and `os.getgid()`.
- `<root>` is the mount root from section 3 (absolute, resolved).
- `--pull never`: the pull already happened in section 3, step 9, so the run
  itself never contacts a registry.
- It is run with `subprocess.run` (no shell), with stdin, stdout and stderr
  as pipes. Stdin gets the selected files: their paths relative to `<root>`,
  POSIX separators, UTF-8, one per line, each followed by `\n`, sorted by
  path. For a single-file `<path>`, the only line is the file name.
- There is no timeout on the run: large repositories take as long as they
  take.

**Outcome.** Let `status` be the container's exit status:

| Case | Behaviour |
|------|-----------|
| `status == 125` and stderr contains `mounts denied` or `not shared from the host` (case-insensitive) | Write the container stderr to tingle's stderr, then the mount error with the Docker Desktop hint (section 10). Exit 1. |
| any other non-zero `status` | Write the container stderr to tingle's stderr, then `Error: RubyCritic failed in <image> (exit <status>)`. Exit 1. |
| `status == 0`, stdout fails the checks in section 5 | Write the container stderr to tingle's stderr, then `Error: could not parse the RubyCritic output from <image>: <reason>`. Exit 1. |
| `status == 0`, stdout valid | The container stderr is discarded. Continue. |

Docker uses 125 for its own failures (daemon errors, mounts, a missing image)
and 126/127 when the entrypoint cannot run. Both were checked against Docker
29 (`mounts denied: The path ... is not shared from the host and is not
known to Docker.`, exit 125).

## 5. RubyCritic JSON contract

The entrypoint prints RubyCritic's `report.json` plus a `parse_errors` key
(see [image.md](image.md#4-entrypoint-contract)). This trimmed sample comes
from a real run of `rubycritic 5.0.0` on the fixture (smell lists cut to one
entry, `simple.rb`, `dup_b.rb` and `constants_only.rb` removed, the
`broken.rb` entry from the entrypoint run):

```json
{
  "metadata": {"rubycritic": {"version": "5.0.0"}},
  "analysed_modules": [
    {
      "name": "Complex",
      "path": "complex.rb",
      "smells": [
        {
          "context": "Complex#run",
          "cost": 0,
          "locations": [{"path": "complex.rb", "line": 2}],
          "message": "has a flog score of 72",
          "score": 72,
          "status": "new",
          "type": "VeryHighComplexity"
        }
      ],
      "churn": 0,
      "committed_at": null,
      "complexity": 72.25,
      "duplication": 0,
      "methods_count": 1,
      "cost": 2.89,
      "rating": "B"
    },
    {
      "name": "DupA",
      "path": "dup_a.rb",
      "smells": [
        {
          "context": "Identical code",
          "cost": 6,
          "locations": [
            {"path": "dup_a.rb", "line": 2},
            {"path": "dup_b.rb", "line": 2}
          ],
          "message": "found in 2 nodes",
          "score": 156,
          "status": "new",
          "type": "DuplicateCode"
        }
      ],
      "churn": 0,
      "committed_at": null,
      "complexity": 15.11,
      "duplication": 39,
      "methods_count": 1,
      "cost": 6.6044,
      "rating": "C"
    },
    {
      "name": "Empty",
      "path": "empty.rb",
      "smells": [],
      "churn": 0,
      "committed_at": null,
      "complexity": 0.0,
      "duplication": 0,
      "methods_count": 0,
      "cost": 0.0,
      "rating": "A"
    }
  ],
  "score": 83.23,
  "parse_errors": [
    {"path": "broken.rb", "message": "unexpected token tSTRING"}
  ]
}
```

**Fields used.** `m` is one entry of `analysed_modules`.

| Report item | JSON path | Type | Notes |
|-------------|-----------|------|-------|
| File | `m.path` | str | Mapped back as below. |
| `Complexity` (and the level) | `m.complexity` | number | Flog's total score for the file, rounded to 2 decimals by RubyCritic. `0.0` for a file with no code. |
| `Rating` | `m.rating` | str | One of `A`, `B`, `C`, `D`, `F` (RubyCritic has no `E`). From `m.cost`: ≤2 A, ≤4 B, ≤8 C, ≤16 D, else F. |
| `Smells` | `m.smells` | list | Count of entries whose `type` is **not** `DuplicateCode` (Flay), `HighComplexity` or `VeryHighComplexity` (Flog). That is the Reek smell count. The JSON has no analyser field. |
| `Duplication` | `m.duplication` | number | Flay mass for the file (integer in practice). |
| `PARSE` rows | `parse_errors[].path`, `parse_errors[].message` | list of objects | Added by the entrypoint. |
| `Score:` | `score` (top level) | number or `null` | RubyCritic's overall score, 0–100. `null` when RubyCritic did not run (every file failed to parse). |

Fields not used: `name` (derived from the file name, e.g. `Empty`),
`churn` (always `0` without git), `committed_at` (`null`), `methods_count`,
`cost`, `metadata`. Each file appears once in `analysed_modules`, even when it
holds several classes.

**Checks.** The output is unparsable (section 4) when any of these fail; the
`<reason>` names the first failure:

- stdout is one JSON object (`invalid JSON: <error>` /
  `expected a JSON object`);
- `analysed_modules` is a list, and each entry has `path` (str),
  `complexity` (number), `rating` (str), `smells` (list) and `duplication`
  (number) (`unexpected analysed_modules entry: <path or index>`);
- `score` is a number or `null` (`unexpected score`);
- `parse_errors` is a list of objects with `path` and `message` strings
  (`unexpected parse_errors`).

JSON booleans are not numbers here.

**Path mapping.** The entrypoint passes the stdin paths to RubyCritic as
they are, so `m.path` is the sent path, relative to `/src` (RubyCritic only
removes a leading `./`; an absolute path would stay absolute). Tingle:

1. removes a leading `/src/`, then any leading `./`, from `m.path` and
   `parse_errors[].path`;
2. matches the result exactly against the lines it sent;
3. ignores entries that match no sent line, and keeps only the first entry
   for a path given twice;
4. turns each sent line back into its host path (`<root>/<line>`) for the
   report.

## 6. Report

The report goes to stdout and mirrors `file_size`'s `Reporter`.

**Header.**

```
Analyzing: <resolved path>
Thresholds: warn=<w> | error=<e> | critical=<c>
Image: <image>
Config: <config file>        (only when a config section was loaded, #297)
<blank line>
```

`Analyzing:` is cyan and bold; the other lines are dim. Thresholds print with
`format(value, "g")` (`100`, `12.5`).

**Table.**

```
Status            Complexity  Rating  Smells  Duplication  File
──────────────── ──────────  ──────  ──────  ───────────  ──────────────────────────────────────────────────
```

- Header: `f"{'Status':<16} {'Complexity':>10}  {'Rating':<6}  {'Smells':>6}  {'Duplication':>11}  File"`.
- Separator: `─` repeated 16, 10, 6, 6, 11 and 50 times, with the same
  spacing.
- Row: the level label padded to 16 and coloured like `file_size`
  (`Palette.level_color`), then the complexity with 2 decimals (`72.25`), the
  rating, the smell count and the duplication (as an integer), aligned like
  the header, then the file.
- File: the same display rule as `file_size`: the path relative to the
  target's parent for a directory `<path>` (so it starts with the directory
  name), the file name for a single-file `<path>`.
- Order: level rows sorted by complexity, highest first, ties by file path
  (ascending); then the `PARSE` rows (section 8.1), sorted by file path.

**Display filters.** `--min-level` and `--top` only change which level rows
are shown. `--min-level` keeps rows at that level or higher, then `--top N`
(when N > 0) keeps the first N. `PARSE` rows are always shown, below the
level rows, and are not counted by `--top`. When no row at all is left to
show (and files were analysed), the table is replaced by
`No files at or above <LEVEL>.`, as in `file_size`.

**Summary.** It always counts every selected file, whatever `--min-level`
and `--top` are:

```
<blank line>
────────────────────────────────────────────────────────────────────────────── (78 × ─, gray)
Summary: <N> file(s) | <a> OK | <b> WARN | <c> ERROR | <d> CRITICAL[ | <k> skipped (parse error)]
Score: <score>/100 (RubyCritic)
```

- `<N>` is the number of selected files, `PARSE` files included. `<a>` to
  `<d>` count the level rows (dropped files count as `OK`).
- ` | <k> skipped (parse error)` (gray) is appended only when `<k>` > 0.
- `<score>` has 2 decimals (`83.23`). When `score` is `null` the line is
  `Score: n/a (RubyCritic)`.
- There is no `Total:` line.

**Full example** (`tingle code_check rubycritic fixture --warn 10 --error 50
--critical 100` on the step-01 fixture, no colours):

```
Analyzing: /home/me/fixture
Thresholds: warn=10 | error=50 | critical=100
Image: darthjee/tingle_rubycritic:0.6.0

Status            Complexity  Rating  Smells  Duplication  File
──────────────── ──────────  ──────  ──────  ───────────  ──────────────────────────────────────────────────
🔴 ERROR               72.25  B           14            0  fixture/complex.rb
⚠️  WARN               15.11  C           11           39  fixture/dup_a.rb
⚠️  WARN               15.11  C           11           39  fixture/dup_b.rb
✅ OK                   0.00  A            0            0  fixture/constants_only.rb
✅ OK                   0.00  A            0            0  fixture/empty.rb
✅ OK                   0.00  A            1            0  fixture/simple.rb
⛔ PARSE                   -  -            -            -  fixture/broken.rb

──────────────────────────────────────────────────────────────────────────────
Summary: 7 file(s) | 3 OK | 2 WARN | 1 ERROR | 0 CRITICAL | 1 skipped (parse error)
Score: 83.23/100 (RubyCritic)
```

The warning for `broken.rb` (section 8.1) goes to stderr before the report
body.

## 7. File selection in #295

#295 selects, with `file_size`'s `FileCollector`:

- for a directory `<path>`: the regular files under it whose suffix is `.rb`
  (case-insensitive), minus the default excludes (see
  [README.md](README.md#6-default-excludes) and
  [file-selection.md](file-selection.md#2-default-excludes));
- for a single-file `<path>`: that file if its suffix is `.rb`, else nothing.

`file_size`'s binary check must not apply: #295 adds the keyword-only
argument `binary_check=True` to `FileCollector` and passes
`binary_check=False` (see
[file-selection.md](file-selection.md#5-filter-order-and-filecollector)), so
a `.rb` file that is not valid UTF-8 reaches the image and becomes a `PARSE`
row instead of vanishing.

Files whose name cannot be sent on stdin are dropped with a warning
(section 8.5). #296 adds `--exclude`, `--no-default-excludes`, `--ignore`,
`--include`, `.gitignore`/`--no-gitignore` and the symlink rule.

## 8. Edge cases

### 8.1 Unparsable files (`PARSE`)

- Detection: a sent path listed in `parse_errors` (after the path mapping).
  The image fills `parse_errors` by pre-parsing each file with Reek's parser,
  because RubyCritic itself aborts on the first syntax error (see
  [README.md](README.md#9-contradictions-with-290)). This also catches files
  that are not valid UTF-8.
- Each one prints `Warning: cannot parse <file>: <message>` on stderr
  (`<file>` as displayed in the table, `<message>` from the JSON).
- Row: label `⛔ PARSE` (gray), `-` in the Complexity, Rating, Smells and
  Duplication columns.
- It counts as skipped in the summary, is never in the level counts, and
  never triggers `--fail-on`. It never changes the exit code.
- If a path is in both `parse_errors` and `analysed_modules`, `parse_errors`
  wins.

### 8.2 Single-file `<path>`

The mount root is the file's parent directory; stdin holds only the file
name. The display is the file name.

### 8.3 No `.rb` files

When the selection is empty: header, then `No Ruby files found for
analysis.` (yellow), exit 0. No Docker command runs.

### 8.4 Mount failure (Docker Desktop file sharing)

Detected as in section 4 (exit 125 plus `mounts denied` or `not shared from
the host`). Docker's stderr is passed through, then the error from section 10
with the file-sharing hint. Exit 1.

### 8.5 Unsendable file names

Stdin is newline-separated UTF-8, so two kinds of names cannot be sent:

- a relative path containing `\n`:
  `Warning: skipping file with a newline in its name: <repr>`;
- a relative path that is not valid UTF-8 (it holds surrogate escapes):
  `Warning: skipping file whose name is not valid UTF-8: <repr>`.

`<repr>` is Python's `repr()` of the path relative to `<path>`. These files
are not counted anywhere. Spaces, tabs and other unicode characters are sent
as they are.

### 8.6 Files missing from the output

A sent path that is neither in `analysed_modules` nor in `parse_errors` is
reported as `OK` with complexity `0.00`, rating `-`, smells `0` and
duplication `0`, so the file count matches the selection. With RubyCritic
5.0.0, empty and method-less files are **not** dropped (they come back with
complexity `0.0` and rating `A`), so this only happens when RubyCritic cannot
find a file it was given (it drops it silently and still exits 0), for
example a file deleted between selection and run.

### 8.7 `<path>` missing or unreadable

See section 3, step 4. The messages match `file_size`'s
`path not found: <resolved>` style.

## 9. Exit codes

| Code | Causes |
|------|--------|
| `0` | Report printed and the gate passed or was not set; no `.rb` files selected; `--help`. `PARSE` rows do not change it. |
| `1` | Usage error (bad flag or value, remapped from argparse's 2); `<path>` missing or unreadable; mount root with `:`; tingle version unreadable without `--image`; config error (#297); `docker` not on PATH; `docker info` failed or timed out; image pull failed; mount failure; container or RubyCritic failure (any non-zero container status); unparsable container output. |
| `2` | `--fail-on LEVEL` is set and at least one level row (dropped files included, `PARSE` rows excluded) reaches `LEVEL`. |

The `--fail-on` gate uses every selected file, not only the displayed rows.

## 10. Messages

All errors are `Error: <message>` in red on stderr, followed by exit 1.
Warnings are `Warning: <message>` in yellow on stderr. Placeholders: `<path>`
and `<root>` are resolved absolute paths, `<image>` the resolved image,
`<status>` the container exit status.

| Case | Text |
|------|------|
| `docker` not found | `Error: docker not found on PATH; tingle code_check rubycritic needs Docker to run RubyCritic` |
| Daemon not responding | `Error: the Docker daemon is not responding (docker info failed); start Docker and retry` |
| Pull progress (dim, not an error) | `Pulling <image> ...` |
| Pull failure | `Error: could not pull image <image>` |
| Mount failure | `Error: Docker could not mount <root>; on Docker Desktop, share it (or a parent folder) under Settings > Resources > File sharing, then retry` |
| Container or RubyCritic failure (after the container stderr) | `Error: RubyCritic failed in <image> (exit <status>)` |
| Unparsable output | `Error: could not parse the RubyCritic output from <image>: <reason>` |
| `<path>` missing | `Error: path not found: <path>` |
| `<path>` unreadable | `Error: path not readable: <path>` |
| Mount root with `:` | `Error: cannot mount <root>: Docker volume paths cannot contain ':'` |
| Version file unreadable | `Error: cannot read the tingle version from <file>; use --image to choose the image` |
| Negative threshold | `Error: --warn must be a number >= 0` (`--error`, `--critical` likewise) |
| Negative `--top` | `Error: --top must be an integer >= 0` |
| Empty `--image` | `Error: --image must not be empty` |
| Filename with a newline | `Warning: skipping file with a newline in its name: <repr>` |
| Filename not valid UTF-8 | `Warning: skipping file whose name is not valid UTF-8: <repr>` |
| Unparsable Ruby file | `Warning: cannot parse <file>: <message>` |
| No `.rb` files (stdout, yellow) | `No Ruby files found for analysis.` |

Config errors use `file_size`'s wording; see
[config.md](config.md#5-error-handling).

## 11. Tests

Tests live under `python/tests/code_check/rubycritic/`. `docker` is never
run: `shutil.which` and `subprocess.run` are mocked, and container stdout is
built from the JSON sample in section 5. Coverage stays at or above 75%.
They cover at least:

- dispatch: `tingle code_check rubycritic` reaches `CheckRubycritic`; the
  subcommand list and completion include `rubycritic` and its flags;
- flags: defaults; float thresholds; negative values, bad choices and an empty
  `--image` exit 1;
- levels: each boundary (`c == warn`, `error`, `critical`) and floats;
- image resolution: default from a temporary `VERSION` (with surrounding
  whitespace), `--image` override, missing or empty `VERSION`;
- the exact `docker run` argument list and stdin content, for a directory and
  for a single file (parent mounted, name sent);
- preflight: no `docker`, `docker info` failing, `docker info` timing out;
  no Docker call at all when no `.rb` file is selected;
- pull: image present (no pull), image missing (pull, progress to stderr),
  pull failing;
- container outcomes: mount failure (hint), other non-zero status (stderr
  passed through), invalid JSON, each structural check, success;
- path mapping: plain, `./`-prefixed and `/src/`-prefixed paths; unknown
  paths ignored; dropped files reported as `OK` 0;
- report: column layout, sort order and ties, `--top`, `--min-level`,
  `No files at or above <LEVEL>.`, `PARSE` rows and their warning, the summary
  with and without the skipped part, `Score: n/a`;
- `--fail-on`: exit 2 when reached, 0 when not, never because of `PARSE`;
- unsendable names: newline and non-UTF-8 names skipped with their warnings;
- `<path>` missing, unreadable, and a mount root containing `:`.
