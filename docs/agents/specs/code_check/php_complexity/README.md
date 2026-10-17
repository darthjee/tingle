# Specs: `tingle code_check php_complexity`

Parent issue: #344. Specs sub-issue: #345. This file holds the **shared
contracts**, meaning everything that more than one sub-issue depends on. Each
feature spec is readable on its own, but it must not contradict this file. If
they disagree, this file wins and the feature spec must be fixed.

These specs are normative and take precedence over the bodies of #344 and of
the sub-issues #346 to #353. Every place where they change #344 is listed in
[section 11](#11-deviations-from-344).

## 1. Overview

`tingle code_check php_complexity <path>` measures the complexity of PHP
code. Tingle selects the files on the host, then runs pinned tools inside the
published Docker image `darthjee/tingle_php_complexity`:

- [PDepend](https://pdepend.org/) is the **only analyser** for the score and
  the drill-down. Its `--summary-xml` report gives `ccn`, `ccn2`, `npath`,
  `lloc` and a maintainability index (`mi`) for every function and method.
  The level of a file comes from its **total CCN**: the sum of `ccn` over
  every function and method PDepend attributes to the file.
- PHP's own parser (the image's PHP 8.5, through `token_get_all(...,
  TOKEN_PARSE)`) decides which files are syntax errors before PDepend runs
  (deviation 1).
- [jscpd](https://github.com/kucherenko/jscpd) adds duplication data (the
  `Dup` column, #352).

The host needs Docker, but no PHP and no Composer. The report has the same
layout as `file_size`, `rubycritic` and `js_complexity`: one row per file,
levels from numeric thresholds on the total CCN, and a summary with the
average and maximum total CCN.

The contracts in these specs come from a real run of the pinned versions
(`php:8.5.11-cli-trixie`, PDepend `3.0.0`, jscpd `5.4.1`) on the fixture
listed in [image.md](image.md#9-smoke-test-fixture), and from a calibration
run on three public codebases ([section 3](#thresholds-and-calibration)).
They are not based on assumptions. The commands, versions and raw output of
the grounding run are in [image.md](image.md#10-grounding-run).

| Spec | Implemented by | Covers |
|------|----------------|--------|
| [README.md](README.md) | all | The shared contracts (this file). |
| [image.md](image.md) | #346 | Dockerfile and pins, the entrypoint contract, staging, the PDepend options, the XML → JSON mapping, refused lines, the fixture, the grounding run. |
| [release.md](release.md) | #347 | The `php_complexity` selector of `scripts/release_image.sh`, `smoke_test_php_complexity`, the CircleCI jobs, the Docker Hub descriptions, `docs/agents/tingle-php-complexity-image.md`. |
| [cli.md](cli.md) | #348 | The package on top of `docker_check`, flags, levels, JSON parsing, the report and summary, `--fail-on`, `PARSE` rows, edge cases, messages, registration, help and completion. |
| [selection.md](selection.md) | #349 | The selection flags, the filter order, the Blade and `bootstrap/cache` skip rules, `.gitignore`. |
| [config.md](config.md) | #350 | `SCHEMA`, precedence, list merging, error messages. |
| [details.md](details.md) | #351 | `--details`, the `functions` key, the line format, ordering and tie-breaks. |
| [duplication.md](duplication.md) | #352 | The jscpd pin and options, the `duplication` key, the `Dup` column, degraded mode. |

There is no `docker-check.md`: the shared `python/code_check/docker_check/`
module already exists (#317) and is used as it is. There is no `sfc.md`: PHP
has no single-file components.

## 2. Sub-issues and merge order

| Sub-issue | What | Spec | Depends on |
|---|---|---|---|
| #345 | Specs (this issue) | — | — |
| #346 | Image `docker/php_complexity/`, PDepend only | [image.md](image.md) | #345 |
| #347 | Release pipeline for `darthjee/tingle_php_complexity` | [release.md](release.md) | #346 |
| #348 | Subcommand core | [cli.md](cli.md) | #345 (local image from #346) |
| #349 | File selection flags | [selection.md](selection.md) | #348 |
| #350 | Config section `php_complexity` | [config.md](config.md) | #349 |
| #351 | `--details` drill-down | [details.md](details.md) | #347, #350 |
| #352 | Duplication via jscpd | [duplication.md](duplication.md) | #347, #348 |
| #353 | Cleanup: remove the specs | — | #345–#352 |

**Merge order**

- After #345, two tracks run in parallel: the image track #346 → #347, and
  the Python track #348 → #349 → #350.
- #347 must be merged before the tingle tag that ships #348 is pushed.
  Otherwise the CLI would default to an image tag that was never published.
  #348 may merge to `main` earlier, as long as no release tag is pushed in
  between.
- #351 and #352 each change the image **and** the Python side in the same
  PR. The image and the CLI are always released under the same tingle tag, so
  they stay in sync.
- #353 merges last. It removes `docs/agents/specs/code_check/php_complexity/`
  (and `docs/agents/specs/code_check/` if it is then empty) and the row in
  [`docs/agents/specs.md`](../../../specs.md).

For manual end-to-end tests before #347, #348 uses a local build from #346
through `--image tingle_php_complexity:dev` (`make php-complexity-image`).

## 3. CLI and flags

```
tingle code_check php_complexity <path> [options]
```

There is no `--ext` flag and no `ext` config key: the extension is fixed
(section 4).

| Flag | Type | Repeatable | Default | Added by | Config key (type) |
|------|------|------------|---------|----------|-------------------|
| `path` (positional) | str | no | required | #348 | none |
| `--warn N` | number ≥ 0 (float) | no | `20` | #348 | `warn` (number ≥ 0) |
| `--error N` | number ≥ 0 (float) | no | `40` | #348 | `error` (number ≥ 0) |
| `--critical N` | number ≥ 0 (float) | no | `60` | #348 | `critical` (number ≥ 0) |
| `--top N` | int ≥ 0 | no | `0` (all) | #348 | `top` (int ≥ 0) |
| `--min-level LEVEL` | `ok\|warn\|error\|critical` | no | `ok` | #348 | `min_level` (str) |
| `--fail-on LEVEL` | `warn\|error\|critical` | no | none (no gate) | #348 | `fail_on` (str or `null`) |
| `--image IMAGE` | str (non-empty) | no | `darthjee/tingle_php_complexity:<tingle version>` | #348 | `image` (non-empty str) |
| `--exclude a,b` | comma-separated str | no | none (adds to the default excludes) | #349 | `exclude` (list of str) |
| `--no-default-excludes` | `store_true` | no | off | #349 | `no_default_excludes` (bool, default `false`) |
| `--no-gitignore` | `store_true` | no | off | #349 | `gitignore` (bool, default `true`, the inverse of the flag) |
| `--ignore GLOB` | str | yes (`append`) | `[]` | #349 | `ignore` (list of str) |
| `--include GLOB` | str | yes (`append`) | `[]` | #349 | `include` (list of str) |
| `--no-config` | `store_true` | no | off | #350 | none (the config file is not read or validated) |
| `--details [N]` | int ≥ 0, optional value | no | off; `5` when given without `N`; `0` = all | #351 | `details` (int ≥ 0 or `null`) |

- The flag names, meanings and argparse style are `js_complexity`'s
  (`python/code_check/js_complexity/flags.py`). Single-value flags default to
  `None` in `FLAGS`, and the built-in default is filled in after merging with
  the config. The help text still shows the built-in default.
- `--warn`, `--error` and `--critical` apply to the file's **total CCN**
  (see [cli.md](cli.md#2-flags-and-levels)). They use `type=float`, so
  decimals are allowed; a negative value is a usage error (exit 1). The total
  CCN is an integer, so no rounding is involved.
- `--top`, `--min-level` and `--details` only change the display. The
  summary and the `--fail-on` gate always count every selected file.
- Choice-valued flags use argparse `choices`. Argparse's exit 2 is remapped
  to 1, as in `rubycritic` and `js_complexity`.
- The precedence rules (CLI over config for single values, concatenation for
  lists) are in [config.md](config.md#3-precedence).
- `Max`, `NPath`, `MI`, `Lines`, `Dup` and the per-function data are
  information only. They never set a level and never change the exit status.

### Thresholds and calibration

The defaults `warn=20 | error=40 | critical=60` from #344 are **kept**. They
were checked with the pinned PDepend through the staged-copy flow
([image.md](image.md#5-parse-check-and-staged-tree)) on three shallow clones, selected the
way #348 and #349 select files (`.php` only, `*.blade.php` skipped, the
default excludes and the `bootstrap/cache` rule applied; tests included,
because a user running `tingle code_check php_complexity .` sees them too).
The total CCN follows section 1: top-level code counts 0, and methods
PDepend reports without a file are not counted (deviation 7).

| Codebase | Commit | Files | Parse errors | `< 20` (OK) | `20–40` (WARN) | `40–60` (ERROR) | `≥ 60` (CRITICAL) | p50 | p90 | p99 | Max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `laravel/framework` | `e51b5fe` | 3028 | 2 | 82.5% | 9.5% | 3.1% | 5.0% | 5 | 32 | 164 | 494 |
| `symfony/console` | `6b6e903` | 382 | 1 | 80.1% | 11.5% | 4.5% | 3.9% | 5 | 35 | 115 | 290 |
| `bcit-ci/CodeIgniter` (3.x, legacy style) | `3658d73` | 282 | 0 | 69.1% | 13.8% | 8.9% | 8.2% | 9 | 54 | 187 | 304 |

The percentages are over the files with a score (parse errors left out).
The parse errors are, in Laravel, `tests/Foundation/Fixtures/bad-syntax-strategy.php`
(an intentional syntax error, rejected by PHP: `Unmatched ')' on line 3`) and
one file PDepend rejects (deviation 2); in Symfony Console, one file PDepend
rejects (deviation 2). Laravel took 40 s and PDepend reported a peak of
2,047 MB of memory (PDepend lifts PHP's `memory_limit` itself).

Why `20/40/60` stays:

- Most files are `OK` in every codebase (69–83%), so `WARN` is not noise.
- `ERROR` and `CRITICAL` are reached, but rarely in the modern codebases (8%
  `ERROR` or worse in Laravel and Symfony Console) and more in the legacy one
  (17%), which is the signal a complexity check should give.
- The files that land in `CRITICAL` are the expected ones: Laravel's
  `src/Illuminate/Database/Query/Builder.php` (493), Symfony's
  `Application.php` (290) and `Helper/Table.php` (179), CodeIgniter's
  `system/database/DB_query_builder.php` (304) and `system/libraries/Email.php`
  (248).
- Lower alternatives flag too much (`10/25/50` puts 33–49% of the files at
  `WARN` or above); higher ones (`30/60/100`) leave only 1–4% `CRITICAL` and
  hide the 40–60 band.

The total CCN of a large test class can be high while every method is simple
(Laravel's `tests/Database/DatabaseQueryBuilderTest.php`: total 494, highest
method 1). That is a property of a per-file total (like Flog's total in
`rubycritic`); the `Max` column shows it, and the guide documents `--ignore`
for tests.

## 4. Extensions

Matching is on the file name, case-insensitive, as in `file_size`'s
`FileCollector` (`path.suffix.lower()`): `UPPER.PHP` is analysed.

| Rule | Names | Added by | Turned off by |
|------|-------|----------|---------------|
| Extension (analysed) | `.php` | #348 | never |
| Blade templates (always skipped) | names ending in `.blade.php` (case-insensitive) | #348 | never (not even `--no-default-excludes`) |

- `.phtml`, `.inc` and the legacy `.php3`–`.php8` are not analysed.
- `--include` only ever narrows the selection. It never brings back a Blade
  template.
- The same rules apply to a single-file `<path>`: a `*.blade.php` or a
  non-`.php` file leaves nothing to analyse (exit 0).
- Skipping is the host's job, but the image also refuses a `*.blade.php`
  line (defence in depth, message `Blade template`, see
  [image.md](image.md#4-entrypoint-input)). Without that rule, PDepend would
  read a Blade file as inline HTML and report nothing for it (checked in the
  grounding run).
- Details: [selection.md](selection.md#2-extensions-and-skip-rules).

## 5. Default excludes

`file_size`'s `Constants.DEFAULT_EXCLUDES` plus three PHP directories, in
this order (16 names):

```
node_modules, dist, build, .git, vendor, third_party, .next, __pycache__,
.cache, coverage, .nuxt, out, target, var, storage, .phpunit.cache
```

`vendor` is already in `file_size`'s list. The names are matched against
path components, case-insensitively, as in `file_size`.

**`bootstrap/cache`** (Laravel's cached config, routes and services) is also
excluded by default, but it spans two path components, which the
component-name excludes cannot express (deviation 11). It is a **skip rule**
instead: a file is skipped when two consecutive components of its path
relative to `<path>` are `bootstrap` then `cache` (case-insensitive).

`--no-default-excludes` drops all of them, the `bootstrap/cache` rule
included. See [selection.md](selection.md#3-default-excludes).

## 6. Filter order

For a directory `<path>`, every regular file found by the walk goes through
these steps in this order. The first step that rejects a file drops it.

1. Default excludes (skipped with `--no-default-excludes`).
2. `--exclude` names.
3. `.gitignore` (skipped with `--no-gitignore`).
4. `--ignore` globs.
5. `--include` globs and the extension: when `--include` is given the path
   must match one include glob, **and** the extension must be `.php`.
6. Skip rules: Blade templates (always), then `bootstrap/cache` (unless
   `--no-default-excludes`).
7. Symlink confinement: a file resolving outside the mount root is dropped.

After the filters, tingle drops the file names that cannot be sent on stdin
(a newline, or not valid UTF-8). #348 ships steps 1, 5 (the extension only),
6 and 7; #349 adds steps 2 to 4 and the `--include` part of step 5. For a
single-file `<path>`, steps 1, 2 and the `bootstrap/cache` rule do not apply.
See [selection.md](selection.md#5-filter-order).

## 7. Config keys

The `php_complexity` section of `~/.tingle/code_check/config.json` accepts
these keys, and no others:

| Key | Validator (`code_check.validators`) | Added by |
|-----|-------------------------------------|----------|
| `warn`, `error`, `critical` | `non_negative_number` | #350 |
| `top` | `non_negative_int` | #350 |
| `exclude`, `ignore`, `include` | `list_of_str` | #350 |
| `no_default_excludes`, `gitignore` | `boolean` | #350 |
| `fail_on` | `one_of(["warn", "error", "critical"], nullable=True)` | #350 |
| `min_level` | `one_of(["ok", "warn", "error", "critical"])` | #350 |
| `image` | `non_empty_str` | #350 |
| `details` | `nullable_non_negative_int` | #351 |

`ext` is an unknown key (`unknown key 'ext'`, exit 1). The rules are
`js_complexity`'s. The schema, precedence and error handling are in
[config.md](config.md).

## 8. Exit codes and streams

| Code | Meaning |
|------|---------|
| `0` | Success, including "no file selected" (no container started) and "no rows at this level". `PARSE` rows, refused lines and jscpd warnings never change the exit code. |
| `1` | Error: bad option or value, `<path>` missing or unreadable, config error, `docker` not found, Docker daemon not responding, image pull failure, mount failure, container, entrypoint or PDepend failure, unparsable container output. |
| `2` | The `--fail-on` gate failed. Only `--fail-on` exits 2. |

- The report goes to stdout, including the yellow
  `No PHP files found for analysis.` line.
- Errors (`Error: <message>`, red, then exit 1), warnings
  (`Warning: <message>`, yellow) and the dim `Pulling <image> ...` line go
  to stderr, in `js_complexity`'s style. The Docker messages are produced by
  the shared `docker_check` package with `command="tingle code_check
  php_complexity"` and `tool="PDepend"`.
- The container's stderr (PDepend's and jscpd's own output included) is
  discarded on success and passed through to stderr on any failure.
- A jscpd failure is never fatal: the report is printed from PDepend's data,
  and one warning naming jscpd goes to stderr. Only a PDepend (or entrypoint)
  failure is fatal.
- Colours only appear on a TTY when `NO_COLOR` is not set (`Palette`).
- The exact message texts are in [cli.md](cli.md#10-messages),
  [duplication.md](duplication.md#5-failure-handling) and
  [config.md](config.md#5-error-handling).

## 9. Image contract summary

- **Image:** `darthjee/tingle_php_complexity`. The default tag is the tingle
  version: the content of `shell/linux/VERSION` with all whitespace removed.
  Every tingle release tag `X.Y.Z` publishes
  `darthjee/tingle_php_complexity:X.Y.Z` (one amd64 + arm64 manifest, no
  `latest`). See [release.md](release.md).
- **Run line** (`docker_check.DockerRunner.run_args`, unchanged, also used by
  the smoke test):

  ```
  docker run --rm -i --pull never --network none --security-opt no-new-privileges \
    --user <uid>:<gid> -v <root>:/src:ro -w /src <image>
  ```

  `<root>` is the resolved `<path>` for a directory, or its parent directory
  for a single file.
- **stdin:** the selected files, one path per line, relative to `<root>`,
  UTF-8, POSIX separators, each line ending in `\n`, sorted.
- **Parse check:** each accepted file is parsed by PHP's own parser first; a
  file it rejects is a parse error and is never staged. See
  [image.md](image.md#5-parse-check-and-staged-tree).
- **Tool input:** the entrypoint **copies** (never symlinks) each accepted
  line `<n>` (1-based stdin line number) to `/tmp/stage/<n>.php`, runs
  PDepend (and later jscpd) on `/tmp/stage`, never on `/src`, and maps the
  results back by `<n>`, never by stripping a prefix. This avoids
  argument-length limits and PDepend's built-in suffix and directory filters
  (case-sensitive `php,php5`; `.git`, `.svn`, `CVS` ignored).
- **stdout:** exactly one JSON document, the **merged JSON** (below).
- **stderr:** everything else, including PDepend's and jscpd's own output.
- **Exit status:** 0 when the JSON was printed; non-zero when PDepend fails
  or the entrypoint fails, with nothing on stdout. A jscpd failure is
  reported in `warnings` and does not change the exit status.
- **No git, no Composer and no Node** in the final image.

### Merged JSON summary

The full definition is in [image.md](image.md#7-merged-json). The rules
every sub-issue relies on:

- **Fixed shape from day one.** #346 already emits every key below. #351 and
  #352 only fill in their parts (`functions`, `duplication`,
  `tool_versions.jscpd`); they never add or rename a key.
- **No version field and no negotiation.** The image and the CLI are always
  released under the same tingle tag. A key that is missing, or of the wrong
  type, is an unparsable-output error (exit 1). Unknown extra keys are
  ignored.
- **One entry per stdin line, in stdin order**, even for parse errors and
  refused lines.
- **`null` means not available; `[]` or `0` means available and empty.**
  `Dup` shows `-` for `null` and `0` for 0; `--details` shows
  `(per-function data unavailable)` for `null` and nothing for `[]`.

```json
{
  "tool_versions": {"php": "8.5.11", "pdepend": "3.0.0", "jscpd": null},
  "files": [
    {
      "path": "Calculator.php",
      "parse_error": false,
      "pdepend": {"ccn": 11, "max_ccn": 7, "max_npath": 36, "min_mi": 53.875623305512, "lloc": 22},
      "functions": null,
      "duplication": null
    },
    {"path": "bootstrap.php", "parse_error": false, "pdepend": null, "functions": null, "duplication": null},
    {"path": "broken.php", "parse_error": true, "pdepend": null, "functions": null, "duplication": null}
  ],
  "warnings": [
    {"tool": "php", "path": "broken.php", "message": "syntax error, unexpected token \":\", expecting variable on line 10"}
  ]
}
```

| Key | Type | `null` when |
|-----|------|-------------|
| `tool_versions.php` | str | never |
| `tool_versions.pdepend` | str | never |
| `tool_versions.jscpd` | str or `null` | always before #352 |
| `files[].path` | str | never (the stdin line, as received) |
| `files[].parse_error` | bool | never |
| `files[].pdepend` | object or `null` | parse error, refused line, or PDepend reported nothing for the file (no class, trait or function) |
| `files[].pdepend.ccn` | int ≥ 0 | never (the total CCN) |
| `files[].pdepend.max_ccn` | int ≥ 1 or `null` | the file has no counted function or method |
| `files[].pdepend.max_npath` | int ≥ 1 or `null` | likewise |
| `files[].pdepend.min_mi` | number or `null` | likewise |
| `files[].pdepend.lloc` | int ≥ 0 | never |
| `files[].functions` | list or `null` | always before #351; parse error, refused line |
| `files[].duplication` | `{"lines": int ≥ 0}` or `null` | always before #352; parse error, refused line, file over 1 MiB, jscpd failure |
| `warnings[]` | `{"tool": "entrypoint" \| "php" \| "pdepend" \| "jscpd", "message": str, "path": str (optional)}` | — |

After #351 and #352 the parts are filled in, for example
`"functions": [{"name": "Calculator::grade", "line": 22, "ccn": 7, "npath": 36}]`
and `"duplication": {"lines": 13}`.

Per-file states:

| `parse_error` | `pdepend` | Report |
|---|---|---|
| `false` | object | normal row (CCN = `pdepend.ccn`) |
| `true` | `null` | `⛔ PARSE` row |
| `false` | `null` | no class, trait or function reported, or refused by the entrypoint → `OK`, CCN 0, `-` elsewhere |

## 10. Pinned tools

| Component | Version | Added by | Pinned by |
|-----------|---------|----------|-----------|
| PHP (base image) | `php:8.5.11-cli-trixie` (Debian 13.7 "trixie" slim base, PHP 8.5.11), index digest `sha256:01a109229f4465bc9ef042d9198f09a4d9da7775a825dbd8572dcdbd8756c4d3` | #346 | `ARG BASE_IMAGE` with the index digest |
| Composer (build only) | `composer:2.10.3`, index digest `sha256:af98f42dfff7c68ba8d53c2164fd9fde1087b7d449514baa38c418b1f6bc4bac` | #346 | `ARG COMPOSER_IMAGE` with the index digest |
| PDepend | `3.0.0` (released 2026-09-29; the latest stable) | #346 | `docker/php_complexity/composer.json` (`"pdepend/pdepend": "3.0.0"`) + `composer.lock` |
| Node (build only) | `node:24.21.0-slim`, index digest `sha256:d6aa754f16b3197301076f047b5def2f02ea1dbbc2ca920407d46d7ec7f87b20` (the same as `docker/js_complexity/`) | #352 | `ARG NODE_IMAGE` with the index digest |
| jscpd | `5.4.1` (the same as `docker/js_complexity/package.json`), native binary from `jscpd-linux-x64-gnu` / `jscpd-linux-arm64-gnu` `5.4.1` | #352 | `docker/php_complexity/package.json` + `package-lock.json` |

- Every index resolves on `linux/amd64` and `linux/arm64/v8`. The Debian
  variant was chosen over Alpine: both have arm64 builds, the Debian one is
  the default `php:8.5-cli` variant, and jscpd's native binaries are glibc
  (`-gnu`) builds.
- PHP 8.5.11 is the latest PHP release; there is no `php:8.6-cli`. The base
  image has no `-slim` tag: its CLI variant is itself built on
  `debian:trixie-slim`.
- Node is **not** in the final image: it only runs `npm ci` in a build stage
  that extracts jscpd's native binary (deviation 13).

Every option that affects the results is pinned in the entrypoint and
recorded in the spec of the sub-issue that adds the tool
([image.md](image.md#6-pdepend-invocation),
[duplication.md](duplication.md#2-jscpd-invocation)). Changing one is a
deliberate change, the same as a version bump.

## 11. Deviations from #344

The grounding run **confirmed** these decisions of #345 and #344:

- **Top-level code counts 0.** PDepend gives top-level code no CCN at all:
  top-level `if`/`foreach` statements and top-level closures and arrow
  functions are not reported (`bootstrap.php`, `helpers.php` in the
  fixture). Closures inside a function or method count toward it. A file's
  total CCN is the sum of `ccn` over its functions and methods only.
- **Staged copies.** PDepend run on the unstaged fixture tree silently
  dropped `UPPER.PHP` (its suffix filter is case-sensitive, default
  `php,php5`) and every file under `CVS/` (its default ignore list is `.git`,
  `.svn`, `CVS`). Staged as `/tmp/stage/<n>.php`, both were analysed. The
  comma-separated source paths mentioned in #344 are not used.
- **The `MI` column stays.** PDepend 3.0.0's summary XML has a per-method and
  per-function `mi` attribute, so decision 3 of #345 (drop `MI` when there is
  none) does not apply. Nothing is computed by tingle.
- **The `20/40/60` defaults stay** (section 3).
- Several classes, traits and functions in one file all add up (`Shapes.php`:
  two classes and a trait, total 6). Mixed HTML/PHP is parsed and the inline
  HTML is not counted (`page.php`). PHP 8.3 syntax (an enum, a readonly class,
  a typed class constant) parses.

Each item below changes #344's body or a sibling issue body. Each resolution
is binding. "Grounding" means the run recorded in
[image.md](image.md#10-grounding-run).

1. **PHP's parser decides parse errors, not only PDepend** (#346, #348,
   [image.md](image.md#5-parse-check-and-staged-tree)). #344: "a file PDepend can't parse is
   shown as a `⛔ PARSE` row". Grounding: PDepend 3.0.0 accepted
   `return $x /;` (`lenient.php`) without any message and reported metrics
   for it. **Resolution:** the entrypoint runs `token_get_all($code,
   TOKEN_PARSE)` on each accepted file first; a `ParseError` makes the file a
   parse error (`tool: "php"` warning) and it is not staged. A file PHP
   accepts but PDepend rejects is a parse error too (item 3).
2. **PDepend rejects some valid PHP** (#346, #348). #344 edge case 6 expects
   only "new syntax". Grounding: PDepend 3.0.0 fails on attributes on
   anonymous classes (`new #[Attr] class { ... }`, valid since PHP 8.0) with
   `Unexpected token: #[`. Calibration: one such file in `symfony/console`
   and one in `laravel/framework`. **Resolution:** such files are `PARSE`
   rows with a `tool: "pdepend"` warning; the guide says so and suggests a
   newer image through `--image` once PDepend supports the syntax.
3. **Parse errors are on stdout, PDepend exits 0, and keeps partial data**
   (#346). Grounding: PDepend prints `The following error occurred:` (or
   `errors occurred:`) on **stdout**, one line per file, each followed by a
   stack trace, exits 0, and still writes the broken file's classes into the
   XML with `start="0"`, `mi="0"` and `NAN` Halstead values (plus PHP
   `Warning: unexpected NAN value was coerced to string` lines on stdout).
   **Resolution:** the entrypoint reads that block from PDepend's stdout,
   marks those files as parse errors and discards all their XML data. See
   [image.md](image.md#6-pdepend-invocation).
4. **PDepend exits 0 when it cannot write the report** (#346). Grounding:
   with an unwritable `--summary-xml` path it printed a PHP warning and
   exited 0. **Resolution:** the entrypoint deletes the report path before
   the run, and a missing or malformed report is an entrypoint failure
   (exit 1).
5. **The XML carries no PDepend version** (#346). Grounding: the root
   element has `pdepend="@package_version@"` (the Composer install has no
   build-time version). **Resolution:** `tool_versions.pdepend` comes from
   Composer's runtime API,
   `Composer\InstalledVersions::getPrettyVersion('pdepend/pdepend')`
   (`"3.0.0"`).
6. **Files with no class, trait or function are absent from the XML** (#346,
   #348). #344 edge case 3 expects such files "reported with the CCN the
   specs decide". Grounding: PDepend omits them from `<files>` entirely, so
   there is no `lloc` either: top-level-only files (`bootstrap.php`), empty
   files, Blade-like markup, and files holding only enums or interfaces.
   **Resolution:** their entry has `pdepend: null`; tingle shows them as
   `OK` with CCN 0 and `-` in `Max`, `NPath`, `MI` and `Lines`, so the file
   count still matches the selection.
7. **Enum methods are not counted, and some anonymous-class methods neither**
   (#346, #348). Grounding: PDepend 3.0.0 has no enum visitor in its summary
   report, so enum methods appear as bare `<method>` elements directly under
   `<package>`, with no `<file>` (`Suit::color` in `Modern.php`). Some
   anonymous-class methods appear the same way. Anonymous-class methods are
   reported inconsistently: depending on the case their decisions are folded
   into the enclosing method's `ccn` or not, and a bare copy may or may not
   be emitted (`Anon.php`: `make` ccn 2 without the bare `label`'s
   decision; a probe: folded **and** bare; see
   [image.md](image.md#10-grounding-run)). Calibration: 572 bare methods in
   `laravel/framework`, 107 in `symfony/console`.
   **Resolution:** bare `<method>` elements are never counted: they cannot be
   mapped to a file, and counting them could count a decision twice. A file
   whose only methods are enum methods has total CCN 0. The guide documents
   the enum undercount. No warning is printed (it would fire on most modern
   codebases).
8. **Property hooks are parsed but not counted** (#346). Grounding: a PHP
   8.4 property hook with a ternary parsed, but its class had `nom="0"` and
   the hook's decision was in no `ccn`. **Resolution:** accepted as a
   PDepend limitation, documented in the guide; not a `PARSE` row.
9. **`Lines` is PDepend's file `lloc`** (#348). It is the logical lines of
   code of the whole file (top-level statements included), not physical
   lines, from the file's `<files>` entry. Tingle never recounts. It is `-`
   for the files of item 6.
10. **`NPath` can exceed 2^53** (#348). PDepend computes NPath with PHP
    64-bit integers (calibration maximum: 5,200,588,800 in CodeIgniter).
    **Resolution:** `max_npath` is a JSON integer of any size, and the
    column prints it in full (`{:>7}` is a minimum width).
11. **`bootstrap/cache` is a skip rule, not an exclude name** (#348, #349).
    #344 lists it with the directory excludes, but `file_size`'s
    `FileCollector` matches excludes against single path components.
    **Resolution:** the default excludes are 16 component names (section 5;
    `vendor` was already in `file_size`'s list) and `bootstrap/cache` is a
    skip rule on two consecutive components, dropped by
    `--no-default-excludes` like the excludes. `--exclude bootstrap/cache`
    matches nothing; `--exclude cache` excludes every `cache` directory.
12. **Composer runs in its own build stage** (#346). Grounding:
    `composer require` inside the PHP base image fails (`The zip extension and
    unzip/7z commands are both missing`). **Resolution:** a
    `composer:2.10.3` stage installs the locked vendor tree, which the final
    stage copies. The final image has no Composer, zip or unzip.
13. **Node is build-only** (#352, [duplication.md](duplication.md)). #344:
    "adds Node and a pinned jscpd to the image". Grounding: jscpd 5.4.1's npm
    package is a Node launcher around a native binary
    (`jscpd-linux-<arch>-gnu/bin/jscpd`), which runs on its own (it links
    only against glibc) and gave the same report. **Resolution:** a pinned
    `node:24.21.0-slim` stage runs `npm ci` and the final image gets only
    `/usr/local/bin/jscpd`. `tool_versions.jscpd` comes from
    `jscpd --version` (`jscpd 5.4.1`).
14. **The `CRITICAL` label** (#348). #344's example shows `🚨 CRITICAL`.
    **Resolution:** reuse `file_size`'s labels (`🟣 CRITICAL`), as
    `rubycritic` and `js_complexity` do.
15. **The `--details` line layout** (#351, [details.md](details.md#4-report)).
    #344's example (`ccn 19  InvoiceService::reconcile   (L210)`) is replaced
    with `js_complexity`'s layout, with `npath` in place of `sloc`:
    `ccn   7  npath      36  Calculator::grade  (fixture/Calculator.php:22)`.
