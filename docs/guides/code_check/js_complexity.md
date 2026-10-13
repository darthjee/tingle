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
The same image also runs [jscpd](https://github.com/kucherenko/jscpd) to
find copy-pasted code between the selected files, and
[typhonjs-escomplex](https://github.com/typhonjs-node-escomplex/typhonjs-escomplex)
to measure each function, so you can drill down from a file to the
functions that make it complex (see [`--details`](#--details)).

Each file gets one row in a report, labelled OK, WARN, ERROR or CRITICAL.
The label comes from the file's **FTA score** compared with thresholds you
can choose. The other columns (cyclomatic complexity, lines, duplicated
lines and FTA's own assessment) and the per-function lines are shown for
information only: they never change the label or the exit status.

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
  supported extension, a declaration file (`.d.ts`, ...), a minified bundle
  (`.min.js`, ...) without `--no-default-excludes`, or a file left out by the
  selection options leaves nothing to analyse (see
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
| `--details [N]` | off | Under each shown file, list its `N` most complex functions. `--details` alone means `5`; `0` lists every function. |
| `--image IMAGE` | `darthjee/tingle_js_complexity:<tingle version>` | Docker image to run. |
| `--exclude a,b` | none | Extra directory names to skip (comma-separated), **added** to the [default excludes](#--exclude). |
| `--no-default-excludes` | off | Do not skip the default directories or minified bundles; only `--exclude` names apply. |
| `--no-gitignore` | off | Do not skip files ignored by git (`.gitignore`, `.git/info/exclude`, global excludes). |
| `--ignore GLOB` | none | Skip files whose path relative to `<path>` matches `GLOB`. Can be repeated. |
| `--include GLOB` | all | Only analyse JavaScript/TypeScript files whose path relative to `<path>` matches `GLOB`. Can be repeated. |
| `--no-config` | off | Do not read `~/.tingle/code_check/config.json` (see [Configuration file](#configuration-file)). |

The thresholds accept decimals (`--warn 52.5`) and must be `0` or more.
`--top` and `--details N` must be whole numbers, `0` or more, and `--image`
must not be empty. The order of the thresholds is not checked: keep `warn` < `error` <
`critical`, or the labels will not make sense.

The file selection options are described in
[File selection](#file-selection). There is no option to change the analysed
extensions (no `--ext`).

The defaults in this table are the built-in ones. Every option except
`--no-config` can also be set in the
[configuration file](#configuration-file); an option given on the command
line wins over it.

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

### `--details`

Drills down from a file to the functions that make it complex. Under each
shown file row, the command lists the file's most complex functions, each
with its own cyclomatic complexity, its length, its name and where it starts:

```
$ tingle code_check js_complexity fixture --details 2
...
Status             FTA  Cyclo  Lines    Dup  Assessment         File
──────────────── ─────  ─────  ─────  ─────  ─────────────────  ──────────────────────────────────────────────────
🔴 ERROR           71.3    136    245      0  Needs improvement  fixture/complex.ts
                 cyclo  12  sloc   27  reducer  (fixture/complex.ts:9)
                 cyclo   9  sloc   11  score  (fixture/complex.ts:74)
✅ OK              37.4      3     18      0  OK                 fixture/component.tsx
                 cyclo   3  sloc   13  List  (fixture/component.tsx:8)
                 cyclo   1  sloc    1  <anon method-1>  (fixture/component.tsx:12)
...
```

- `--details` without a number shows up to **5** functions per file;
  `--details N` shows up to `N`; `--details 0` shows **every** function.
- Without `--details`, no function lines are printed.
- Functions are sorted by cyclomatic complexity, highest first, then by
  line, then by name. A file with fewer functions shows only those it has; a
  file with no function at all (for example one with only constants or
  imports) gets no function lines.
- Only the **shown** rows get function lines: `--min-level` and `--top` pick
  the files first, then `--details` adds lines under each of them. `⛔ PARSE`
  rows never get function lines.
- Functions have **no level**: they are not labelled OK/WARN/ERROR/CRITICAL,
  are not counted in the `Summary:` line, and never affect `--fail-on` or
  the exit status. The level and the gate stay based on each file's FTA
  score.

The function data comes from escomplex, not from FTA. When it is missing for
a file, the row gets a short note instead of function lines (see
[Function lines](#function-lines)); this is never an error.

### `--image`

By default the image is `darthjee/tingle_js_complexity:<tingle version>`,
where the version is read from tingle's own `shell/linux/VERSION` file, so
each tingle release uses the matching image. `--image` runs another image
instead, for example one you built locally:

```
tingle code_check js_complexity ./src --image tingle_js_complexity:dev
```

The image is pulled only when it is not present locally. If tingle cannot
read its version file (and you did not pass `--image` or set `image` in the
[configuration file](#configuration-file)), the command fails and suggests
`--image`:

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

**Minified bundles** (names ending in `.min.js`, `.min.mjs` or `.min.cjs`, in
any case, such as `app.min.js` or `VENDOR.MIN.JS`) are skipped by default,
silently. Minified code always gets a very high score, so it would only
crowd the report with CRITICAL rows nobody will refactor. To analyse them,
pass [`--no-default-excludes`](#--no-default-excludes) (or set
`"no_default_excludes": true` in the
[configuration file](#configuration-file)); there is no separate option for
this. `--include` does **not** bring them back: `--include '**/*.min.js'` on
its own leaves nothing to analyse.

Only the `.min` suffix counts:

- `app.min.ts` is not a minified bundle, so it is analysed;
- a minified file without `.min` in its name (for example `bundle.js`) is
  analysed too, and usually shows up as CRITICAL. Skip it with
  [`--ignore`](#--ignore-and---include), for example `--ignore 'bundle.js'`.

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

It also stops skipping [minified bundles](#extensions) (`*.min.js`,
`*.min.mjs`, `*.min.cjs`), so they are analysed like any other file.
Declaration files stay skipped: `--no-default-excludes` does not affect
them.

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
- `--include` never brings back a declaration file or a minified bundle.
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
6. declaration files (`.d.ts`, `.d.mts`, `.d.cts`), always; then minified
   bundles (`.min.js`, `.min.mjs`, `.min.cjs`), unless
   `--no-default-excludes`;
7. the symlink rule (see [Symlinks](#symlinks)).

A file dropped by any of these steps is not counted anywhere and no message
is printed.

### Single-file targets

When `<path>` is a single file, the directory exclude list (the defaults
and `--exclude`) is ignored. The other filters still apply:

- the file is skipped if git ignores it, unless you pass `--no-gitignore`;
- `--ignore` and `--include` globs are matched against the file's **name**
  (for example `app.ts`);
- the file must have a supported extension and must not be a declaration
  file;
- a minified bundle (such as `app.min.js`) is skipped, unless you pass
  `--no-default-excludes`. Unlike the directory excludes, this rule applies
  to a single file too.

If `<path>` is a symlink, it is resolved first: its target's parent
directory is mounted, and the target's name is the one shown and matched.

For example, this leaves nothing to analyse, so it prints
`No JavaScript/TypeScript files found for analysis.` and exits `0`:

```
tingle code_check js_complexity ./src/app.test.ts --ignore '*.test.ts'
```

and so does this one, while adding `--no-default-excludes` analyses the
bundle:

```
tingle code_check js_complexity ./public/app.min.js
tingle code_check js_complexity ./public/app.min.js --no-default-excludes
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

## Configuration file

If you always pass the same options, store them once in a configuration
file instead:

```
~/.tingle/code_check/config.json
```

This is the same file that [`file_size`](file_size.md#configuration-file)
and [`rubycritic`](rubycritic.md#configuration-file) use. It is looked up in
your home directory (`$HOME`); its location cannot be changed, and there is
no per-project configuration file. The file is optional: if it does not
exist, the built-in defaults are used and nothing is printed about it.

The file holds a JSON object. The options for this command go under the
`js_complexity` key:

```json
{
  "js_complexity": {
    "warn": 40,
    "top": 20,
    "exclude": ["generated"],
    "fail_on": "error"
  }
}
```

Other top-level keys (such as `file_size` or `rubycritic`) are ignored: they
belong to the other [`tingle code_check`](../code_check.md) subcommands that
share this file, and those subcommands ignore the `js_complexity` key in
turn. If the file exists but has no `js_complexity` key, the built-in
defaults are used, as if the file did not exist. An empty section
(`"js_complexity": {}`) is valid: it changes nothing, but it counts as
loaded, so the header shows the `Config:` line (see [Header](#header)).

### Keys

Every key is optional and matches a command-line option:

| Key | Type | Default | Option |
| --- | --- | --- | --- |
| `warn` | number >= 0 | `50` | `--warn` |
| `error` | number >= 0 | `60` | `--error` |
| `critical` | number >= 0 | `75` | `--critical` |
| `top` | integer >= 0 | `0` | `--top` |
| `fail_on` | `"warn"`, `"error"`, `"critical"` or `null` | `null` | `--fail-on` (`null` means no gate) |
| `details` | integer >= 0 or `null` | `null` | `--details` (`0` lists every function, `null` prints no function lines) |
| `min_level` | `"ok"`, `"warn"`, `"error"` or `"critical"` | `"ok"` | `--min-level` |
| `image` | non-empty string | `darthjee/tingle_js_complexity:<tingle version>` | `--image` |
| `exclude` | list of strings | `[]` | `--exclude` (comma-separated on the command line) |
| `ignore` | list of strings | `[]` | `--ignore` |
| `include` | list of strings | `[]` | `--include` |
| `no_default_excludes` | `true` or `false` | `false` | `--no-default-excludes` (`true` drops the default directories and analyses minified bundles) |
| `gitignore` | `true` or `false` | `true` | `--no-gitignore` (inverted: `"gitignore": false` is the same as `--no-gitignore`) |

Notes:

- The thresholds accept decimals (`"critical": 75.5`). Numbers must be
  real, finite JSON numbers: `true`, `"50"`, `NaN` and `Infinity` are
  errors. `top` and `details` must be whole numbers (`"top": 20.0` is an
  error).
- A `null` value for a single-value key means "not set": the built-in
  default (or the command-line option) is used.
- `image` must not be empty or only spaces. Setting it also means tingle
  does not need to read its version file to pick the default image.
- In lists, write each item as its own string:
  `"exclude": ["test", "fixtures"]`, not `"test,fixtures"`. An empty list is
  valid and adds nothing.
- There is **no `ext` key**: the analysed extensions are fixed (see
  [Extensions](#extensions)), so `"ext"` is reported as
  `unknown key 'ext'`. The path to analyse is not a config key either: you
  always give it on the command line.
- The order of the thresholds is not checked, as on the command line.

### How the config and the command line combine

- **Single values** (`warn`, `error`, `critical`, `top`, `fail_on`,
  `min_level`, `image`, `details`): the command line wins over the config,
  which wins over the built-in default.
- **Lists** (`exclude`, `ignore`, `include`): the config values come first,
  then the command-line values are **added**. Duplicates are dropped (the
  first occurrence is kept). The command line never replaces a config list.
  The [default excludes](#--exclude) are added on top, unless
  `no_default_excludes` ends up true.
- **`no_default_excludes` and `gitignore`**: the config can set either
  value. `--no-default-excludes` and `--no-gitignore` can only turn the
  behaviour off, and they win over the config: `--no-gitignore` skips the
  `.gitignore` step even when the config says `"gitignore": true`, but there
  is no option to turn it back on when the config says `"gitignore": false`.

For example, with this file:

```json
{
  "rubycritic": {
    "warn": 100
  },
  "js_complexity": {
    "warn": 50,
    "error": 60,
    "critical": 75.5,
    "top": 20,
    "exclude": ["generated"],
    "no_default_excludes": false,
    "ignore": ["**/*.test.ts"],
    "include": ["src/**"],
    "gitignore": true,
    "fail_on": "error",
    "min_level": "warn",
    "image": "darthjee/tingle_js_complexity:0.9.0",
    "details": 5
  }
}
```

this command:

```
tingle code_check js_complexity . --warn 40 --exclude fixtures --ignore '**/legacy/**'
```

runs with:

- `warn=40` (the command line wins), `error=60` and `critical=75.5` (from
  the config);
- the default excludes plus `generated` and `fixtures`;
- the ignore globs `**/*.test.ts` and `**/legacy/**`;
- the image `darthjee/tingle_js_complexity:0.9.0`, and the other values
  (`top`, `include`, `fail_on`, `min_level`, `details`) from the config.

The `rubycritic` section is ignored here.

### Running without the config: `--no-config`

Some config values cannot be undone from the command line. For example,
there is no option to turn the gate off when the config sets `fail_on`, or
to turn `.gitignore` back on when it sets `"gitignore": false`. Pass
`--no-config` to ignore the file completely:

```
tingle code_check js_complexity . --no-config
```

With `--no-config`, the file is not read or checked at all (even an invalid
one), and only the built-in defaults and the options you pass are used. No
`Config:` line is printed.

### Config errors

The file is checked every time it is read, even when you pass every option
on the command line. If something is wrong, the command prints one error
line on standard error and exits with status `1`, before selecting any file
or calling Docker:

```
Error: /home/me/.tingle/code_check/config.json: <reason>
```

| Problem | Reason |
| --- | --- |
| The file cannot be read | `cannot read file: <OS error>` |
| The file is not valid JSON | `invalid JSON: <details>` |
| The top level is not a JSON object | `top level must be an object` |
| The `js_complexity` section is not a JSON object | `'js_complexity' must be an object` |
| An unknown key, such as a typo or `ext` | `unknown key '<key>'` |
| A wrong type or value | for example `'warn' must be a number >= 0`, `'top' must be an integer >= 0`, `'details' must be an integer >= 0 or null`, `'image' must be a non-empty string` or `'fail_on' must be one of warn, error, critical or null` |

For example:

```
Error: /home/me/.tingle/code_check/config.json: unknown key 'ext'
Error: /home/me/.tingle/code_check/config.json: 'warn' must be a number >= 0
```

Only the first problem is reported. Fix the file, or run with `--no-config`
in the meantime. An invalid `js_complexity` section only breaks this
command: `file_size` and `rubycritic` read only their own sections, and the
reverse is true too.

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

Status             FTA  Cyclo  Lines    Dup  Assessment         File
──────────────── ─────  ─────  ─────  ─────  ─────────────────  ──────────────────────────────────────────────────
🔴 ERROR           71.3    136    245      0  Needs improvement  fixture/complex.ts
✅ OK              37.4      3     18      0  OK                 fixture/component.tsx
✅ OK              35.1      9     23     23  OK                 fixture/dup_b.js
✅ OK              35.0      9     23     23  OK                 fixture/dup_a.js
✅ OK              31.0      3     11      0  OK                 fixture/widget.jsx
✅ OK               7.7      1      6      0  OK                 fixture/simple.js
✅ OK               7.3      2      6      0  OK                 fixture/bom.ts
✅ OK               7.3      2      6      0  OK                 fixture/crlf.js
✅ OK               7.3      2      6      0  OK                 fixture/ext/UPPER.JS
✅ OK               7.3      2      6      0  OK                 fixture/ext/a.mjs
✅ OK               7.3      2      6      0  OK                 fixture/ext/b.cjs
✅ OK               7.3      2      6      0  OK                 fixture/ext/c.mts
✅ OK               7.3      2      6      0  OK                 fixture/ext/d.cts
✅ OK               3.5      1      1      0  OK                 fixture/short.js
✅ OK               0.0      -      -      0  -                  fixture/empty.js
⛔ PARSE              -      -      -      -  -                  fixture/broken.js
⛔ PARSE              -      -      -      -  -                  fixture/latin1.js

──────────────────────────────────────────────────────────────────────────────
Summary: 17 file(s) | 14 OK | 0 WARN | 1 ERROR | 0 CRITICAL | 2 skipped (parse error)
FTA score: avg 18.14 | max 71.30
```

In this project, the files under `build/` are skipped (a default exclude),
`ext/types.d.ts` is skipped (a declaration file) and `bundle.min.js` is
skipped (a minified bundle). Before the report, a
warning for each of `broken.js` and `latin1.js` is printed on standard error
(see [Parse warnings](#parse-warnings)).

### Header

- `Analyzing:` shows the target as an absolute path.
- `Thresholds:` shows the `warn`, `error` and `critical` values in use.
- `Image:` shows the Docker image that runs FTA, jscpd and escomplex.
- `Config:` (dimmed) shows the path of the configuration file, when a
  `js_complexity` section was loaded from it, even an empty one. It is not
  printed when the file or the section does not exist, or with
  `--no-config` (see [Configuration file](#configuration-file)).

### Function lines

With [`--details`](#--details), indented lines follow some file rows, one per
function, dimmed in a terminal:

```
                 cyclo  12  sloc   27  reducer  (fixture/complex.ts:9)
```

- `cyclo`: the function's own cyclomatic complexity (at least `1`);
- `sloc`: the number of lines the function spans, from its first line to its
  last;
- the function's name. A class method is shown as `Class.method` (for
  example `Store.dispatch`), with `<anonymous>` as the class name for an
  unnamed class. An anonymous function (an arrow function or a callback,
  for example) is shown as `<anon method-N>`. Nested functions are listed
  too, as their own lines;
- in parentheses, the file (as in the `File` column) and the line where the
  function starts, as your editor numbers it (Windows line endings and a
  leading BOM do not shift it).

A file's function values do not add up to its `Cyclo` or `Lines` columns:
those come from FTA and also count the code outside functions.

When the per-function data is not available for a shown row, a single dim
note replaces its function lines:

```
                 (per-function data unavailable)
```

This happens when escomplex could not parse a file that FTA could (for
example very recent TypeScript syntax), when escomplex failed as a whole
(see [escomplex failures](#escomplex-failures)), or with an older image
passed through [`--image`](#--image) that does not report functions. The row
keeps its level, and the exit status does not change. A file that simply has
no function gets neither function lines nor this note.

### Columns

| Column | Meaning |
| --- | --- |
| `Status` | The level of the file (see [Thresholds and levels](#thresholds-and-levels)). |
| `FTA` | The file's FTA score, rounded to one decimal. This is the value compared with the thresholds. |
| `Cyclo` | The file's cyclomatic complexity, as reported by FTA. Information only. |
| `Lines` | The file's number of code lines, as counted by FTA. Information only. |
| `Dup` | The number of the file's lines that are inside an exact copy-pasted block (a clone), as found by jscpd (see [Duplicated lines](#duplicated-lines)). Information only. `-` means the value is not available. |
| `Assessment` | FTA's own verdict: `OK`, `Could be better` or `Needs improvement`. Information only. |
| `File` | For a directory target, the path relative to the target's parent directory, so it starts with the directory's name (`fixture/...` above). For a single-file target, only the file name. |

### Sort order

Level rows come first, sorted by FTA score, highest first; files with the
same score are sorted by path. The `⛔ PARSE` rows follow, sorted by path.

### Files shown as `OK 0.0`

FTA leaves out the files that have no code line: empty files, and files with
only blank lines or comments. Such a file is still listed, as `✅ OK` with a
score of `0.0` and `-` in the `Cyclo`, `Lines` and `Assessment` columns, so
the file count matches the selection (`fixture/empty.js` above). jscpd still
reads it, so its `Dup` column shows `0`.

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

It appears as a `⛔ PARSE` row, with `-` in every value column (`Dup`
included), and in the
`skipped (parse error)` count. It is never in the level counts or the FTA
score line, and it never changes the exit status.

### Duplicated lines

The `Dup` column counts the file's lines that are part of an exact clone: a
block of at least 50 tokens and 5 lines that appears more than once, either
in another selected file or elsewhere in the same file. jscpd finds the
clones; only exact copies count, so a copy with renamed variables is not a
match.

- Each line counts **once**, however many clones cover it. In the sample
  above, `dup_a.js` and `dup_b.js` share one 23-line block, so both show
  `23`.
- Only the **selected files** are compared with each other. A copy in an
  excluded or ignored file (for example under `node_modules`) is never
  counted.
- Copies between JavaScript and TypeScript files are found too (for
  example a `.js` file and a `.ts` file).
- `0` means the file was checked and has no duplicated line.
- `-` means the value is not available: the file could not be parsed
  (`⛔ PARSE` rows), it is larger than 1 MiB (1,048,576 bytes), or jscpd
  failed (see below).

The column is for information only: it never changes the file's level, the
`--fail-on` gate, the exit status or the summary.

If jscpd fails inside the image, the analysis still completes. Tingle prints
one warning on standard error, before the report:

```
Warning: jscpd failed in <image>; duplication data is not available: <message>
```

The `Dup` column then shows `-` on every row. The exit status is not
changed.

### escomplex failures

If escomplex fails as a whole inside the image (it crashed, ran out of
memory, or gave output tingle could not read), the analysis still completes.
Tingle prints one warning on standard error, before the report:

```
Warning: escomplex failed in <image>; per-function data is not available: <message>
```

With [`--details`](#--details), every level row then shows the
`(per-function data unavailable)` note. The levels, the summary and the exit
status are not changed. The warning is printed with or without `--details`.

When escomplex cannot parse a single file, no warning is printed: only that
file's row shows the note under `--details`.

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

Show the 3 most complex functions of each of the 5 most complex files:

```
tingle code_check js_complexity ./src --top 5 --details 3
```

Ignore your configuration file for one run:

```
tingle code_check js_complexity . --no-config
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
| Negative `--details` | `Error: --details must be an integer >= 0` | `1` |
| Empty `--image` | `Error: --image must not be empty` | `1` |
| Invalid configuration file (unreadable, bad JSON, unknown key, wrong value, ...) | `Error: <config file>: <reason>` (see [Config errors](#config-errors)) | `1` |
| `<path>` does not exist | `Error: path not found: <absolute path>` | `1` |
| `<path>` cannot be read | `Error: path not readable: <absolute path>` | `1` |
| The folder to mount contains `:` | `Error: cannot mount <folder>: Docker volume paths cannot contain ':'` | `1` |
| Tingle version unreadable, and no `--image` or `image` in the config | `Error: cannot read the tingle version from <file>; use --image to choose the image` | `1` |
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
| `1` | Usage error, invalid configuration file, path problem, or Docker / FTA failure |
| `2` | The complexity gate failed (`--fail-on`) |

Unparsable files (`⛔ PARSE` rows), files shown as `OK 0.0`, the `Dup`
column, the function lines of `--details`, the
`(per-function data unavailable)` note and a jscpd or escomplex failure
warning never change the exit status on their own. The report always goes to standard output and
error messages to standard error.

## Limitations

- **Podman is not supported.** It may work when aliased as `docker`, but
  this is not tested.
- **No Docker-in-Docker.** The `darthjee/tingle` container (used by
  [`tingle linux`](../linux.md)) has no `docker` command, so running this
  subcommand inside it fails with `docker not found on PATH`. Run it on a
  host with Docker.
- **Minified bundles are detected by name only.** `*.min.js`-style bundles
  (`.min.js`, `.min.mjs`, `.min.cjs`) are skipped by default (see
  [Extensions](#extensions)). A minified file without `.min` in its name is
  still analysed and gets a high score, usually CRITICAL: skip it with
  `--ignore` (for example `--ignore 'public/bundle.js'`), or keep it under a
  default-excluded directory such as `dist/` or in `.gitignore`.
- **Generated code is analysed** unless it is skipped by the selection
  rules. Keep it out with `.gitignore`, `--exclude` or `--ignore` (for
  example `--ignore '*.generated.ts'`).

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
(`--fail-on`) and **Image** (`--image`), then describes the
**Configuration** (the `js_complexity` section and `--no-config`), followed
by the exit codes and a few examples.
