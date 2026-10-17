# `tingle code_check php_complexity`

PHP code complexity via PDepend (Docker).

This is a subcommand of [`tingle code_check`](../code_check.md).

## What it does

`tingle code_check php_complexity` finds the PHP files that are the hardest
to read, test and maintain, so you know where to refactor first.

It selects the `.php` files under a file or directory on your machine, then
runs [PDepend](https://pdepend.org/) on them inside the
`darthjee/tingle_php_complexity` Docker image. Before PDepend runs, the
image checks each file with PHP's own parser, so files with a syntax error
are reported as such instead of getting a misleading score.

Each file gets one row in a report, labelled OK, WARN, ERROR or CRITICAL.
The label comes from the file's **total CCN** (see
[The metric: total CCN](#the-metric-total-ccn)) compared with thresholds you
can choose. The other columns (the highest method CCN, NPath, the
maintainability index and the line count) are shown for information only:
they never change the label or the exit status.

## Requirements

- **Docker**, with the `docker` command on your `PATH` and a running daemon.
  You do not need PHP or Composer on your machine: PHP and PDepend run
  inside the image.
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

PDepend's memory use grows with the number of files: a large framework of
about 3,000 files needs around 2 GB. If Docker kills the container, the
command fails with `Error: PDepend failed in <image> (exit <status>)`. Raise
Docker's memory limit, or analyse a smaller folder.

## Usage

```
tingle code_check php_complexity <path> [options]
```

`<path>` can be:

- **a directory**: every `.php` file below it is analysed, recursively,
  except for the files left out by the selection rules (see
  [File selection](#file-selection)). The directory is mounted into the
  container;
- **a single file**: only that file is analysed. If it is a symlink, it is
  resolved first, and its target's parent directory is mounted into the
  container; otherwise its own parent directory is. A file that does not end
  in `.php`, or a Blade template (`*.blade.php`), leaves nothing to analyse.

The file list is sent to the container on its standard input, so there is no
limit on the number of files, and the run has no timeout.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `--warn N` | `20` | Files with a total CCN of at least `N` are marked WARN. |
| `--error N` | `40` | Files with a total CCN of at least `N` are marked ERROR. |
| `--critical N` | `60` | Files with a total CCN of at least `N` are marked CRITICAL. |
| `--top N` | `0` | Show only the `N` most complex files. `0` shows all files. |
| `--min-level LEVEL` | `ok` | Show only files at `LEVEL` or higher. `LEVEL` is `ok`, `warn`, `error` or `critical`. |
| `--fail-on LEVEL` | off | Exit with status `2` if any file is at `LEVEL` or higher. `LEVEL` is `warn`, `error` or `critical`. |
| `--image IMAGE` | `darthjee/tingle_php_complexity:<tingle version>` | Docker image to run. |
| `--exclude a,b` | none | Extra directory names to skip (comma-separated), **added** to the [default excludes](#--exclude). |
| `--no-default-excludes` | off | Do not skip the default directories or `bootstrap/cache`; only `--exclude` names apply. |
| `--no-gitignore` | off | Do not skip files ignored by git (`.gitignore`, `.git/info/exclude`, global excludes). |
| `--ignore GLOB` | none | Skip files whose path relative to `<path>` matches `GLOB`. Can be repeated. |
| `--include GLOB` | all | Only analyse PHP files whose path relative to `<path>` matches `GLOB`. Can be repeated. |

The thresholds accept decimals (`--warn 22.5`) and must be `0` or more.
`--top` must be a whole number, `0` or more, and `--image` must not be
empty. The order of the thresholds is not checked: keep `warn` < `error` <
`critical`, or the labels will not make sense.

The file selection options are described in
[File selection](#file-selection). There is no option to change the analysed
extension (no `--ext`).

### `--min-level` and `--top`

These options only change **which level rows are shown**:

- `--min-level LEVEL` keeps the rows at `LEVEL` or higher, using the order
  OK < WARN < ERROR < CRITICAL;
- then `--top N` (when `N` is more than `0`) keeps the `N` most complex rows
  left.

`⛔ PARSE` rows (files that could not be parsed) are **always shown**, below
the level rows, and are not counted by `--top`.

When no row at all is left to show, the table is replaced by a short note,
followed by the usual summary:

```
No files at or above WARN.
```

The `Summary:` and `CCN:` lines and the `--fail-on` gate always count every
selected file, shown or not.

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
- If there are no PHP files to analyse, the command exits `0`.

### `--image`

By default the image is `darthjee/tingle_php_complexity:<tingle version>`,
where the version is read from tingle's own `shell/linux/VERSION` file, so
each tingle release uses the matching image. `--image` runs another image
instead, for example one you built locally:

```
tingle code_check php_complexity ./src --image tingle_php_complexity:dev
```

The image is pulled only when it is not present locally. If tingle cannot
read its version file and you did not pass `--image`, the command fails and
suggests `--image`:

```
Error: cannot read the tingle version from /path/to/tingle/shell/linux/VERSION; use --image to choose the image
```

## The metric: total CCN

The level of a file comes from its **total CCN**: the sum of the cyclomatic
complexity (CCN) of every function and method that PDepend finds in the
file, across all its classes and traits. Each `if`, `elseif`, loop, `case`,
`catch`, `&&`, `||`, `?:` and `??` adds a decision point; a function with no
decision has a CCN of `1`.

- **Several classes in one file add up.** A file with two classes and a
  trait gets the sum of all their methods.
- **Top-level code counts 0.** Statements outside any function or method
  (top-level `if` or `foreach`, top-level closures and arrow functions) are
  not counted. A closure *inside* a function or method counts toward that
  function.
- **Mixed HTML/PHP** (templates such as `page.php`) is parsed: only the
  functions in the PHP blocks count, not the inline HTML or the top-level
  control flow.
- The total CCN is a whole number, so no rounding is involved.

### Why 20 / 40 / 60

The default thresholds were checked against three public codebases:
`laravel/framework` (3,028 files), `symfony/console` (382 files) and the
legacy-style CodeIgniter 3 (282 files), tests included:

- most files are OK in every codebase (69% to 83%), so a WARN stands out;
- ERROR or worse is rare in the modern codebases (about 8% of the files) and
  more common in the legacy one (17%), which is the signal a complexity check
  should give;
- the CRITICAL files are the expected ones, such as Laravel's query
  `Builder.php` (total 493), Symfony's `Application.php` (290) and
  CodeIgniter's `DB_query_builder.php` (304).

Lower thresholds such as `10/25/50` put a third to a half of the files at
WARN or above; higher ones such as `30/60/100` leave almost nothing
CRITICAL. Use `--warn`, `--error` and `--critical` to tune them for your
project.

### Large test classes

A total is a per-file measure: a big test class with many simple test
methods can reach a high total CCN even though each method is trivial (in
Laravel, `DatabaseQueryBuilderTest.php` has a total of 494, with no method
above 1). The `Max` column shows this: a high `CCN` with a low `Max` means
"many simple methods", not "a few tangled ones". See
[Tests and generated code](#tests-and-generated-code) to leave such files
out.

## Thresholds and levels

| Status | Rule | Default range |
| --- | --- | --- |
| ✅ OK | total CCN below `--warn` | below 20 |
| ⚠️ WARN | at least `--warn`, below `--error` | 20 to 39 |
| 🔴 ERROR | at least `--error`, below `--critical` | 40 to 59 |
| 🟣 CRITICAL | at least `--critical` | 60 and above |
| ⛔ PARSE | PHP or PDepend could not parse the file | - |

Each threshold is inclusive: a file with a total CCN of exactly `40` is
ERROR, not WARN. With a decimal threshold such as `--warn 2.5`, a total of
`2` is OK and `3` is WARN.

## File selection

The files to analyse are chosen on your machine, before Docker is called.
Only the selected files are sent to the container. By default:

- only `.php` files are analysed (see [Extension](#extension));
- Blade templates are always skipped (see [Skip rules](#skip-rules));
- the [default excludes](#--exclude) and Laravel's `bootstrap/cache`
  directory are skipped;
- files ignored by git are skipped (see
  [.gitignore and `--no-gitignore`](#gitignore-and---no-gitignore)).

The options below change this selection. The order in which the filters are
applied is described in [Filter order](#filter-order).

### Extension

A file is analysed when its name ends in `.php`, in any case (`UPPER.PHP`
counts). `.phtml`, `.inc` and the legacy `.php3` to `.php8` are not
analysed. There is no option to change this (no `--ext`).

### Skip rules

Two rules skip PHP files that are not code you write:

- **Blade templates** (names ending in `.blade.php`, in any case, such as
  `welcome.blade.php` or `View.BLADE.PHP`) are always skipped: they are
  templates, not PHP code. No option turns this off, and `--include` never
  brings one back: `--include '**/*.blade.php'` leaves nothing to analyse.
- **`bootstrap/cache`:** Laravel's cached config, routes and services are
  skipped too. A file is skipped when the directories in its path relative
  to `<path>` contain a `bootstrap` directory directly followed by a `cache`
  directory (in any case):

  | File (relative to `<path>`) | Skipped? |
  | --- | --- |
  | `bootstrap/cache/services.php` | yes |
  | `app/Bootstrap/Cache/x.php` | yes |
  | `bootstrap/app.php` | no |
  | `cache/bootstrap/x.php` | no |
  | `bootstrap/other/cache/x.php` | no |

  [`--no-default-excludes`](#--no-default-excludes) turns this rule off.
  It does not apply when `<path>` is a single file, nor to the directories
  *above* `<path>`: `tingle code_check php_complexity app/bootstrap/cache`
  analyses the files in that directory.

  This rule is not an `--exclude` name: `--exclude` matches one path
  component at a time, so `--exclude bootstrap/cache` matches nothing.

A file dropped by a skip rule is not counted anywhere and no message is
printed.

### `--exclude`

The default list is:

```
node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,.cache,coverage,.nuxt,out,target,var,storage,.phpunit.cache
```

That is the [`file_size`](file_size.md#--exclude) default list plus `var`,
`storage` and `.phpunit.cache`, the cache and runtime folders of common PHP
frameworks and tools. These directories are always skipped unless you pass
[`--no-default-excludes`](#--no-default-excludes). Passing `--exclude`
**adds** names to this list:

```
tingle code_check php_complexity . --exclude tests,fixtures
```

skips `tests` and `fixtures` as well as `vendor`, `var`, `storage` and the
rest.

A file is skipped when **any** part of its path **relative to `<path>`**
matches one of the names. Matching is case-insensitive (`Tests` matches
`tests`) and covers a whole path component: `build` does not match
`builder`. The directories *above* `<path>` are never checked, so a project
living in `~/work/build/my-app` is analysed normally.

The names are plain directory names, not globs or paths. To skip files by
pattern, use [`--ignore`](#--ignore-and---include).

| Invocation | Excluded names |
| --- | --- |
| `tingle code_check php_complexity .` | The defaults (and `bootstrap/cache`) |
| `tingle code_check php_complexity . --exclude tests` | The defaults + `tests` (and `bootstrap/cache`) |
| `tingle code_check php_complexity . --no-default-excludes` | None (`vendor/`, `storage/` and `bootstrap/cache/` are walked too) |
| `tingle code_check php_complexity . --no-default-excludes --exclude tests` | Only `tests` |

`--exclude` is not repeatable: if you pass it more than once, only the last
one counts. Put all the names in a single comma-separated list.

Spaces around each name are trimmed and empty entries are dropped, so
`--exclude ' tests, ,fixtures'` adds `tests` and `fixtures`, and
`--exclude ''` adds nothing. A name that is already a default
(`--exclude vendor`) has no extra effect and is not an error.

### `--no-default-excludes`

Drops the default list, so directories such as `vendor/`, `storage/` and
`.git/` are walked too. On its own, it skips no directory at all:

```
tingle code_check php_complexity . --no-default-excludes
```

Combine it with `--exclude` to choose exactly which names to skip:

```
tingle code_check php_complexity . --no-default-excludes --exclude .git,vendor
```

It also turns off the [`bootstrap/cache` rule](#skip-rules), so Laravel's
cached files are analysed like any other file. Blade templates stay
skipped: `--no-default-excludes` does not affect them.

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
and caches that your project already ignores.

To turn this step off and analyse ignored files too, pass `--no-gitignore`:

```
tingle code_check php_complexity . --no-gitignore
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
  `darthjee/tingle_php_complexity` image has no git, and does not need it.

### `--ignore` and `--include`

These options filter files by a glob pattern, similar to a `.gitignore`
line:

- `--ignore GLOB` skips every file that matches the glob.
- `--include GLOB` analyses **only** the PHP files that match the glob.
  Without any `--include`, every PHP file is included.

Both can be repeated. A file is skipped if it matches **any** `--ignore`
glob, and kept if it matches **any** `--include` glob.

The glob is matched against the file's path **relative to `<path>`**,
always written with `/` (for example `src/Service/InvoiceService.php` when
`<path>` is the project root). For a single-file `<path>`, it is matched
against the file name. The whole path must match, not just part of it.
Matching is case-insensitive, so `*Test.php` also matches `UserTEST.php`.

> **Quote your globs.** Write `--ignore '**/*Test.php'`, not
> `--ignore **/*Test.php`. Without quotes, your shell may expand the
> pattern into file names before `tingle` sees it.

The glob syntax is the same as for `file_size` (see
[Glob syntax](file_size.md#glob-syntax) and
[Where a pattern matches](file_size.md#where-a-pattern-matches)). In short:

- `*` matches within one path segment, `**` spans directories;
- a pattern with no `/` matches in any directory (`*Test.php` is the same as
  `**/*Test.php`);
- a pattern with a `/` is anchored at `<path>`, and a leading `/` only marks
  the anchor (`/src/*.php` is the same as `src/*.php`);
- a trailing `/` matches everything under that directory (`generated/` is
  the same as `**/generated/**`).

Combining filters:

- `--ignore` wins over `--include`: a file that matches both is skipped.
- `--include` and the `.php` extension must **both** match:
  `--include '*.phtml'` leaves nothing to analyse.
- `--include` never brings back a Blade template.
- Excluded directories (the defaults plus any `--exclude` names) are always
  skipped, whatever the globs say.

A glob that matches nothing is not an error, and an empty pattern
(`--ignore ''`) is ignored.

| Command | Effect |
| --- | --- |
| `tingle code_check php_complexity . --ignore '**/*Test.php'` | Skips every `*Test.php` file, in any directory. |
| `tingle code_check php_complexity . --ignore 'tests/**'` | Skips every file under the top-level `tests/` directory. |
| `tingle code_check php_complexity . --ignore '**/*Test.php' --ignore 'database/migrations/'` | Skips the test classes and the migrations. |
| `tingle code_check php_complexity . --include 'src/**'` | Analyses only the files under `src/`. |
| `tingle code_check php_complexity . --include 'app/**' --ignore 'app/Legacy/'` | Analyses the files under `app/`, except those under `app/Legacy/`. |

### Filter order

For a directory `<path>`, every file found below it goes through these
steps, in order. The first step that rejects a file drops it:

1. the default excludes (skipped with `--no-default-excludes`);
2. the `--exclude` names;
3. `.gitignore` (skipped with `--no-gitignore`);
4. the `--ignore` globs;
5. the `--include` globs (when given) **and** the `.php`
   [extension](#extension), in any case;
6. Blade templates, always; then the `bootstrap/cache` rule, unless
   `--no-default-excludes` (see [Skip rules](#skip-rules));
7. the symlink rule (see [Symlinks](#symlinks)).

A file dropped by any of these steps is not counted anywhere and no message
is printed.

### Single-file targets

When `<path>` is a single file, the directory excludes (the defaults and
`--exclude`) and the `bootstrap/cache` rule do not apply. The rest still
does: the file must end in `.php`, must not be a Blade template, must not be
ignored by git (unless `--no-gitignore`), and its name must pass `--ignore`
and `--include`. Otherwise there is nothing to analyse.

### Symlinks

Directory symlinks are not followed. A file symlink pointing outside
`<path>`, or whose target does not exist, is skipped silently. A file
symlink pointing inside `<path>` is analysed as its target, and is counted
only once.

### Unusual file names

Spaces, tabs and unicode in file names are fine. A file whose name contains
a newline, or whose name is not valid UTF-8, cannot be sent to the
container: it is skipped with a warning on standard error and not counted
anywhere:

```
Warning: skipping file with a newline in its name: 'src/odd\nname.php'
Warning: skipping file whose name is not valid UTF-8: 'src/caf\udce9.php'
```

### Nothing to analyse

If no file is left, the command prints the header and
`No PHP files found for analysis.`, then exits `0` without calling Docker at
all.

### Tests and generated code

Tests and generated code are analysed like any other file. Large test
classes often score a high total CCN (see
[Large test classes](#large-test-classes)), and generated code is not code
you will refactor, so you may want to leave both out:

- skip a `tests` directory wherever it is:

  ```
  tingle code_check php_complexity . --exclude tests
  ```

- skip only the top-level `tests/` directory:

  ```
  tingle code_check php_complexity . --ignore 'tests/**'
  ```

- skip test classes by name, wherever they are:

  ```
  tingle code_check php_complexity . --ignore '**/*Test.php'
  ```

- keep generated code under a default-excluded or git-ignored directory
  (such as `var/` or `build/`), or analyse only your source folder, for
  example `tingle code_check php_complexity ./src`.

## Reading the output

Sample run against a small project, with the default thresholds:

```
$ tingle code_check php_complexity fixture
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

In this project, `welcome.blade.php` is skipped (a Blade template) and
`notes.txt` is not a PHP file. Before the report, a warning for each of the
three `⛔ PARSE` files is printed on standard error:

```
Warning: cannot parse fixture/attr_anon.php: Unexpected token: #[, line: 14, col: 20
Warning: cannot parse fixture/broken.php: syntax error, unexpected token ":", expecting variable on line 10
Warning: cannot parse fixture/lenient.php: syntax error, unexpected token ";" on line 5
```

With stricter thresholds and only the files at WARN or higher, the same
project gives:

```
$ tingle code_check php_complexity fixture --warn 4 --error 6 --critical 10 --min-level warn
...
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

### Header

- `Analyzing:` shows the target as an absolute path.
- `Thresholds:` shows the `warn`, `error` and `critical` values in use.
- `Image:` shows the Docker image that runs PHP and PDepend.

### Columns

| Column | Meaning |
| --- | --- |
| `Status` | The level of the file (see [Thresholds and levels](#thresholds-and-levels)). |
| `CCN` | The file's total CCN: the sum over all its functions and methods. This is the value compared with the thresholds. |
| `Max` | The highest CCN of a single function or method in the file. Information only. |
| `NPath` | The highest NPath of a single function or method: the number of distinct paths through it. It grows very fast and can be a very large number, which is printed in full. Information only. |
| `MI` | The lowest maintainability index of a function or method in the file, rounded to a whole number. Higher is better. Information only. |
| `Lines` | The file's logical lines of code, as counted by PDepend (statements, not physical lines; top-level statements included). Information only. |
| `File` | For a directory target, the path relative to the target's parent directory, so it starts with the directory's name (`fixture/...` above). For a single-file target, only the file name. |

A `-` means the value is not available (see
[Files shown as `OK 0`](#files-shown-as-ok-0)).

### Sort order

Level rows come first, sorted by total CCN, highest first; files with the
same CCN are sorted by path. The `⛔ PARSE` rows follow, sorted by path.

### Files shown as `OK 0`

PDepend reports nothing for a file that has no class, trait or function:
empty files, files with only top-level code (`bootstrap.php` above), and
files holding only enums or interfaces. Such a file is still listed, as
`✅ OK` with a CCN of `0` and `-` in the `Max`, `NPath`, `MI` and `Lines`
columns, so the file count matches the selection.

A file with classes but no method shows `0` too, with `-` in `Max`, `NPath`
and `MI`, and its line count in `Lines`.

In rare cases the image also refuses a file it was given, for example one
deleted between the selection and the run. It prints a warning on standard
error, and the file is listed the same way, as `✅ OK` with `0`:

```
Warning: the image skipped src/gone.php: not a regular file under /src
```

### Parse errors (`⛔ PARSE` rows)

A file is a `⛔ PARSE` row when it cannot be parsed, for one of two reasons:

- **PHP rejects it**: a real syntax error. The image checks every file with
  PHP's own parser first, so even code PDepend would quietly accept (such
  as `return $x /;`) is reported. The message is PHP's, for example
  `syntax error, unexpected token ";" on line 5`.
- **PDepend rejects valid PHP**: PDepend does not support every recent
  syntax. For example, PDepend 3.0.0 fails on attributes on anonymous
  classes (`new #[Attr] class { ... }`, valid since PHP 8.0) with
  `Unexpected token: #[`. The code is fine; the analyser is behind.

Each such file prints a warning on standard error, before the report:

```
Warning: cannot parse <file>: <message>
```

It appears as a `⛔ PARSE` row, with `-` in every value column, and in the
`skipped (parse error)` count. It is never in the level counts or the `CCN:`
line, and it never changes the exit status.

When PDepend rejects valid code, a newer image may support the syntax: once
a tingle release ships a newer PDepend, update tingle, or try another image
with [`--image`](#--image).

Files that are not valid UTF-8 (for example ISO-8859-1) are analysed
normally: PHP source has no encoding requirement. Windows line endings and a
UTF-8 BOM do not change the results.

PDepend may also print a message that names no file; it is shown as
`Warning: PDepend reported: <message>` and the analysis goes on.

### Summary

- `Summary:` shows the number of selected files (`⛔ PARSE` files included)
  and how many fall into each level. Files shown as `OK 0` count as OK.
  When some files could not be parsed, `| k skipped (parse error)` is added
  at the end.
- `CCN:` shows the average and the maximum total CCN of the level rows, with
  2 decimals (`OK 0` files count with `0`, `⛔ PARSE` files are left out).
  When every file failed to parse, it shows `CCN: n/a`.

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
NO_COLOR=1 tingle code_check php_complexity ./src
```

## Examples

Analyse every PHP file under `./src` with the default settings:

```
tingle code_check php_complexity ./src
```

Use stricter thresholds:

```
tingle code_check php_complexity ./src --warn 15 --error 30 --critical 45
```

Show only the 10 most complex files at WARN or higher:

```
tingle code_check php_complexity ./src --top 10 --min-level warn
```

Analyse a single file:

```
tingle code_check php_complexity ./src/Service/InvoiceService.php
```

Skip test and fixture directories as well as the defaults:

```
tingle code_check php_complexity . --exclude tests,fixtures
```

Skip test classes, wherever they are:

```
tingle code_check php_complexity . --ignore '**/*Test.php'
```

Analyse only the files under `app/`:

```
tingle code_check php_complexity . --include 'app/**'
```

Analyse `vendor/`, `storage/` and `bootstrap/cache/` too, but still skip
`.git/`:

```
tingle code_check php_complexity . --no-default-excludes --exclude .git
```

Analyse the files git ignores too:

```
tingle code_check php_complexity . --no-gitignore
```

Run a locally built image:

```
tingle code_check php_complexity ./src --image tingle_php_complexity:dev
```

### Using in CI

Fail the build when any file under `./src` reaches the ERROR threshold:

```
tingle code_check php_complexity ./src --fail-on error
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
| Tingle version unreadable, and no `--image` | `Error: cannot read the tingle version from <file>; use --image to choose the image` | `1` |
| No PHP files to analyse | The header, then `No PHP files found for analysis.` | `0` |
| `docker` not on `PATH` | `Error: docker not found on PATH; tingle code_check php_complexity needs Docker to run PDepend` | `1` |
| Docker daemon not running (`docker info` failed or took over 30 seconds) | `Error: the Docker daemon is not responding (docker info failed); start Docker and retry` | `1` |
| Image pull failed | `Pulling <image> ...` and Docker's output, then `Error: could not pull image <image>` | `1` |
| `docker run` could not be started | `Error: could not run docker: <reason>` | `1` |
| Folder not shared with Docker Desktop | Docker's error, then `Error: Docker could not mount <folder>; on Docker Desktop, share it (or a parent folder) under Settings > Resources > File sharing, then retry` | `1` |
| PDepend or the container failed (including running out of memory) | The container's error output, then `Error: PDepend failed in <image> (exit <status>)` | `1` |
| Unexpected output from the container | The container's error output, then `Error: could not parse the output of <image>: <reason>` | `1` |
| Analysis completed, no `--fail-on` | The report | `0` |
| Analysis completed, `--fail-on` gate passed | The report | `0` |
| Analysis completed, `--fail-on` gate failed | The report | `2` |

In short:

| Code | Meaning |
| --- | --- |
| `0` | Success, nothing to analyse, or the complexity gate passed / was not requested |
| `1` | Usage error, path problem, or Docker / PDepend failure |
| `2` | The complexity gate failed (`--fail-on`) |

Unparsable files (`⛔ PARSE` rows), files shown as `OK 0` and refused-file
warnings never change the exit status on their own. The report always goes
to standard output and error messages to standard error.

## Limitations

- **Enum methods are not counted.** PDepend 3.0.0 does not attribute enum
  methods to their file, so their decisions are left out of the total CCN.
  A file holding only an enum shows `OK 0`, and a file with a class and an
  enum counts only the class.
- **Some anonymous-class methods are undercounted.** PDepend reports the
  methods of anonymous classes inconsistently: sometimes their decisions are
  folded into the enclosing method, sometimes not. Tingle never counts a
  method it cannot tie to a file, so a file that relies heavily on
  anonymous classes may score lower than it should.
- **Property hooks are not counted.** PHP 8.4 property hooks parse fine, but
  PDepend does not include their decisions in any CCN. The file is not a
  `⛔ PARSE` row; its hooks simply add nothing.
- **Some valid PHP is a `⛔ PARSE` row.** Syntax PDepend does not support yet,
  such as attributes on anonymous classes, cannot be analysed (see
  [Parse errors](#parse-errors--parse-rows)).
- **Podman is not supported.** It may work when aliased as `docker`, but
  this is not tested.
- **No Docker-in-Docker.** The `darthjee/tingle` container (used by
  [`tingle linux`](../linux.md)) has no `docker` command, so running this
  subcommand inside it fails with `docker not found on PATH`. Run it on a
  host with Docker.
- **Tests and generated code are analysed** unless they are left out by the
  selection rules (see [Tests and generated code](#tests-and-generated-code)).
- **No configuration file yet.** Unlike `file_size`, `rubycritic` and
  `js_complexity`, this subcommand does not read
  `~/.tingle/code_check/config.json` yet: pass the options on the command
  line.

## Quick help

For a short summary of the command's options, run:

```
tingle code_check php_complexity --help
```

`tingle --help code_check` shows the options of every `code_check`
subcommand, together with their list.
