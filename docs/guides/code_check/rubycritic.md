# `tingle code_check rubycritic`

Ruby code complexity via RubyCritic (Docker).

This is a subcommand of [`tingle code_check`](../code_check.md).

## What it does

`tingle code_check rubycritic` finds the Ruby files that are the hardest to
read and maintain, so you know where to refactor first.

It selects the `.rb` files under a file or directory on your machine, then
runs [RubyCritic](https://github.com/whitesmith/rubycritic) on them inside the
`darthjee/tingle_rubycritic` Docker image. RubyCritic combines three
analysers:

- **Flog**: how complex the code is;
- **Flay**: how much code is duplicated;
- **Reek**: code smells (long methods, feature envy, ...).

Each file gets one row in a report, labelled OK, WARN, ERROR or CRITICAL.
The label comes from the file's **total Flog complexity** compared with
thresholds you can configure. RubyCritic's rating (A to F) is shown too, for
information only: it never changes the label or the exit status.

## Requirements

- **Docker**, with the `docker` command on your `PATH` and a running daemon.
  You do not need Ruby on your machine: RubyCritic runs inside the image.
- The image is **pulled automatically** the first time you use it. The pull
  progress is shown on standard error, after a `Pulling <image> ...` line.
  The default image tag is pinned to your tingle version, so once the image
  is present it is never pulled again.
- **Podman**: it may work when aliased as `docker`, but it is not supported.
- **Docker Desktop** (macOS, Windows): the folder you analyse must be covered
  by the file-sharing setting (Settings > Resources > File sharing).
  Otherwise Docker cannot mount it and the command fails with a hint.

The container runs sandboxed: with no network, with your folder mounted
read-only, and as your own user and group id, so it cannot change your files.

## Usage

```
tingle code_check rubycritic <path> [options]
```

`<path>` can be:

- **a directory**: every `.rb` file below it is analysed, recursively,
  except for the excluded directories (see [Skipped files](#skipped-files));
- **a single `.rb` file**: only that file is analysed. Its parent directory
  is mounted into the container. A file that does not end in `.rb` leaves
  nothing to analyse.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `--warn N` | `100` | Files with a total Flog complexity of at least `N` are marked WARN. |
| `--error N` | `200` | Files with a total Flog complexity of at least `N` are marked ERROR. |
| `--critical N` | `400` | Files with a total Flog complexity of at least `N` are marked CRITICAL. |
| `--top N` | `0` | Show only the `N` most complex files. `0` shows all files. |
| `--min-level LEVEL` | `ok` | Show only files at `LEVEL` or higher. `LEVEL` is `ok`, `warn`, `error` or `critical`. |
| `--fail-on LEVEL` | off | Exit with status `2` if any file is at `LEVEL` or higher. `LEVEL` is `warn`, `error` or `critical`. |
| `--image IMAGE` | `darthjee/tingle_rubycritic:<tingle version>` | Docker image to run. |
| `--details [N]` | off | Under each shown file, list its `N` most complex methods. `--details` alone means `5`; `0` lists every method. |

The thresholds accept decimals (`--warn 12.5`) and must be `0` or more.
`--top` and `--details N` must be whole numbers, `0` or more, and `--image`
must not be empty.
The order of the thresholds is not checked: keep `warn` < `error` <
`critical`, or the labels will not make sense.

### `--min-level` and `--top`

These options only change **which level rows are shown**:

- `--min-level LEVEL` keeps the rows at `LEVEL` or higher, using the order
  OK < WARN < ERROR < CRITICAL;
- then `--top N` (when `N` is more than `0`) keeps the `N` most complex rows
  left.

`⛔ PARSE` rows (files RubyCritic could not parse) are **always shown**,
below the level rows, and are not counted by `--top`.

When no row at all is left to show, the table is replaced by a short note,
followed by the usual summary:

```
No files at or above WARN.
```

The `Summary:` line and the `--fail-on` gate always count every selected
file, shown or not.

### `--fail-on`

Turns the command into a complexity gate, for example in CI. The command
fails when at least one file is classified at `LEVEL` or higher:

| `--fail-on` | Fails on |
| --- | --- |
| `warn` | WARN, ERROR or CRITICAL files |
| `error` | ERROR or CRITICAL files |
| `critical` | CRITICAL files only |

The full report is always printed first; then the command exits with status
`2` if the gate failed, or `0` if it passed. Without `--fail-on`, a completed
analysis always exits `0`.

- `--top` and `--min-level` do not hide files from the gate.
- `⛔ PARSE` rows never trigger the gate: a file that cannot be parsed does
  not fail the build.
- If there are no `.rb` files to analyse, the command exits `0`.

### `--details`

Drills down from a file to the methods that make it complex. Under each
shown file row, the command lists the file's most complex methods, each with
its own Flog score, its name and where it starts:

```
$ tingle code_check rubycritic fixture --warn 10 --error 50 --critical 100 --top 2 --details 2
...
Status           Complexity  Rating  Smells  Duplication  File
──────────────── ──────────  ──────  ──────  ───────────  ──────────────────────────────────────────────────
🔴 ERROR               72.25  B           14            0  fixture/complex.rb
                      41.30  Complex#run  (fixture/complex.rb:2)
                      18.45  Complex#normalize  (fixture/complex.rb:31)
⚠️  WARN              15.11  C           11           39  fixture/dup_a.rb
                       9.80  DupA#process  (fixture/dup_a.rb:3)
                       5.31  DupA#report  (fixture/dup_a.rb:15)
⛔ PARSE                   -  -            -            -  fixture/broken.rb
...
```

- `--details` without a number shows up to **5** methods per file;
  `--details N` shows up to `N`; `--details 0` shows **every** method.
- Without `--details`, no method lines are printed.
- Methods are sorted by score, highest first, then by name. A file with
  fewer methods shows only those it has; a file with no methods (for example
  one with only constants) gets no method lines.
- Only the **shown** rows get method lines: `--min-level` and `--top` pick
  the files first, then `--details` adds lines under each of them. `⛔ PARSE`
  rows never get method lines.
- Methods have **no level**: they are not labelled OK/WARN/ERROR/CRITICAL,
  are not counted in the `Summary:` line, and never affect `--fail-on` or
  the exit status. The gate stays based on each file's total complexity.

`--details` needs an image that reports per-method scores. The default image
always does; an older or custom image passed with `--image` may not, and
then the command fails (see [Exit status and errors](#exit-status-and-errors)).

### `--image`

By default the image is `darthjee/tingle_rubycritic:<tingle version>`, where
the version is read from tingle's own `shell/linux/VERSION` file, so each
tingle release uses the matching image. `--image` runs another image
instead, for example one you built locally:

```
tingle code_check rubycritic ./app --image tingle_rubycritic:dev
```

The image is pulled only when it is not present locally. If tingle cannot
read its version file (and you did not pass `--image`), the command fails
and suggests `--image`:

```
Error: cannot read the tingle version from /path/to/tingle/shell/linux/VERSION; use --image to choose the image
```

## Skipped files

When `<path>` is a directory, only files ending in `.rb` (in any case) are
selected, and these directories are always skipped:

```
node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,.cache,coverage,.nuxt,out,target,tmp,log,.bundle
```

That is the [`file_size`](file_size.md#--exclude) default list plus `tmp`,
`log` and `.bundle`. A file is skipped when any part of its path relative to
`<path>` matches one of the names (case-insensitive, whole path component).
The list does not apply to a single-file `<path>`.

A few details:

- There is no binary check: a `.rb` file that is not valid UTF-8 is still
  sent to RubyCritic, and shows up as a `⛔ PARSE` row.
- File names are sent to the container one per line, as UTF-8. A file whose
  name contains a newline, or whose name is not valid UTF-8, cannot be sent:
  it is skipped with a warning on standard error and not counted anywhere:

  ```
  Warning: skipping file with a newline in its name: 'app/odd\nname.rb'
  Warning: skipping file whose name is not valid UTF-8: 'app/caf\udce9.rb'
  ```

- If no `.rb` file is left, the command prints the header and
  `No Ruby files found for analysis.`, then exits `0` without calling Docker
  at all.

## Reading the output

Sample run against a small project, with low thresholds:

```
$ tingle code_check rubycritic fixture --warn 10 --error 50 --critical 100
Analyzing: /home/me/fixture
Thresholds: warn=10 | error=50 | critical=100
Image: darthjee/tingle_rubycritic:0.5.0

Status           Complexity  Rating  Smells  Duplication  File
──────────────── ──────────  ──────  ──────  ───────────  ──────────────────────────────────────────────────
🔴 ERROR               72.25  B           14            0  fixture/complex.rb
⚠️  WARN              15.11  C           11           39  fixture/dup_a.rb
⚠️  WARN              15.11  C           11           39  fixture/dup_b.rb
✅ OK                   0.00  A            0            0  fixture/constants_only.rb
✅ OK                   0.00  A            0            0  fixture/empty.rb
✅ OK                   0.00  A            1            0  fixture/simple.rb
⛔ PARSE                   -  -            -            -  fixture/broken.rb

──────────────────────────────────────────────────────────────────────────────
Summary: 7 file(s) | 3 OK | 2 WARN | 1 ERROR | 0 CRITICAL | 1 skipped (parse error)
Score: 83.23/100 (RubyCritic)
```

Before the report, a warning for `broken.rb` is printed on standard error
(see [Parse warnings](#parse-warnings)).

### Header

- `Analyzing:` shows the target as an absolute path.
- `Thresholds:` shows the `warn`, `error` and `critical` values in use.
- `Image:` shows the Docker image that runs RubyCritic.

### Method lines

With [`--details`](#--details), indented lines follow some file rows, one per
method, dimmed in a terminal:

```
                      41.30  Complex#run  (fixture/complex.rb:2)
```

- the method's own Flog score, aligned under the `Complexity` column;
- the method's name, as `Class#method` for an instance method or
  `Class::method` for a class method;
- in parentheses, the file (as in the `File` column) and the line where the
  method starts.

A file's method scores usually do not add up to its total complexity: the
total also counts code outside methods.

### Columns

| Column | Meaning |
| --- | --- |
| `Status` | The level of the file (see [Classifications](#classifications)). |
| `Complexity` | The file's total Flog complexity, with 2 decimals. `0.00` for a file with no code. This is the value compared with the thresholds. |
| `Rating` | RubyCritic's rating, `A` (best) to `F` (worst); there is no `E`. Information only. |
| `Smells` | The number of Reek smells in the file. Flog and Flay findings are not counted here. |
| `Duplication` | The Flay mass of the duplicated code in the file. `0` means no duplication. |
| `File` | For a directory target, the path relative to the target's parent directory, so it starts with the directory's name (`fixture/...` above). For a single-file target, only the file name. |

### Classifications

With the default thresholds:

| Status | Rule | Default range |
| --- | --- | --- |
| ✅ OK | complexity below `--warn` | below 100 |
| ⚠️ WARN | at least `--warn`, below `--error` | 100 to below 200 |
| 🔴 ERROR | at least `--error`, below `--critical` | 200 to below 400 |
| 🟣 CRITICAL | at least `--critical` | 400 and above |
| ⛔ PARSE | RubyCritic could not parse the file | - |

Each threshold is inclusive: a file with a complexity of exactly 200 is
ERROR, not WARN. A `⛔ PARSE` row shows `-` in every number column.

### Sort order

Level rows come first, sorted by complexity, highest first; files with the
same complexity are sorted by path. The `⛔ PARSE` rows follow, sorted by
path.

### Summary

- `Summary:` shows the number of selected files (`⛔ PARSE` files included)
  and how many fall into each level. When some files could not be parsed,
  `| k skipped (parse error)` is added at the end.
- `Score:` is RubyCritic's overall score for the analysed code, from `0` to
  `100` (higher is better), for example `Score: 83.23/100 (RubyCritic)`. When
  RubyCritic had nothing to score (every file failed to parse), it shows
  `Score: n/a (RubyCritic)`.

Both lines always cover every selected file, even when `--top` or
`--min-level` hide some rows.

### Parse warnings

Each file RubyCritic cannot parse (a syntax error, or a file that is not
valid UTF-8) prints a warning on standard error, before the report:

```
Warning: cannot parse fixture/broken.rb: unexpected token tSTRING
```

It appears as a `⛔ PARSE` row and in the `skipped (parse error)` count, but
never in the level counts, and it never changes the exit status.

### Files missing from the output

In rare cases RubyCritic silently leaves out a file it was given, for
example a file deleted between the selection and the run. Such a file is
still listed, as `✅ OK` with complexity `0.00`, rating `-`, `0` smells and
`0` duplication, so the file count matches the selection.

### Colours

The output is coloured with ANSI escape codes only when it is written to a
terminal. When it is redirected to a file or a pipe (as in most CI logs), it
is plain text with the same layout and emoji labels. Standard output and
standard error are checked separately.

To turn colours off in a terminal too, set the
[`NO_COLOR`](https://no-color.org/) environment variable to any non-empty
value:

```
NO_COLOR=1 tingle code_check rubycritic ./app
```

## Examples

Analyse every Ruby file under `./app` with the default settings:

```
tingle code_check rubycritic ./app
```

Use lower thresholds:

```
tingle code_check rubycritic ./app --warn 50 --error 100 --critical 200
```

Show only the 10 most complex files at WARN or higher:

```
tingle code_check rubycritic ./app --top 10 --min-level warn
```

Show the 5 most complex files, each with its 3 most complex methods:

```
tingle code_check rubycritic ./app --top 5 --details 3
```

Run a locally built image:

```
tingle code_check rubycritic ./app --image tingle_rubycritic:dev
```

Analyse a single file:

```
tingle code_check rubycritic ./app/models/user.rb
```

### Using in CI

Fail the build when any Ruby file under `./app` reaches the ERROR threshold:

```
tingle code_check rubycritic ./app --fail-on error
```

The report is printed as usual, and the step fails with exit status `2` if
an ERROR or CRITICAL file is found. The CI runner needs Docker (see
[Requirements](#requirements) and [Limitations](#limitations)).

## Exit status and errors

Errors are printed on **standard error** as `Error: <message>`.

| Situation | Output | Exit status |
| --- | --- | --- |
| No arguments, or `--help` | The option help | `0` |
| Unknown option or invalid value (e.g. `--top abc`, `--fail-on foo`) | A usage error | `1` |
| Negative threshold | `Error: --warn must be a number >= 0` (`--error`, `--critical` likewise) | `1` |
| Negative `--top` | `Error: --top must be an integer >= 0` | `1` |
| Negative `--details` | `Error: --details must be an integer >= 0` | `1` |
| Empty `--image` | `Error: --image must not be empty` | `1` |
| `<path>` does not exist | `Error: path not found: <absolute path>` | `1` |
| `<path>` cannot be read | `Error: path not readable: <absolute path>` | `1` |
| The folder to mount contains `:` | `Error: cannot mount <folder>: Docker volume paths cannot contain ':'` | `1` |
| Tingle version unreadable and no `--image` | `Error: cannot read the tingle version from <file>; use --image to choose the image` | `1` |
| No `.rb` files to analyse | The header, then `No Ruby files found for analysis.` | `0` |
| `docker` not on `PATH` | `Error: docker not found on PATH; tingle code_check rubycritic needs Docker to run RubyCritic` | `1` |
| Docker daemon not running (`docker info` failed or took over 30 seconds) | `Error: the Docker daemon is not responding (docker info failed); start Docker and retry` | `1` |
| Image pull failed | `Pulling <image> ...` and Docker's output, then `Error: could not pull image <image>` | `1` |
| `docker run` could not be started | `Error: could not run docker: <reason>` | `1` |
| Folder not shared with Docker Desktop | Docker's error, then `Error: Docker could not mount <folder>; on Docker Desktop, share it (or a parent folder) under Settings > Resources > File sharing, then retry` | `1` |
| RubyCritic or the container failed | The container's error output, then `Error: RubyCritic failed in <image> (exit <status>)` | `1` |
| Unexpected output from the container | The container's error output, then `Error: could not parse the RubyCritic output from <image>: <reason>` | `1` |
| `--details` with an image too old to report per-method scores (e.g. an older custom `--image`) | `Error: the RubyCritic output from <image> has no per-method data; --details needs a newer tingle_rubycritic image` | `1` |
| Analysis completed, no `--fail-on` | The report | `0` |
| Analysis completed, `--fail-on` gate passed | The report | `0` |
| Analysis completed, `--fail-on` gate failed | The report | `2` |

In short:

| Code | Meaning |
| --- | --- |
| `0` | Success, or the complexity gate passed / was not requested |
| `1` | Usage error, path problem, or Docker / RubyCritic failure |
| `2` | The complexity gate failed (`--fail-on`) |

Unparsable Ruby files (`⛔ PARSE` rows) never change the exit status. The
report always goes to standard output and error messages to standard error.

## Limitations

- **No Docker-in-Docker.** The `darthjee/tingle` container (used by
  [`tingle linux`](../linux.md)) has no `docker` command, so running this
  subcommand inside it fails with `docker not found on PATH`. Run it on a
  host with Docker.
- **No file filters yet.** The `--exclude`, `--no-default-excludes`,
  `--ignore` and `--include` options, and `.gitignore` support, are not
  available yet: only the [default excludes](#skipped-files) apply.
- **No configuration file yet.** This subcommand does not read
  `~/.tingle/code_check/config.json`, and there is no `--no-config` option
  yet. Pass the options on the command line.

## Quick help

For a short summary of the command's options, run:

```
tingle code_check rubycritic --help
```

`tingle --help code_check` shows the options of every `code_check`
subcommand, together with their list.
