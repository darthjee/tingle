# Issue: code_check php_complexity: write specs in docs/agents/specs/code_check/php_complexity/

## Description
Write the specs for the new `tingle code_check php_complexity <path>` subcommand (parent #344). The subcommand measures PHP code complexity by running [PDepend](https://pdepend.org/) inside a published Docker image, `darthjee/tingle_php_complexity`. [jscpd](https://github.com/kucherenko/jscpd) adds duplication data later (#352). It mirrors `tingle code_check rubycritic` (#290) and `tingle code_check js_complexity` (#315).

The specs go under `docs/agents/specs/code_check/php_complexity/`, and `docs/agents/specs.md` indexes them. They are temporary: #353, the last sub-issue of #344, removes them once everything has landed.

## Problem
#344 is split into this specs sub-issue (#345), seven implementation sub-issues (#346–#352) and a cleanup (#353):
- the image, PDepend only (#346), and its release pipeline (#347)
- the subcommand core (#348), the file selection flags (#349), the config section (#350), the `--details` drill-down (#351), and duplication via jscpd (#352)

Several of them share contracts:
- the CLI and flag names
- the config keys
- the image stdin/stdout contract and the merged JSON shape
- the PDepend fields used
- exit codes

Without one agreed, normative source, the image track and the Python track would drift apart. The PDepend output shape that #344 relies on (the `--summary-xml` per-file/class/method metrics) has also not been checked against real output yet.

## Expected Behavior
### Check the real tool output first
**Pins.** Pick and pin these first; `README.md` §10 records them:
- **Base image:** the latest `php:<8.x>-cli` slim variant, as tag plus digest. Choose Debian or Alpine according to arm64 support.
- **PDepend:** the latest stable release, through `composer.json`/`composer.lock`.
- **jscpd (#352):** the same version `docker/js_complexity/` already pins, so the two images stay aligned.

**Fixture.** Build a small fixture that #346 reuses as `docker/php_complexity/fixture/`, its smoke fixture. It contains:
- a class with a few methods of varying CCN
- several classes in one file
- plain functions
- a file with top-level code only
- a mixed HTML/PHP file
- an empty file
- a file with a syntax error
- a file using PHP 8.3 syntax (enums, readonly classes)
- a `*.blade.php` file
- two files that share a duplicated block

**Run it.** Run the pinned PDepend (with `--summary-xml`) and jscpd in the pinned base image on the fixture, then record:
- the exact XML elements and attributes used: `ccn`, `ccn2`, `npath`, `lloc`, the maintainability index if there is one, and the file/class/method/function nesting
- how parse errors show up (XML vs. stderr, and the exact message format)
- how files with top-level code only, or empty files, show up
- jscpd's clone report fields for PHP

The specs include **trimmed real excerpts** of PDepend's XML and stderr and of jscpd's JSON, plus the exact commands and versions, so anyone can reproduce them. Nothing else is committed.

**Calibrate the thresholds.** Run the pinned PDepend on 2–3 real public codebases, e.g. `laravel/framework` and `symfony/console`, plus one legacy-style project. Record how the files spread across `20/40/60`, and adjust the defaults if most files land in WARN or above. The specs state the chosen defaults and why.

If real output contradicts an assumption in #344, list it explicitly in a "Deviations from #344" section. Never drop it silently.

### Decisions (confirmed or overturned by real output)
The specs start from these decisions. If real output makes one of them unworkable, they record the change under "Deviations from #344".
1. **Top-level code counts as 0.** The file's CCN is the sum of `ccn` over its functions and methods only. A file with no functions or methods scores 0 and is `OK`. A base of 1 per file was rejected because it would only shift every file up by 1 and make the thresholds harder to reason about. The specs record what PDepend actually reports for top-level code.
2. **The file list reaches PDepend through staged copies.** The entrypoint copies (never symlinks) each accepted line `<n>` to `/tmp/stage/<n>.php`, runs PDepend on `/tmp/stage`, and maps the results back by `<n>`, never by stripping a prefix. This is the same approach js_complexity uses. It avoids argument-length limits, gets around PDepend's own suffix and ignore filters, and makes mapping back unambiguous. Passing a comma-separated list of source paths was rejected.
3. **No invented maintainability index.** If PDepend's summary XML has no per-method maintainability index, the specs **drop the `MI` column** and record it as a deviation. Computing MI in the image (from Halstead volume, CCN and lloc) was rejected, because it is extra code tingle would own.

### What the specs must pin down
Add a shared `README.md` for the contracts used by more than one sub-issue, plus one spec per concern:
- **CLI:** `tingle code_check php_complexity <path>`.
  - `--warn/--error/--critical`: numbers ≥ 0, defaults `20/40/60` (subject to calibration), applied to the file's **total CCN** (the sum of `ccn` over every function and method in the file).
  - Display flags: `--top`, `--min-level`.
  - `--fail-on`: exits 2.
  - `--image`.
  - Selection flags: `--exclude`/`--no-default-excludes`, `--ignore`, `--include`, `--no-gitignore`.
  - `--no-config`.
  - `--details [N]`: `5` when given alone, `0` means all.
  - There is no `--ext`.
- **Extensions:** `.php` only, matched regardless of case. `*.blade.php` is always skipped.
- **Default excludes:** `file_size`'s `DEFAULT_EXCLUDES` plus `vendor`, `var`, `storage`, `bootstrap/cache` and `.phpunit.cache`.
- **Config:** the `php_complexity` section and its keys, the same as `js_complexity`'s (`warn`, `error`, `critical`, `top`, `exclude`, `ignore`, `include`, `no_default_excludes`, `gitignore`, `fail_on`, `min_level`, `image`, `details`). An `ext` key is rejected as unknown.
- **Report columns:** `Status`, `CCN`, `Max`, `NPath`, `MI`, `Lines`, `Dup` (added later), `File`. Also the summary line with the average and maximum total CCN.
- **Image contract:** a file list on stdin, one merged JSON document on stdout, diagnostics on stderr, and the exit statuses. The JSON has every key from day one, including the `duplication` and per-function keys (set to `null` until their sub-issues land).
- **Edge cases:** every case listed in #344's "Edge cases" section, each with its exact behaviour and message.
- **Exit codes:** `0` OK, `1` error, `2` `--fail-on` gate.

### Files
All files go under `docs/agents/specs/code_check/php_complexity/`. Each implementation sub-issue has exactly one spec file, which it links as its normative spec:

| File | Implemented by | Covers |
|---|---|---|
| `README.md` | all | The shared contracts (sections below) |
| `image.md` | #346 | Dockerfile and pins, the entrypoint contract, how the file list reaches PDepend, PDepend options, the XML → JSON mapping, refused lines and their messages, smoke checks |
| `release.md` | #347 | The `release_image.sh` selector, `smoke_test_php_complexity`, the CircleCI jobs, the Docker Hub descriptions, `docs/agents/tingle-php-complexity-image.md` |
| `cli.md` | #348 | The package layout on `docker_check`, the parser, the reporter columns and summary, thresholds, display flags, `--fail-on`, `PARSE` rows, registration, help and completion |
| `selection.md` | #349 | The selection flags, filter order, the Blade skip, interaction with `.gitignore` |
| `config.md` | #350 | `SCHEMA`, precedence, list merging, error messages |
| `details.md` | #351 | `--details` semantics, the line format, ordering and tie-breaks, the `details` key |
| `duplication.md` | #352 | The jscpd pin and options, the `duplication` JSON, the `Dup` column, degraded mode |

There is no `docker-check.md`, because the shared `docker_check` module already exists (#317), and no `sfc.md`, because there are no single-file components.

`README.md` has these sections, following the js_complexity specs README (#316):
1. Overview
2. Sub-issues and merge order (#345–#353)
3. CLI and flags
4. Extensions
5. Default excludes
6. Filter order
7. Config keys
8. Exit codes and streams
9. Image contract summary, including a merged JSON summary
10. Pinned tools: the PHP base image, PDepend, Node and jscpd
11. Deviations from #344

`docs/agents/specs.md` gets an entry that links the folder.

## Solution
Follow the structure of the js_complexity specs (#316). Pin versions, digests, field names, messages and the JSON shape precisely enough that the image and Python sub-issues can be implemented in parallel without asking each other.

### Out of scope
- Any implementation: image, Python, CLI or docs outside `docs/agents/specs/`.

## Benefits
- The image track (#346 → #347) and the Python track (#348 → #349 → #350) can be built in parallel against one agreed contract.
- Wrong assumptions about PDepend's output are caught before any code is written, not during implementation.
- The default thresholds are based on real PHP codebases rather than guesswork.
