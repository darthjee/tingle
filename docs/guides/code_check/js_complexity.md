# `tingle code_check js_complexity`

JavaScript/TypeScript code complexity via FTA (Docker).

This is a subcommand of [`tingle code_check`](../code_check.md).

## What it does

`tingle code_check js_complexity` finds the JavaScript and TypeScript files
that are the hardest to read and maintain, so you know where to refactor
first.

It selects the JavaScript/TypeScript files under a file or directory on your
machine, then runs [FTA](https://ftaproject.dev/) (Fast TypeScript Analyzer)
on them inside the `darthjee/tingle_js_complexity` Docker image. FTA gives
each file a score that combines its cyclomatic complexity, its size and its
Halstead metrics. The higher the score, the harder the file is to maintain.

Each file gets one row in a report, labelled OK, WARN, ERROR or CRITICAL.
The label comes from the file's **FTA score** compared with thresholds you
can choose. The other columns (cyclomatic complexity, lines and FTA's own
assessment) are shown for information only: they never change the label or
the exit status.

## Requirements

- **Docker**, with the `docker` command on your `PATH` and a running daemon.
  You do not need Node.js on your machine: FTA runs inside the image.
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
The image copies the selected files into its own temporary folder before
analysing them, so a very large selection needs as much temporary space
inside the container.

## Usage

```
tingle code_check js_complexity <path> [options]
```

`<path>` can be:

- **a directory**: every JavaScript/TypeScript file below it is analysed,
  recursively, except for the files left out by the selection rules (see
  [File selection](#file-selection)). The directory is mounted into the
  container;
- **a single file**: only that file is analysed. If it is a symlink, it is
  resolved first, and its target's parent directory is mounted into the
  container; otherwise its own parent directory is. A file without a
  supported extension, a declaration file (`.d.ts`, ...), or a file left out
  by the selection options leaves nothing to analyse (see
  [Single-file targets](#single-file-targets)).

The file list is sent to the container on its standard input, so there is no
limit on the number of files, and the run has no timeout.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `--warn N` | `50` | Files with an FTA score of at least `N` are marked WARN. |
| `--error N` | `60` | Files with an FTA score of at least `N` are marked ERROR. |
| `--critical N` | `75` | Files with an FTA score of at least `N` are marked CRITICAL. |
| `--top N` | `0` | Show only the `N` most complex files. `0` shows all files. |
| `--min-level LEVEL` | `ok` | Show only files at `LEVEL` or higher. `LEVEL` is `ok`, `warn`, `error` or `critical`. |
| `--fail-on LEVEL` | off | Exit with status `2` if any file is at `LEVEL` or higher. `LEVEL` is `warn`, `error` or `critical`. |
| `--image IMAGE` | `darthjee/tingle_js_complexity:<tingle version>` | Docker image to run. |
| `--exclude a,b` | none | Extra directory names to skip (comma-separated), **added** to the [default excludes](#--exclude). |
| `--no-default-excludes` | off | Do not skip the default directories; only `--exclude` names apply. |
| `--no-gitignore` | off | Do not skip files ignored by git (`.gitignore`, `.git/info/exclude`, global excludes). |
| `--ignore GLOB` | none | Skip files whose path relative to `<path>` matches `GLOB`. Can be repeated. |
| `--include GLOB` | all | Only analyse JavaScript/TypeScript files whose path relative to `<path>` matches `GLOB`. Can be repeated. |

The thresholds accept decimals (`--warn 52.5`) and must be `0` or more.
`--top` must be a whole number, `0` or more, and `--image` must not be
empty. The order of the thresholds is not checked: keep `warn` < `error` <
`critical`, or the labels will not make sense.

The file selection options are described in
[File selection](#file-selection). There is no option to change the analysed
extensions (no `--ext`).

### `--min-level` and `--top`

These options only change **which level rows are shown**:

- `--min-level LEVEL` keeps the rows at `LEVEL` or higher, using the order
  OK < WARN < ERROR < CRITICAL;
- then `--top N` (when `N` is more than `0`) keeps the `N` most complex rows
  left.

`⛔ PARSE` rows (files FTA could not parse) are **always shown**, below the
level rows, and are not counted by `--top`.

When no row at all is left to show, the table is replaced by a short note,
followed by the usual summary:

```
No files at or above WARN.
```

The `Summary:` and `FTA score:` lines and the `--fail-on` gate always count
every selected file, shown or not.

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
- If there are no JavaScript/TypeScript files to analyse, the command exits
  `0`.

### `--image`

By default the image is `darthjee/tingle_js_complexity:<tingle version>`,
where the version is read from tingle's own `shell/linux/VERSION` file, so
each tingle release uses the matching image. `--image` runs another image
instead, for example one you built locally:

```
tingle code_check js_complexity ./src --image tingle_js_complexity:dev
```

The image is pulled only when it is not present locally. If tingle cannot
read its version file and you did not pass `--image`, the command fails and
suggests `--image`:

```
Error: cannot read the tingle version from /path/to/tingle/shell/linux/VERSION; use --image to choose the image
```

## File selection

The files to analyse are chosen on your machine, before Docker is called.
Only the selected files are sent to the container. The options work as in
[`tingle code_check rubycritic`](rubycritic.md#file-selection), except that
the extension list is the JavaScript/TypeScript one and declaration files are
always skipped. There is no `--ext` and no binary check.

### Extensions

A file is analysed when its name ends in one of these extensions, in any
case (`UPPER.JS` counts):

```
.js .mjs .cjs .jsx .ts .mts .cts .tsx
```

TypeScript **declaration files** (`.d.ts`, `.d.mts`, `.d.cts`, in any case)
hold only types, so they are always skipped, even with
`--no-default-excludes` or a matching `--include`. Other files, such as
`.vue`, `.svelte` or `.json`, are not analysed.

### `--exclude`

The default list is:

```
node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,.cache,coverage,.nuxt,out,target,.turbo,.svelte-kit,.output,.vercel,.parcel-cache,storybook-static
```

That is the [`file_size`](file_size.md#--exclude) default list plus
`.turbo`, `.svelte-kit`, `.output`, `.vercel`, `.parcel-cache` and
`storybook-static`, the output folders of common JavaScript tools. These
directories are always skipped unless you pass
[`--no-default-excludes`](#--no-default-excludes). Passing `--exclude`
**adds** names to this list:

```
tingle code_check js_complexity . --exclude test,fixtures
```

skips `test` and `fixtures` as well as `node_modules`, `dist` and the rest.

A file is skipped when **any** part of its path **relative to `<path>`**
matches one of the names. Matching is case-insensitive (`Test` matches
`test`) and covers a whole path component: `build` does not match `builder`.
The directories *above* `<path>` are never checked, so a project living in
`~/work/build/my-app` is analysed normally.

The names are plain directory names, not globs. To skip files by pattern,
use [`--ignore`](#--ignore-and---include).

| Invocation | Excluded names |
| --- | --- |
| `tingle code_check js_complexity .` | The defaults |
| `tingle code_check js_complexity . --exclude test` | The defaults + `test` |
| `tingle code_check js_complexity . --no-default-excludes` | None (`node_modules/`, `dist/` and `.git/` are walked too) |
| `tingle code_check js_complexity . --no-default-excludes --exclude test` | Only `test` |

`--exclude` is not repeatable: if you pass it more than once, only the last
one counts. Put all the names in a single comma-separated list.

Spaces around each name are trimmed and empty entries are dropped, so
`--exclude ' test, ,fixtures'` adds `test` and `fixtures`, and `--exclude ''`
adds nothing. A name that is already a default (`--exclude dist`) has no
extra effect and is not an error.

### `--no-default-excludes`

Drops the default list, so directories such as `node_modules/`, `dist/` and
`.git/` are walked too. On its own, it skips no directory at all:

```
tingle code_check js_complexity . --no-default-excludes
```

Combine it with `--exclude` to choose exactly which names to skip:

```
tingle code_check js_complexity . --no-default-excludes --exclude .git,node_modules
```

Declaration files stay skipped: `--no-default-excludes` only affects the
directory names.

`.gitignore` support does not skip `.git/`, because git never lists it as
ignored. If you drop the defaults but still want to leave `.git/` out, add
it back with `--exclude .git`.

### .gitignore and `--no-gitignore`

By default, when `<path>` (or, for a single file, its parent directory) is
inside a git repository, files that git ignores are skipped, so the report
only covers the files that belong to the project. Git's own rules are used:

- `.gitignore` files, including nested ones in subdirectories;
- the repository's `.git/info/exclude` file;
- your global excludes file (`core.excludesFile`).

Only **untracked** files are skipped. A tracked file is always analysed,
even if it matches an ignore pattern (for example a file added with
`git add -f`), just as git keeps tracking it. An ignored directory skips
every file under it. This is a convenient way to leave out generated code
and build output that your project already ignores.

To turn this step off and analyse ignored files too, pass `--no-gitignore`:

```
tingle code_check js_complexity . --no-gitignore
```

A few details:

- If `git` is not installed, `<path>` is not inside a git repository, or the
  git call fails for any reason, nothing is skipped by git. No warning is
  shown and the exit status is unchanged.
- When `<path>` is a subdirectory of a repository, rules from `.gitignore`
  files in the parent directories still apply.
- Only the repository that contains `<path>` is consulted. The ignore rules
  of nested repositories and submodules are not used.
- Git runs on your machine, not in the container: the
  `darthjee/tingle_js_complexity` image has no git, and does not need it.

### `--ignore` and `--include`

These options filter files by a glob pattern, similar to a `.gitignore`
line:

- `--ignore GLOB` skips every file that matches the glob.
- `--include GLOB` analyses **only** the JavaScript/TypeScript files that
  match the glob. Without any `--include`, every JavaScript/TypeScript file
  is included.

Both can be repeated. A file is skipped if it matches **any** `--ignore`
glob, and kept if it matches **any** `--include` glob.

The glob is matched against the file's path **relative to `<path>`**,
always written with `/` (for example `src/app.ts` when `<path>` is the
project root). The whole path must match, not just part of it. Matching is
case-insensitive, so `*.test.ts` also matches `app.TEST.ts`.

> **Quote your globs.** Write `--ignore '**/*.test.ts'`, not
> `--ignore **/*.test.ts`. Without quotes, your shell may expand the
> pattern into file names before `tingle` sees it.

The glob syntax is the same as for `file_size` (see
[Glob syntax](file_size.md#glob-syntax) and
[Where a pattern matches](file_size.md#where-a-pattern-matches)). In short:

- `*` matches within one path segment, `**` spans directories;
- a pattern with no `/` matches in any directory (`*.test.ts` is the same as
  `**/*.test.ts`);
- a pattern with a `/` is anchored at `<path>`, and a leading `/` only marks
  the anchor (`/src/*.ts` is the same as `src/*.ts`);
- a trailing `/` matches everything under that directory (`generated/` is
  the same as `**/generated/**`).

Combining filters:

- `--ignore` wins over `--include`: a file that matches both is skipped.
- `--include` and the extension list must **both** match:
  `--include '*.json'` leaves nothing to analyse.
- `--include` never brings back a declaration file.
- Excluded directories (the defaults plus any `--exclude` names) are always
  skipped, whatever the globs say.

A glob that matches nothing is not an error, and an empty pattern
(`--ignore ''`) is ignored.

| Command | Effect |
| --- | --- |
| `tingle code_check js_complexity . --ignore '**/*.test.ts'` | Skips every `.test.ts` file, in any directory. |
| `tingle code_check js_complexity . --ignore '**/*.test.ts' --ignore '**/*.spec.js'` | Skips the `.test.ts` and `.spec.js` files. |
| `tingle code_check js_complexity . --ignore '*.generated.ts'` | Skips generated files such as `api.generated.ts`. |
| `tingle code_check js_complexity . --include 'src/**'` | Analyses only the files under `src/`. |
| `tingle code_check js_complexity . --include 'src/**' --ignore 'src/legacy/'` | Analyses the files under `src/`, except those under `src/legacy/`. |

### Filter order

For a directory `<path>`, every file found below it goes through these
steps, in order. The first step that rejects a file drops it:

1. the default excludes (skipped with `--no-default-excludes`);
2. the `--exclude` names;
3. `.gitignore` (skipped with `--no-gitignore`);
4. the `--ignore` globs;
5. the `--include` globs (when given) **and** the
   [extension list](#extensions), in any case;
6. declaration files (`.d.ts`, `.d.mts`, `.d.cts`), always;
7. the symlink rule (see [Symlinks](#symlinks)).

A file dropped by any of these steps is not counted anywhere and no message
is printed.

### Single-file targets

When `<path>` is a single file, the exclude list (the defaults, `--exclude`
and `--no-default-excludes`) is ignored. The other filters still apply:

- the file is skipped if git ignores it, unless you pass `--no-gitignore`;
- `--ignore` and `--include` globs are matched against the file's **name**
  (for example `app.ts`);
- the file must have a supported extension and must not be a declaration
  file.

If `<path>` is a symlink, it is resolved first: its target's parent
directory is mounted, and the target's name is the one shown and matched.

For example, this leaves nothing to analyse, so it prints
`No JavaScript/TypeScript files found for analysis.` and exits `0`:

```
tingle code_check js_complexity ./src/app.test.ts --ignore '*.test.ts'
```

### Symlinks

The container only sees the folder that is mounted (`<path>` for a
directory), read-only, so every file sent to it must be a real file inside
that folder:

- **Directory symlinks are not followed**: the files behind a symlinked
  directory are not analysed.
- A file symlink pointing **outside** `<path>`, or whose target does not
  exist (a dangling symlink), is skipped silently.
- A file symlink pointing **inside** `<path>` is analysed as its target: the
  `File` column shows the target's path. If the target is selected too, the
  file is counted only once.
- Absolute symlinks that point inside `<path>` work too: they are sent as
  the target's path inside the mounted folder.

### Unusual file names

Spaces, tabs and unicode in file names are fine. File names are sent to the
container one per line, as UTF-8, so a file whose name contains a newline,
or whose name is not valid UTF-8, cannot be sent: it is skipped with a
warning on standard error and not counted anywhere:

```
Warning: skipping file with a newline in its name: 'src/odd\nname.js'
Warning: skipping file whose name is not valid UTF-8: 'src/caf\udce9.js'
```

### Nothing to analyse

There is no binary check: a file with a supported extension that is not
valid UTF-8 is still sent to FTA, and shows up as a `⛔ PARSE` row.

If no file is left (none exist, or the rules leave none), the command prints
the header and `No JavaScript/TypeScript files found for analysis.`, then
exits `0` without calling Docker at all.

## Thresholds and levels

The level of a file comes from its FTA score **rounded to one decimal**, the
same value shown in the `FTA` column. A raw score of `59.96` is shown as
`60.0` and is ERROR with the default thresholds.

| Status | Rule | Default range |
| --- | --- | --- |
| ✅ OK | score below `--warn` | below 50 |
| ⚠️ WARN | at least `--warn`, below `--error` | 50 to below 60 |
| 🔴 ERROR | at least `--error`, below `--critical` | 60 to below 75 |
| 🟣 CRITICAL | at least `--critical` | 75 and above |
| ⛔ PARSE | FTA could not parse the file | - |

Each threshold is inclusive: a file with a score of exactly `60.0` is ERROR,
not WARN.

The defaults follow FTA's own assessment bands: above 50 FTA says
"Could be better", and above 60 "Needs improvement". The `critical=75`
level is tingle's own, for the files that most need attention. FTA scores
are not capped at 100: a very large file can score above it, and is simply
CRITICAL.

## Reading the output

Sample run against a small project, with the default thresholds:

```
$ tingle code_check js_complexity fixture
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

In this project, the files under `build/` are skipped (a default exclude)
and `ext/types.d.ts` is skipped (a declaration file). Before the report, a
warning for each of `broken.js` and `latin1.js` is printed on standard error
(see [Parse warnings](#parse-warnings)).

### Header

- `Analyzing:` shows the target as an absolute path.
- `Thresholds:` shows the `warn`, `error` and `critical` values in use.
- `Image:` shows the Docker image that runs FTA.

### Columns

| Column | Meaning |
| --- | --- |
| `Status` | The level of the file (see [Thresholds and levels](#thresholds-and-levels)). |
| `FTA` | The file's FTA score, rounded to one decimal. This is the value compared with the thresholds. |
| `Cyclo` | The file's cyclomatic complexity, as reported by FTA. Information only. |
| `Lines` | The file's number of code lines, as counted by FTA. Information only. |
| `Assessment` | FTA's own verdict: `OK`, `Could be better` or `Needs improvement`. Information only. |
| `File` | For a directory target, the path relative to the target's parent directory, so it starts with the directory's name (`fixture/...` above). For a single-file target, only the file name. |

### Sort order

Level rows come first, sorted by FTA score, highest first; files with the
same score are sorted by path. The `⛔ PARSE` rows follow, sorted by path.

### Files shown as `OK 0.0`

FTA leaves out the files that have no code line: empty files, and files with
only blank lines or comments. Such a file is still listed, as `✅ OK` with a
score of `0.0` and `-` in the other columns, so the file count matches the
selection (`fixture/empty.js` above).

In rare cases the image also refuses a file it was given, for example one
deleted between the selection and the run. It prints a warning on standard
error, and the file is listed the same way, as `✅ OK` with `0.0`:

```
Warning: the image skipped src/gone.js: not a regular file under /src
```

### Parse warnings

Each file FTA cannot parse (a syntax error, or a file that is not valid
UTF-8) prints a warning on standard error, before the report:

```
Warning: cannot parse fixture/broken.js: <message>
```

It appears as a `⛔ PARSE` row, with `-` in every value column, and in the
`skipped (parse error)` count. It is never in the level counts or the FTA
score line, and it never changes the exit status.

### Summary

- `Summary:` shows the number of selected files (`⛔ PARSE` files included)
  and how many fall into each level. Files shown as `OK 0.0` count as OK.
  When some files could not be parsed, `| k skipped (parse error)` is added
  at the end.
- `FTA score:` shows the average and the maximum score of the level rows,
  with 2 decimals (`OK 0.0` files count with `0.0`, `⛔ PARSE` files are left
  out). FTA has no project-wide score: tingle computes both. When every file
  failed to parse, it shows `FTA score: n/a`.

Both lines always cover every selected file, even when `--top` or
`--min-level` hide some rows.

### Colours

The output is coloured with ANSI escape codes only when it is written to a
terminal. When it is redirected to a file or a pipe (as in most CI logs), it
is plain text with the same layout and emoji labels. Standard output and
standard error are checked separately.

To turn colours off in a terminal too, set the
[`NO_COLOR`](https://no-color.org/) environment variable to any non-empty
value:

```
NO_COLOR=1 tingle code_check js_complexity ./src
```

## Examples

Analyse every JavaScript/TypeScript file under `./src` with the default
settings:

```
tingle code_check js_complexity ./src
```

Use stricter thresholds:

```
tingle code_check js_complexity ./src --warn 40 --error 50 --critical 60
```

Show only the 10 most complex files at WARN or higher:

```
tingle code_check js_complexity ./src --top 10 --min-level warn
```

Analyse a single file:

```
tingle code_check js_complexity ./src/app.ts
```

Skip test and fixture directories as well as the defaults:

```
tingle code_check js_complexity . --exclude test,fixtures
```

Skip test and spec files, wherever they are:

```
tingle code_check js_complexity . --ignore '**/*.test.ts' --ignore '**/*.spec.js'
```

Analyse only the files under `src/`:

```
tingle code_check js_complexity . --include 'src/**'
```

Analyse the files git ignores too:

```
tingle code_check js_complexity . --no-gitignore
```

Run a locally built image:

```
tingle code_check js_complexity ./src --image tingle_js_complexity:dev
```

### Using in CI

Fail the build when any file under `./src` reaches the ERROR threshold:

```
tingle code_check js_complexity ./src --fail-on error
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
| Empty `--image` | `Error: --image must not be empty` | `1` |
| `<path>` does not exist | `Error: path not found: <absolute path>` | `1` |
| `<path>` cannot be read | `Error: path not readable: <absolute path>` | `1` |
| The folder to mount contains `:` | `Error: cannot mount <folder>: Docker volume paths cannot contain ':'` | `1` |
| Tingle version unreadable and no `--image` | `Error: cannot read the tingle version from <file>; use --image to choose the image` | `1` |
| No JavaScript/TypeScript files to analyse | The header, then `No JavaScript/TypeScript files found for analysis.` | `0` |
| `docker` not on `PATH` | `Error: docker not found on PATH; tingle code_check js_complexity needs Docker to run FTA` | `1` |
| Docker daemon not running (`docker info` failed or took over 30 seconds) | `Error: the Docker daemon is not responding (docker info failed); start Docker and retry` | `1` |
| Image pull failed | `Pulling <image> ...` and Docker's output, then `Error: could not pull image <image>` | `1` |
| `docker run` could not be started | `Error: could not run docker: <reason>` | `1` |
| Folder not shared with Docker Desktop | Docker's error, then `Error: Docker could not mount <folder>; on Docker Desktop, share it (or a parent folder) under Settings > Resources > File sharing, then retry` | `1` |
| FTA or the container failed | The container's error output, then `Error: FTA failed in <image> (exit <status>)` | `1` |
| Unexpected output from the container | The container's error output, then `Error: could not parse the output of <image>: <reason>` | `1` |
| Analysis completed, no `--fail-on` | The report | `0` |
| Analysis completed, `--fail-on` gate passed | The report | `0` |
| Analysis completed, `--fail-on` gate failed | The report | `2` |

In short:

| Code | Meaning |
| --- | --- |
| `0` | Success, nothing to analyse, or the complexity gate passed / was not requested |
| `1` | Usage error, path problem, or Docker / FTA failure |
| `2` | The complexity gate failed (`--fail-on`) |

Unparsable files (`⛔ PARSE` rows) and files shown as `OK 0.0` never change
the exit status on their own. The report always goes to standard output and
error messages to standard error.

## Limitations

- **Podman is not supported.** It may work when aliased as `docker`, but
  this is not tested.
- **No Docker-in-Docker.** The `darthjee/tingle` container (used by
  [`tingle linux`](../linux.md)) has no `docker` command, so running this
  subcommand inside it fails with `docker not found on PATH`. Run it on a
  host with Docker.
- **Minified bundles are analysed.** A minified bundle (`app.min.js`, or
  one without `.min` in its name) usually gets a very high score and shows
  up as CRITICAL. Bundles under a default-excluded directory such as
  `dist/` or `build/`, or ignored by git, are already skipped; for the
  others, use `--ignore` (for example `--ignore '*.min.js'`). A default
  skip for `*.min.js` bundles is planned (#323).
- **Generated code is analysed** unless it is skipped by the selection
  rules. Keep it out with `.gitignore`, `--exclude` or `--ignore` (for
  example `--ignore '*.generated.ts'`).
- **No configuration file section yet.** The options, including the file
  selection options, must be given on the command line;
  `~/.tingle/code_check/config.json` is not read by this subcommand.

## Quick help

For a short summary of the command's options, run:

```
tingle code_check js_complexity --help
```

`tingle --help code_check` shows the options of every `code_check`
subcommand, together with their list. Its `js_complexity` part groups the
options as **File selection** (`--exclude`, `--no-default-excludes`,
`--no-gitignore`, `--ignore`, `--include`), **Thresholds** (`--warn`,
`--error`, `--critical`), **Display** (`--top`, `--min-level`), **CI gate**
(`--fail-on`) and **Image** (`--image`), followed by the exit codes and a
few examples.
