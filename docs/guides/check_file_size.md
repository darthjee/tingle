# `tingle check_file_size`

Token efficiency triage: file size analysis.

## What it does

When you feed a repository to an AI assistant, very long files use up a lot
of tokens and are harder for the model to work with. `tingle
check_file_size` helps you find them before that happens.

It walks a file or directory, counts the lines of every text file it finds,
and lists them from largest to smallest. Each file is labelled OK, WARN,
ERROR or CRITICAL according to line-count thresholds you can configure, so
the files worth splitting or leaving out stand out at a glance.

## Usage

```
tingle check_file_size <path> [options]
```

`<path>` can be:

- **a directory**: every file below it is scanned, recursively, except for
  excluded directories and binary files (see [Skipped files](#skipped-files));
- **a single file**: only that file is analysed.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `--warn N` | `300` | Files with at least `N` lines are marked WARN. |
| `--error N` | `500` | Files with at least `N` lines are marked ERROR. |
| `--critical N` | `1000` | Files with at least `N` lines are marked CRITICAL. |
| `--top N` | `0` | Show only the `N` largest files. `0` shows all files. |
| `--exclude LIST` | see below | Comma-separated directory names to skip. |
| `--ext EXT` | no filter | Only analyse files with this extension. Can be repeated. |
| `--fail-on LEVEL` | off | Exit with status `2` if any file is at `LEVEL` or higher. `LEVEL` is `warn`, `error` or `critical`. |

### `--exclude`

The default list is:

```
node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,.cache,coverage,.nuxt,out,target
```

A file is skipped if **any** part of its path matches one of these names.
Matching is case-insensitive (`Build` matches `build`).

> **Passing `--exclude` replaces the default list. It does not add to it.**
> `--exclude fixtures` skips *only* `fixtures`, so `node_modules`, `.git`
> and the rest are scanned again.

To keep the defaults and skip one more directory, repeat the default list
and add your entry at the end:

```
tingle check_file_size ./src --exclude node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,.cache,coverage,.nuxt,out,target,fixtures
```

The match covers the whole absolute path, including the directories *above*
`<path>`. For example, if your project lives in `~/work/build/my-app`,
every file matches `build` and you get `No files found for analysis.`. In
that case, pass an `--exclude` list that leaves out the conflicting name.

### `--ext`

Limits the analysis to files with the given extension. Repeat the option to
allow more than one:

```
tingle check_file_size ./src --ext .py --ext .js
```

Include the leading dot (`.py`, not `py`). The comparison is
case-insensitive and uses the file's last extension, so `archive.tar.gz`
counts as `.gz`.

### `--fail-on`

Turns the command into a size gate, for example in CI. `LEVEL` is one of
`warn`, `error` or `critical` (lowercase). The command fails when at least
one analysed file is classified at that level **or higher**, using the order
WARN < ERROR < CRITICAL:

| `--fail-on` | Fails on |
| --- | --- |
| `warn` | WARN, ERROR or CRITICAL files |
| `error` | ERROR or CRITICAL files |
| `critical` | CRITICAL files only |

The full report is always printed first; then the command exits with status
`2` if the gate failed, or `0` if it passed. Without `--fail-on`, the gate is
off and a completed analysis always exits `0`.

A few details:

- `--top` does not hide files from the gate. Every analysed file counts,
  including those not shown in the table.
- If there are no files to analyse (`No files found for analysis.`), the
  command exits `0`.
- The level refers to the thresholds in use, so `--warn`, `--error` and
  `--critical` change what the gate catches.

### Single-file targets

When `<path>` is a single file, `--ext` and `--exclude` are ignored. The
file is analysed unless it is detected as binary.

## Skipped files

Besides the directories matched by `--exclude`, binary files are skipped
automatically. A file counts as binary when:

- its extension is a known binary type: images (`.png`, `.jpg`, `.svg`,
  ...), video and audio (`.mp4`, `.mp3`, ...), office documents and PDFs
  (`.pdf`, `.docx`, ...), archives (`.zip`, `.tar`, `.gz`, ...), compiled
  code and libraries (`.exe`, `.so`, `.pyc`, `.class`, `.jar`, `.wasm`,
  ...), fonts (`.ttf`, `.woff2`, ...), databases (`.db`, `.sqlite`, ...),
  and a few others such as `.lock` and `.map`; or
- its first 1024 bytes contain a NUL byte or are not valid UTF-8; or
- it cannot be read (for example, because of permissions).

Hidden directories that are not in the exclude list (for example
`.pytest_cache`) are scanned like any other directory.

## Reading the output

Sample run against a small project:

```
$ tingle check_file_size ./my-app
Analyzing: /home/me/projects/my-app
Thresholds: warn=300 | error=500 | critical=1000

Status                Lines  File
──────────────── ──────────  ──────────────────────────────────────────────────
🟣 CRITICAL            1.234  my-app/src/api/routes.py
🔴 ERROR                 612  my-app/src/api/handlers.py
⚠️  WARN                345  my-app/src/utils/helpers.js
✅ OK                     87  my-app/src/utils/format.js

──────────────────────────────────────────────────────────────────────────────
Summary: 4 file(s) | 1 OK | 1 WARN | 1 ERROR | 1 CRITICAL
Total: 2.278 lines
```

### Header

- `Analyzing:` shows the target as an absolute path.
- `Thresholds:` shows the `warn`, `error` and `critical` values in use.

### Table

- One row per file, with the **Status**, **Lines** and **File** columns.
- Rows are sorted by line count, largest first. `--top N` is applied after
  sorting, so you get the `N` largest files.
- Line counts use `.` as the thousands separator: `1.234` means one
  thousand two hundred and thirty-four lines.
- For a directory target, paths are shown relative to the target's parent
  directory, so they start with the target directory's name (`my-app/...`
  above). For a single-file target, only the file name is shown.

### Classifications

With the default thresholds:

| Status | Rule | Default range |
| --- | --- | --- |
| ✅ OK | fewer than `--warn` lines | 0 – 299 |
| ⚠️ WARN | at least `--warn`, fewer than `--error` | 300 – 499 |
| 🔴 ERROR | at least `--error`, fewer than `--critical` | 500 – 999 |
| 🟣 CRITICAL | at least `--critical` lines | 1000 and above |

Each threshold is inclusive: a file with exactly 500 lines is ERROR, not
WARN.

### Summary

- `Summary:` shows the number of files listed and how many fall into each
  classification.
- `Total:` is the sum of their line counts.

With `--top`, both lines only count the rows shown, not every file that was
scanned.

### Colours

The output is coloured with ANSI escape codes only when it is written to a
terminal. When it is redirected to a file or a pipe (as in most CI logs),
the output is plain text with the same layout and emoji labels. Standard
output and standard error are checked separately.

To turn colours off in a terminal too, set the
[`NO_COLOR`](https://no-color.org/) environment variable to any non-empty
value:

```
NO_COLOR=1 tingle check_file_size ./src
```

## Examples

Analyse everything under `./src` with the default settings:

```
tingle check_file_size ./src
```

Set the thresholds explicitly (these are the defaults; change the numbers
to suit your project):

```
tingle check_file_size ./src --warn 300 --error 500 --critical 1000
```

Show only the 20 largest files:

```
tingle check_file_size ./src --top 20
```

Skip only `node_modules`, `dist` and `build`. This replaces the default
exclude list:

```
tingle check_file_size ./src --exclude node_modules,dist,build
```

Analyse only Python and JavaScript files:

```
tingle check_file_size ./src --ext .py --ext .js
```

### Using in CI

Fail the build when any file under `./src` reaches the ERROR threshold:

```
tingle check_file_size ./src --fail-on error
```

The report is printed as usual, and the step fails with exit status `2` if
an ERROR or CRITICAL file is found. Combine it with the other options to fit
your project, for example:

```
tingle check_file_size ./src --ext .py --error 400 --fail-on error
```

## Exit status and errors

| Situation | Output | Exit status |
| --- | --- | --- |
| No arguments | Prints the option help | `0` |
| `<path>` does not exist | `Error: path not found: <absolute path>` on **standard error** | `1` |
| Unknown option or invalid value (e.g. `--top abc`, `--fail-on foo`) | A usage error on standard error | `1` |
| No files left to analyse | The header, then `No files found for analysis.` | `0` |
| Analysis completed, no `--fail-on` | The report | `0` |
| Analysis completed, `--fail-on` gate passed | The report | `0` |
| Analysis completed, `--fail-on` gate failed | The report | `2` |

In short:

| Code | Meaning |
| --- | --- |
| `0` | Success, or the size gate passed / was not requested |
| `1` | Runtime or usage error (path not found, unknown option, invalid value) |
| `2` | The size gate failed (`--fail-on`) |

Status `2` means only "the size gate failed", so a CI job can tell large
files apart from a misconfigured command. The report always goes to
standard output and error messages to standard error.

## Quick help

For a short summary of the command, run:

```
tingle --help check_file_size
```
