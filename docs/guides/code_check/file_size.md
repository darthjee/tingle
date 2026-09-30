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
  excluded directories, files ignored by git and binary files (see
  [Skipped files](#skipped-files));
- **a single file**: only that file is analysed.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `--warn N` | `300` | Files with at least `N` lines are marked WARN. |
| `--error N` | `500` | Files with at least `N` lines are marked ERROR. |
| `--critical N` | `1000` | Files with at least `N` lines are marked CRITICAL. |
| `--top N` | `0` | Show only the `N` largest files. `0` shows all files. |
| `--min-level LEVEL` | `ok` | Show only files at `LEVEL` or higher. `LEVEL` is `ok`, `warn`, `error` or `critical`. Display only: the summary and `--fail-on` still count every file. |
| `--exclude LIST` | none | Comma-separated directory names to skip, added to the defaults. |
| `--no-default-excludes` | off | Do not skip the default directories (see below). |
| `--no-gitignore` | off | Do not skip files ignored by git (see below). |
| `--ext EXT` | no filter | Only analyse files with this extension. Can be repeated. |
| `--ignore GLOB` | none | Skip files whose path relative to `<path>` matches this glob. Can be repeated. |
| `--include GLOB` | none | Only analyse files whose path relative to `<path>` matches this glob. Can be repeated. |
| `--fail-on LEVEL` | off | Exit with status `2` if any file is at `LEVEL` or higher. `LEVEL` is `warn`, `error` or `critical`. |
| `--no-config` | off | Do not read `~/.tingle/code_check/config.json` (see [Configuration file](#configuration-file)). |

The defaults above are the built-in ones. Your
[configuration file](#configuration-file) can change them.

### `--exclude`

The default list is:

```
node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,.cache,coverage,.nuxt,out,target
```

These directories are always skipped unless you pass
[`--no-default-excludes`](#--no-default-excludes). Passing `--exclude`
**adds** names to this list:

```
tingle check_file_size . --exclude fixtures
```

skips `fixtures` as well as `node_modules`, `dist`, `build` and the rest.

A file is skipped when **any** part of its path **relative to `<path>`**
matches one of the names. Matching is case-insensitive (`Build` matches
`build`) and covers a whole path component: `build` does not match
`builder`. The directories *above* `<path>` are never checked, so a project
living in `~/work/build/my-app` is scanned normally.

The names are plain directory names, not globs. To skip files by pattern,
use [`--ignore`](#--ignore-and---include).

| Invocation | Excluded names |
| --- | --- |
| `tingle check_file_size .` | The defaults |
| `tingle check_file_size . --exclude fixtures` | The defaults + `fixtures` |
| `tingle check_file_size . --no-default-excludes` | None (`.git/` is walked too) |
| `tingle check_file_size . --no-default-excludes --exclude fixtures` | Only `fixtures` |

`--exclude` is not repeatable: if you pass it more than once, only the last
one counts. Put all the names in a single comma-separated list.

Spaces around each name are trimmed and empty entries are dropped, so
`--exclude ' fixtures, ,tmp'` adds `fixtures` and `tmp`, and `--exclude ''`
adds nothing. A name that is already a default (`--exclude dist`) has no
extra effect and is not an error.

> `--exclude` now **adds** to the default excludes instead of replacing them.
> `--exclude fixtures` now also skips `node_modules`, `dist`, `build`, etc.
> For the old behaviour, use `--no-default-excludes --exclude fixtures`.

### `--no-default-excludes`

Drops the default list, so directories such as `.git/` and `node_modules/`
are walked too. On its own, it skips no directory at all:

```
tingle check_file_size . --no-default-excludes
```

Combine it with `--exclude` to choose exactly which names to skip:

```
tingle check_file_size . --no-default-excludes --exclude node_modules,fixtures
```

`.gitignore` support does not skip `.git/`, because git never lists it as
ignored. If you drop the defaults but still want to leave `.git/` out, add
it back with `--exclude .git`.

### .gitignore and `--no-gitignore`

By default, when `<path>` is inside a git repository, files that git ignores
are skipped, so the report only covers the files that belong to the project.
Git's own rules are used:

- `.gitignore` files, including nested ones in subdirectories;
- the repository's `.git/info/exclude` file;
- your global excludes file (`core.excludesFile`).

Only **untracked** files are skipped. A tracked file is always analysed,
even if it matches an ignore pattern (for example a file added with
`git add -f`), just as git keeps tracking it.

For example, with `*.log` in `.gitignore`, an untracked `debug.log` and a
force-added `keep.log`:

```
tingle check_file_size .
```

skips `debug.log` and analyses `keep.log`. An ignored directory, such as
`tmp/` listed in `.gitignore`, skips every file under it.

To turn this step off and analyse ignored files too, pass `--no-gitignore`:

```
tingle check_file_size . --no-gitignore
```

A few details:

- If `git` is not installed, `<path>` is not inside a git repository, or the
  git call fails for any reason, nothing is skipped by git. No warning is
  shown and the exit status is unchanged.
- When `<path>` is a subdirectory of a repository, rules from `.gitignore`
  files in the parent directories still apply.
- When `<path>` is a single file, it is skipped if git ignores it (see
  [Single-file targets](#single-file-targets)).
- Only the repository that contains `<path>` is consulted. The ignore rules
  of nested repositories and submodules are not used.
- `.git/` itself stays covered by the default excludes.
- This step runs after the directory excludes (the defaults and
  `--exclude`) and before `--ignore`, `--include` and `--ext`. The full
  order is: default excludes, `--exclude`, `.gitignore`, `--ignore`,
  `--include` / `--ext`, then the binary check.

### `--ext`

Limits the analysis to files with the given extension. Repeat the option to
allow more than one:

```
tingle check_file_size ./src --ext .py --ext .js
```

Include the leading dot (`.py`, not `py`). The comparison is
case-insensitive and uses the file's last extension, so `archive.tar.gz`
counts as `.gz`.

### `--ignore` and `--include`

These options filter files by a glob pattern, similar to a `.gitignore`
line:

- `--ignore GLOB` skips every file that matches the glob.
- `--include GLOB` analyses **only** the files that match the glob. Without
  any `--include`, every file is included.

Both can be repeated. A file is skipped if it matches **any** `--ignore`
glob, and kept if it matches **any** `--include` glob.

The glob is matched against the file's path **relative to `<path>`**,
always written with `/` (for example `src/app/main.py` when `<path>` is the
project root). The whole path must match, not just part of it. Matching is
case-insensitive, like `--exclude` and `--ext`, so `*.test.js` also matches
`b.TEST.js`.

> **Quote your globs.** Write `--ignore '*.md'`, not `--ignore *.md`.
> Without quotes, your shell expands the pattern into file names before
> `tingle` sees it.

#### Glob syntax

| Pattern | Matches |
| --- | --- |
| `*` | Any run of characters (possibly none), but never `/`. |
| `?` | Exactly one character other than `/`. |
| `[abc]`, `[a-z]` | One character from the set or range. |
| `[!abc]` | One character *not* in the set. A set never matches `/`. |
| `**` | As a whole path segment (`**/x`, `a/**`, `a/**/b`): zero or more directories. A lone `**` matches everything. Inside a segment (`a**b`) it acts like `*`. |
| `\c` | The literal character `c` (for example `\*` matches a real `*`). |

An unclosed `[` is treated as a literal `[`. Dot-files get no special
treatment: `*` matches `.env`.

#### Where a pattern matches

- **No `/` in the pattern**: it matches in any directory. `*.test.js` is
  the same as `**/*.test.js`, so it matches `a.test.js` and
  `src/deep/b.test.js`.
- **A `/` in the pattern**: it is anchored at `<path>`. `src/*.py` matches
  `src/a.py` but not `lib/src/a.py` or `src/sub/a.py`. A leading `/` only
  marks the anchor: `/src/*.py` is the same as `src/*.py`.
- **A trailing `/`**: it matches everything under that directory.
  `fixtures/` is the same as `**/fixtures/**` (any `fixtures` directory),
  and `src/gen/` is the same as `src/gen/**`.

#### Combining filters

- `--ignore` wins over `--include`: a file that matches both is skipped.
- `--include` and `--ext` must **both** match. For example,
  `--include 'src/**' --ext .py` analyses only `.py` files under `src/`.
- Excluded directories (the defaults plus any `--exclude` names) are still
  skipped, whatever the globs say.

A glob that matches nothing is not an error, and an empty pattern
(`--ignore ''`) is ignored. If the filters leave no files, the command
prints `No files found for analysis.` and exits `0`.

#### Examples

| Command | Effect |
| --- | --- |
| `tingle check_file_size . --ignore '*.test.js'` | Skips `a.test.js` and `src/b.TEST.js`. |
| `tingle check_file_size . --ignore 'docs/**' --ignore '*.md'` | Skips everything under `docs/` and every Markdown file. |
| `tingle check_file_size . --include 'src/**'` | Analyses only files under `src/`. |
| `tingle check_file_size . --include 'src/**' --ext .py` | Analyses only `.py` files under `src/`. |
| `tingle check_file_size . --include 'src/**' --ignore 'src/vendor/'` | Analyses files under `src/`, except those under `src/vendor/`. |

### `--min-level`

Hides the table rows below a given level, so you can focus on the files that
need attention. `LEVEL` is one of `ok`, `warn`, `error` or `critical`
(lowercase). A row is shown when its file is classified at that level **or
higher**, using the order OK < WARN < ERROR < CRITICAL (the same order as
[`--fail-on`](#--fail-on)):

| `--min-level` | Rows shown |
| --- | --- |
| `ok` (default) | Every file |
| `warn` | WARN, ERROR and CRITICAL files |
| `error` | ERROR and CRITICAL files |
| `critical` | CRITICAL files only |

`--min-level ok` is the same as not passing the option.

A few details:

- It only changes **which rows are shown**. The `Summary:` line, the
  `Total:` line and the `--fail-on` gate still count every analysed file.
- It is applied **before** `--top`: `--top N` shows the `N` largest files
  left after `--min-level`. If fewer than `N` files are left, all of them are
  shown.
- The level is based on the thresholds in use, so `--warn`, `--error` and
  `--critical` change which files pass.
- When no file is at or above the level, the table header is not printed.
  A short note is shown instead, followed by the usual summary, and the
  command exits `0` (unless the `--fail-on` gate fails):

  ```
  $ tingle check_file_size ./my-app --min-level warn
  Analyzing: /home/me/projects/my-app
  Thresholds: warn=300 | error=500 | critical=1000

  No files at or above WARN.

  ──────────────────────────────────────────────────────────────────────────────
  Summary: 12 file(s) | 12 OK | 0 WARN | 0 ERROR | 0 CRITICAL
  Total: 1.234 lines
  ```

  If there are no files to analyse at all, the command prints
  `No files found for analysis.` instead, as usual.

| Command | Rows shown |
| --- | --- |
| `tingle check_file_size .` | All rows. |
| `tingle check_file_size . --min-level warn` | WARN, ERROR and CRITICAL rows. |
| `tingle check_file_size . --min-level error --top 5` | The 5 largest ERROR or CRITICAL rows. |
| `tingle check_file_size . --min-level critical --fail-on error` | Only CRITICAL rows. Exits `2` if any file is ERROR or higher, shown or not. |

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

- `--top` and `--min-level` do not hide files from the gate. Every analysed
  file counts, including those not shown in the table.
- If there are no files to analyse (`No files found for analysis.`), the
  command exits `0`.
- The level refers to the thresholds in use, so `--warn`, `--error` and
  `--critical` change what the gate catches.

### Single-file targets

When `<path>` is a single file, the exclude list (the defaults, `--exclude`
and `--no-default-excludes`) is ignored. The other filters
still apply:

- the file is skipped if git ignores it, unless you pass `--no-gitignore`;
- `--ignore` and `--include` globs are matched against the file's **name**
  (for example `main.py`);
- `--ext` is checked against the file's extension.

The file is analysed if it passes these filters and is not detected as
binary. For example, `tingle check_file_size ./main.py --ignore 'main.*'`
leaves nothing to analyse, so it prints `No files found for analysis.` and
exits `0`.

## Configuration file

If you always pass the same options, store them once in a configuration
file instead:

```
~/.tingle/code_check/config.json
```

The file is looked up in your home directory (`$HOME`). Its location cannot
be changed, and there is no per-project configuration file. The file is
optional: if it does not exist, the built-in defaults are used and nothing
is printed about it.

The file holds a JSON object. The options for this command go under the
`check_file_size` key:

```json
{
  "check_file_size": {
    "warn": 200,
    "exclude": ["fixtures"],
    "ignore": ["*.test.js", "*.lock"],
    "fail_on": "error"
  }
}
```

Other top-level keys are ignored: they are reserved for a future `code_check`
tool that will share this file. If the file exists but has no
`check_file_size` key, the built-in defaults are used, as if the file did
not exist.

### Keys

Every key is optional and matches a command-line option:

| Key | Type | Option |
| --- | --- | --- |
| `warn` | integer >= 0 | `--warn` |
| `error` | integer >= 0 | `--error` |
| `critical` | integer >= 0 | `--critical` |
| `top` | integer >= 0 | `--top` |
| `exclude` | list of strings | `--exclude` (comma-separated on the command line) |
| `ignore` | list of strings | `--ignore` |
| `include` | list of strings | `--include` |
| `ext` | list of strings | `--ext` |
| `no_default_excludes` | `true` or `false` (default `false`) | `--no-default-excludes` |
| `gitignore` | `true` or `false` (default `true`) | `--no-gitignore` (inverted: `"gitignore": false` is the same as `--no-gitignore`) |
| `fail_on` | `"warn"`, `"error"`, `"critical"` or `null` | `--fail-on` (`null` means no gate) |
| `min_level` | `"ok"`, `"warn"`, `"error"` or `"critical"` | `--min-level` |

Notes:

- Integers must be real JSON numbers: `"top": true` or `"top": "20"` are
  errors.
- In lists, write each item as its own string: `"exclude": ["fixtures",
  "tmp"]`, not `"fixtures,tmp"`. An empty list is valid and adds nothing.
- The path to analyse is not a config key: you always give it on the
  command line. A `path` key is reported as an unknown key.

### How the config and the command line combine

- **Single values** (`warn`, `error`, `critical`, `top`, `fail_on`,
  `min_level`): the command line wins over the config, which wins over the
  built-in default.
- **Lists** (`exclude`, `ignore`, `include`, `ext`): the config values come
  first, then the command-line values are **added**. Duplicates are dropped.
- **`no_default_excludes` and `gitignore`**: the config can set either
  value. `--no-default-excludes` and `--no-gitignore` can only turn the
  behaviour off, and they win over the config.

With the example config above:

| Command | Result |
| --- | --- |
| `tingle check_file_size .` | `warn=200`, the default excludes plus `fixtures`, skips `*.test.js` and `*.lock`, fails on ERROR. |
| `tingle check_file_size . --warn 400` | `warn=400`: the command line wins. |
| `tingle check_file_size . --ignore '*.spec.js'` | Skips `*.test.js`, `*.lock` **and** `*.spec.js`: both lists apply. |
| `tingle check_file_size . --fail-on critical` | Fails on CRITICAL only. |

When a `check_file_size` section was loaded, even an empty one, the header
shows the file in use (see [Header](#header)).

### Running without the config: `--no-config`

Some config values cannot be undone from the command line. For example,
there is no option to turn the gate off when the config sets `fail_on`, or
to turn `.gitignore` back on when it sets `"gitignore": false`. Pass
`--no-config` to ignore the file completely:

```
tingle check_file_size . --no-config
```

With `--no-config`, the file is not read or checked at all (even an invalid
one), and only the built-in defaults and the options you pass are used.

### Config errors

The file is checked every time it is read, even when you pass every option
on the command line. If something is wrong, the command prints one error line
on standard error and exits with status `1`, before printing any report:

```
Error: /home/me/.tingle/code_check/config.json: <reason>
```

Typical reasons:

- the file is not valid JSON, or cannot be read;
- the top level, or the `check_file_size` section, is not a JSON object;
- an unknown key, such as a typo: `unknown key 'wran'`;
- a wrong type or value, for example `'top' must be an integer >= 0` or
  `'fail_on' must be one of warn, error, critical or null`.

Fix the file, or run with `--no-config` in the meantime.

The config is never read when you run `tingle check_file_size` with no
arguments: the help is printed as usual.

## Skipped files

Besides the excluded directories (the defaults plus any `--exclude` names),
the untracked files ignored by git (see
[.gitignore and `--no-gitignore`](#gitignore-and---no-gitignore)) and the
files filtered out by `--ext`, `--ignore` and `--include`, binary files are
skipped automatically. A file counts as binary when:

- its extension is a known binary type: images (`.png`, `.jpg`, `.svg`,
  ...), video and audio (`.mp4`, `.mp3`, ...), office documents and PDFs
  (`.pdf`, `.docx`, ...), archives (`.zip`, `.tar`, `.gz`, ...), compiled
  code and libraries (`.exe`, `.so`, `.pyc`, `.class`, `.jar`, `.wasm`,
  ...), fonts (`.ttf`, `.woff2`, ...), databases (`.db`, `.sqlite`, ...),
  and a few others such as `.lock`, `.map` and minified assets (`.min.js`,
  `.min.css`); or
- its first 1024 bytes contain a NUL byte or are not valid UTF-8; or
- it cannot be read (for example, because of permissions).

Hidden directories that are not excluded (for example `.pytest_cache`) are
scanned like any other directory.

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
- `Thresholds:` shows the `warn`, `error` and `critical` values in use,
  after applying the config file and the command-line options.
- `Config:` (dimmed) shows the path of the
  [configuration file](#configuration-file), right after the `Thresholds:`
  line. It only appears when the file has a `check_file_size` section (even
  an empty one), and never with `--no-config`:

  ```
  Analyzing: /home/me/projects/my-app
  Thresholds: warn=200 | error=500 | critical=1000
  Config: /home/me/.tingle/code_check/config.json
  ```

### Table

- One row per file, with the **Status**, **Lines** and **File** columns.
- Rows are sorted by line count, largest first. `--min-level` hides the rows
  below the given level, then `--top N` keeps the `N` largest of the rows
  left.
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

The order of the thresholds is not checked, on the command line or in the
config file. Keep `warn` < `error` < `critical`, or the labels will not make
sense.

### Summary

- `Summary:` shows the number of files analysed and how many fall into each
  classification.
- `Total:` is the sum of their line counts.

Both lines always count every analysed file, even when `--top` or
`--min-level` hide some rows from the table.

> Before `--min-level` was added, `--top` also cut the summary and total
> down to the rows shown. Now they always cover every analysed file.

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

Show only the files at WARN or higher:

```
tingle check_file_size ./src --min-level warn
```

Show the 5 largest ERROR or CRITICAL files:

```
tingle check_file_size ./src --min-level error --top 5
```

Also skip `fixtures` directories, on top of the default exclude list:

```
tingle check_file_size ./src --exclude fixtures
```

Skip only `fixtures`, scanning `node_modules`, `.git` and the other default
directories too:

```
tingle check_file_size ./src --no-default-excludes --exclude fixtures
```

Also analyse files that git ignores (build output, local data, ...):

```
tingle check_file_size . --no-gitignore
```

Analyse only Python and JavaScript files:

```
tingle check_file_size ./src --ext .py --ext .js
```

Skip test files and everything under `docs/`:

```
tingle check_file_size . --ignore '*.test.js' --ignore 'docs/**'
```

Analyse only the code under `src/`, leaving out the vendored copy in
`src/vendor/`:

```
tingle check_file_size . --include 'src/**' --ignore 'src/vendor/'
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

To keep CI logs short, list only the files that fail the gate. The gate still
checks every file:

```
tingle check_file_size ./src --min-level error --fail-on error
```

If your personal [configuration file](#configuration-file) sets options,
they apply on any machine where that file exists. Pass `--no-config` to make a CI step depend only on its
own options:

```
tingle check_file_size ./src --no-config --fail-on error
```

## Exit status and errors

| Situation | Output | Exit status |
| --- | --- | --- |
| No arguments | Prints the option help | `0` |
| `<path>` does not exist | `Error: path not found: <absolute path>` on **standard error** | `1` |
| Unknown option or invalid value (e.g. `--top abc`, `--fail-on foo`, `--min-level foo`) | A usage error on standard error | `1` |
| Invalid config file (bad JSON, unknown key, wrong type, ...) | `Error: <config path>: <reason>` on **standard error** (see [Config errors](#config-errors)) | `1` |
| No files left to analyse | The header, then `No files found for analysis.` | `0` |
| Analysis completed, no `--fail-on` | The report | `0` |
| Analysis completed, `--fail-on` gate passed | The report | `0` |
| Analysis completed, `--fail-on` gate failed | The report | `2` |

In short:

| Code | Meaning |
| --- | --- |
| `0` | Success, or the size gate passed / was not requested |
| `1` | Runtime or usage error (path not found, unknown option, invalid value, invalid config file) |
| `2` | The size gate failed (`--fail-on`) |

Status `2` means only "the size gate failed", so a CI job can tell large
files apart from a misconfigured command. The report always goes to
standard output and error messages to standard error.

## Quick help

For a short summary of the command, run:

```
tingle --help check_file_size
```
