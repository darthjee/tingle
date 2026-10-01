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
  except for the files left out by the selection filters: excluded
  directories, files ignored by git, and the `--ignore` / `--include` globs
  (see [File selection](#file-selection));
- **a single `.rb` file**: only that file is analysed. If it is a symlink,
  it is resolved first, and its target's parent directory is mounted into
  the container; otherwise its own parent directory is. The directory
  excludes do not apply, and the `--ignore` / `--include` globs are matched
  against the file name (see [Single-file targets](#single-file-targets)).
  A file that does not end in `.rb` leaves nothing to analyse.

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
| `--exclude LIST` | none | Extra directory names to skip (comma-separated), added to the [default excludes](#--exclude). |
| `--no-default-excludes` | off | Do not skip the default directories; only `--exclude` names apply. |
| `--no-gitignore` | off | Do not skip files ignored by git (`.gitignore`, `.git/info/exclude`, global excludes). |
| `--ignore GLOB` | none | Skip files whose path relative to `<path>` matches this glob. Can be repeated. |
| `--include GLOB` | none | Only analyse `.rb` files whose path relative to `<path>` matches this glob. Can be repeated. |
| `--no-config` | off | Do not read `~/.tingle/code_check/config.json` (see [Configuration file](#configuration-file)). |

The thresholds accept decimals (`--warn 12.5`) and must be `0` or more.
`--top` and `--details N` must be whole numbers, `0` or more, and `--image`
must not be empty.
The order of the thresholds is not checked: keep `warn` < `error` <
`critical`, or the labels will not make sense.

There is no `--ext` option: only `.rb` files are ever analysed. The file
selection options are described in [File selection](#file-selection).

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
read its version file (and you did not pass `--image` or set `image` in the
[configuration file](#configuration-file)), the command fails and suggests
`--image`:

```
Error: cannot read the tingle version from /path/to/tingle/shell/linux/VERSION; use --image to choose the image
```

## File selection

The files to analyse are chosen on your machine, before Docker is called.
Only the selected files are sent to the container. The options work as in
[`tingle code_check file_size`](file_size.md#--exclude), except that the
`.rb` filter is fixed (there is no `--ext`) and there is no binary check.

### `--exclude`

The default list is:

```
node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,.cache,coverage,.nuxt,out,target,tmp,log,.bundle
```

That is the [`file_size`](file_size.md#--exclude) default list plus `tmp`,
`log` and `.bundle`. These directories are always skipped unless you pass
[`--no-default-excludes`](#--no-default-excludes). Passing `--exclude`
**adds** names to this list:

```
tingle code_check rubycritic . --exclude spec,db
```

skips `spec` and `db` as well as `vendor`, `tmp`, `log` and the rest.

A file is skipped when **any** part of its path **relative to `<path>`**
matches one of the names. Matching is case-insensitive (`Spec` matches
`spec`) and covers a whole path component: `spec` does not match `specs`.
The directories *above* `<path>` are never checked, so a project living in
`~/work/tmp/my-app` is analysed normally.

The names are plain directory names, not globs. To skip files by pattern,
use [`--ignore`](#--ignore-and---include).

| Invocation | Excluded names |
| --- | --- |
| `tingle code_check rubycritic .` | The defaults |
| `tingle code_check rubycritic . --exclude spec` | The defaults + `spec` |
| `tingle code_check rubycritic . --no-default-excludes` | None (`.git/` and `vendor/` are walked too) |
| `tingle code_check rubycritic . --no-default-excludes --exclude spec` | Only `spec` |

`--exclude` is not repeatable: if you pass it more than once, only the last
one counts. Put all the names in a single comma-separated list.

Spaces around each name are trimmed and empty entries are dropped, so
`--exclude ' spec, ,db'` adds `spec` and `db`, and `--exclude ''` adds
nothing. A name that is already a default (`--exclude vendor`) has no extra
effect and is not an error.

### `--no-default-excludes`

Drops the default list, so directories such as `vendor/`, `tmp/` and `.git/`
are walked too. On its own, it skips no directory at all:

```
tingle code_check rubycritic . --no-default-excludes
```

Combine it with `--exclude` to choose exactly which names to skip:

```
tingle code_check rubycritic . --no-default-excludes --exclude .git,spec
```

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
every file under it.

To turn this step off and analyse ignored files too, pass `--no-gitignore`:

```
tingle code_check rubycritic . --no-gitignore
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
  `darthjee/tingle_rubycritic` image has no git, and does not need it.

### `--ignore` and `--include`

These options filter files by a glob pattern, similar to a `.gitignore`
line:

- `--ignore GLOB` skips every file that matches the glob.
- `--include GLOB` analyses **only** the `.rb` files that match the glob.
  Without any `--include`, every `.rb` file is included.

Both can be repeated. A file is skipped if it matches **any** `--ignore`
glob, and kept if it matches **any** `--include` glob.

The glob is matched against the file's path **relative to `<path>`**,
always written with `/` (for example `app/models/user.rb` when `<path>` is
the project root). The whole path must match, not just part of it. Matching
is case-insensitive, so `*_spec.rb` also matches `user_SPEC.rb`.

> **Quote your globs.** Write `--ignore 'db/migrate/**'`, not
> `--ignore db/migrate/**`. Without quotes, your shell may expand the
> pattern into file names before `tingle` sees it.

The glob syntax is the same as for `file_size` (see
[Glob syntax](file_size.md#glob-syntax) and
[Where a pattern matches](file_size.md#where-a-pattern-matches)). In short:

- `*` matches within one path segment, `**` spans directories;
- a pattern with no `/` matches in any directory (`*_spec.rb` is the same as
  `**/*_spec.rb`);
- a pattern with a `/` is anchored at `<path>`, and a leading `/` only marks
  the anchor (`/app/*.rb` is the same as `app/*.rb`);
- a trailing `/` matches everything under that directory (`concerns/` is the
  same as `**/concerns/**`).

Combining filters:

- `--ignore` wins over `--include`: a file that matches both is skipped.
- `--include` and the `.rb` filter must **both** match: `--include '*.rake'`
  leaves nothing to analyse.
- Excluded directories (the defaults plus any `--exclude` names) are always
  skipped, whatever the globs say.

A glob that matches nothing is not an error, and an empty pattern
(`--ignore ''`) is ignored.

| Command | Effect |
| --- | --- |
| `tingle code_check rubycritic . --ignore 'db/migrate/**'` | Skips every migration. |
| `tingle code_check rubycritic . --ignore '*_spec.rb'` | Skips every spec file, in any directory. |
| `tingle code_check rubycritic . --include 'app/**'` | Analyses only the `.rb` files under `app/`. |
| `tingle code_check rubycritic . --include 'app/**' --ignore 'app/admin/'` | Analyses the `.rb` files under `app/`, except those under `app/admin/`. |

### Filter order

For a directory `<path>`, every file found below it goes through these
steps, in order. The first step that rejects a file drops it:

1. the default excludes (skipped with `--no-default-excludes`);
2. the `--exclude` names;
3. `.gitignore` (skipped with `--no-gitignore`);
4. the `--ignore` globs;
5. the `--include` globs (when given) **and** the `.rb` suffix, in any case;
6. the symlink rule (see [Symlinks](#symlinks)).

### Single-file targets

When `<path>` is a single file, the exclude list (the defaults, `--exclude`
and `--no-default-excludes`) is ignored. The other filters still apply:

- the file is skipped if git ignores it, unless you pass `--no-gitignore`;
- `--ignore` and `--include` globs are matched against the file's **name**
  (for example `user.rb`);
- the file must end in `.rb`.

If `<path>` is a symlink, it is resolved first: its target's parent
directory is mounted, and the target's name is the one shown and matched.

For example, this leaves nothing to analyse, so it prints
`No Ruby files found for analysis.` and exits `0`:

```
tingle code_check rubycritic ./app/models/user.rb --ignore 'user.*'
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

## Configuration file

If you always pass the same options, store them once in a configuration
file instead:

```
~/.tingle/code_check/config.json
```

This is the same file that [`file_size`](file_size.md#configuration-file)
uses. It is looked up in your home directory (`$HOME`); its location cannot
be changed, and there is no per-project configuration file. The file is
optional: if it does not exist, the built-in defaults are used and nothing
is printed about it.

The file holds a JSON object. The options for this command go under the
`rubycritic` key:

```json
{
  "rubycritic": {
    "warn": 50,
    "top": 20,
    "ignore": ["spec/fixtures/**"],
    "fail_on": "error"
  }
}
```

Other top-level keys (such as `file_size`) are ignored: they belong to the
other [`tingle code_check`](../code_check.md) subcommands that share this
file. If the file exists but has no `rubycritic` key, the built-in defaults
are used, as if the file did not exist. An empty section
(`"rubycritic": {}`) is valid: it changes nothing, but it counts as loaded,
so the header shows the `Config:` line (see [Header](#header)).

### Keys

Every key is optional and matches a command-line option:

| Key | Type | Default | Option |
| --- | --- | --- | --- |
| `warn` | number >= 0 | `100` | `--warn` |
| `error` | number >= 0 | `200` | `--error` |
| `critical` | number >= 0 | `400` | `--critical` |
| `top` | integer >= 0 | `0` | `--top` |
| `fail_on` | `"warn"`, `"error"`, `"critical"` or `null` | `null` | `--fail-on` (`null` means no gate) |
| `min_level` | `"ok"`, `"warn"`, `"error"` or `"critical"` | `"ok"` | `--min-level` |
| `image` | non-empty string | `darthjee/tingle_rubycritic:<tingle version>` | `--image` |
| `details` | integer >= 0 or `null` | `null` | `--details` (`0` lists every method, `null` prints no method lines) |
| `exclude` | list of strings | `[]` | `--exclude` (comma-separated on the command line) |
| `ignore` | list of strings | `[]` | `--ignore` |
| `include` | list of strings | `[]` | `--include` |
| `no_default_excludes` | `true` or `false` | `false` | `--no-default-excludes` |
| `gitignore` | `true` or `false` | `true` | `--no-gitignore` (inverted: `"gitignore": false` is the same as `--no-gitignore`) |

Notes:

- The thresholds accept decimals (`"critical": 400.5`). Numbers must be
  real, finite JSON numbers: `true`, `"100"`, `NaN` and `Infinity` are
  errors. `top` and `details` must be whole numbers (`"top": 20.0` is an
  error).
- `image` must not be empty or only spaces. Setting it also means tingle
  does not need to read its version file to pick the default image.
- In lists, write each item as its own string: `"exclude": ["spec", "db"]`,
  not `"spec,db"`. An empty list is valid and adds nothing.
- There is **no `ext` key**: only `.rb` files are analysed, so `"ext"` is
  reported as `unknown key 'ext'`. The path to analyse is not a config key
  either: you always give it on the command line.
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
  behaviour off, and they win over the config.

For example, with this file:

```json
{
  "file_size": {
    "warn": 250
  },
  "rubycritic": {
    "warn": 100,
    "error": 200,
    "critical": 400.5,
    "top": 20,
    "exclude": ["db"],
    "no_default_excludes": false,
    "ignore": ["spec/fixtures/**"],
    "include": ["app/**", "lib/**"],
    "gitignore": true,
    "fail_on": "error",
    "min_level": "warn",
    "image": "darthjee/tingle_rubycritic:0.6.0",
    "details": 5
  }
}
```

this command:

```
tingle code_check rubycritic . --warn 50 --exclude tmp2 --ignore '**/legacy/**'
```

runs with:

- `warn=50` (the command line wins), `error=200` and `critical=400.5` (from
  the config);
- the default excludes plus `db` and `tmp2`;
- the ignore globs `spec/fixtures/**` and `**/legacy/**`;
- the image `darthjee/tingle_rubycritic:0.6.0`, and the other values
  (`top`, `include`, `fail_on`, `min_level`, `details`) from the config.

The `file_size` section is ignored here.

### Running without the config: `--no-config`

Some config values cannot be undone from the command line. For example,
there is no option to turn the gate off when the config sets `fail_on`, or
to turn `.gitignore` back on when it sets `"gitignore": false`. Pass
`--no-config` to ignore the file completely:

```
tingle code_check rubycritic . --no-config
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
| The `rubycritic` section is not a JSON object | `'rubycritic' must be an object` |
| An unknown key, such as a typo or `ext` | `unknown key '<key>'` |
| A wrong type or value | for example `'warn' must be a number >= 0`, `'top' must be an integer >= 0`, `'details' must be an integer >= 0 or null`, `'image' must be a non-empty string` or `'fail_on' must be one of warn, error, critical or null` |

For example:

```
Error: /home/me/.tingle/code_check/config.json: unknown key 'ext'
Error: /home/me/.tingle/code_check/config.json: 'warn' must be a number >= 0
```

Only the first problem is reported. Fix the file, or run with `--no-config`
in the meantime.

## Skipped files

A file under `<path>` is left out of the analysis when:

- it does not end in `.rb` (in any case);
- it is under an excluded directory (the defaults or `--exclude`);
- git ignores it (unless you pass `--no-gitignore`);
- it matches an `--ignore` glob, or does not match any `--include` glob;
- it is a symlink pointing outside `<path>`, or a dangling symlink.

See [File selection](#file-selection) for the details. By default, these
directories are skipped:

```
node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,.cache,coverage,.nuxt,out,target,tmp,log,.bundle
```

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

- If no `.rb` file is left (none exist, or the filters leave none), the
  command prints the header and
  `No Ruby files found for analysis.`, then exits `0` without calling Docker
  at all.

## Reading the output

Sample run against a small project, with low thresholds:

```
$ tingle code_check rubycritic fixture --warn 10 --error 50 --critical 100
Analyzing: /home/me/fixture
Thresholds: warn=10 | error=50 | critical=100
Image: darthjee/tingle_rubycritic:0.5.0
Config: /home/me/.tingle/code_check/config.json

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
- `Config:` (dimmed) shows the path of the configuration file, when a
  `rubycritic` section was loaded from it, even an empty one. It is not
  printed when the file or the section does not exist, or with
  `--no-config` (see [Configuration file](#configuration-file)).

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

Skip the `spec` and `db` directories, on top of the defaults:

```
tingle code_check rubycritic . --exclude spec,db
```

Skip every migration:

```
tingle code_check rubycritic . --ignore 'db/migrate/**'
```

Analyse only the Ruby files under `app/`:

```
tingle code_check rubycritic . --include 'app/**'
```

Also analyse the files git ignores:

```
tingle code_check rubycritic . --no-gitignore
```

Walk every directory except `.git/`, including `vendor/` and `tmp/`:

```
tingle code_check rubycritic . --no-default-excludes --exclude .git
```

Ignore your configuration file for one run:

```
tingle code_check rubycritic . --no-config
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
| Invalid configuration file (unreadable, bad JSON, unknown key, wrong value, ...) | `Error: <config file>: <reason>` (see [Config errors](#config-errors)) | `1` |
| Tingle version unreadable and no `--image` or `image` | `Error: cannot read the tingle version from <file>; use --image to choose the image` | `1` |
| No `.rb` files to analyse (or all filtered out) | The header, then `No Ruby files found for analysis.` | `0` |
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
| `1` | Usage error, invalid configuration file, path problem, or Docker / RubyCritic failure |
| `2` | The complexity gate failed (`--fail-on`) |

Unparsable Ruby files (`⛔ PARSE` rows) never change the exit status. The
report always goes to standard output and error messages to standard error.

## Limitations

- **No Docker-in-Docker.** The `darthjee/tingle` container (used by
  [`tingle linux`](../linux.md)) has no `docker` command, so running this
  subcommand inside it fails with `docker not found on PATH`. Run it on a
  host with Docker.

## Quick help

For a short summary of the command's options, run:

```
tingle code_check rubycritic --help
```

`tingle --help code_check` shows the options of every `code_check`
subcommand, together with their list.
