# Specs: `tingle check_file_size` filtering, display and config

Parent issue: #247. This file holds the **shared contracts**, meaning everything
that more than one sub-issue depends on. Each feature spec is readable on its
own, but it must not contradict this file. If they disagree, this file wins and
the feature spec must be fixed.

## 1. Overview

#247 makes `tingle check_file_size` easier to point at real repositories. It
adds finer file selection (globs, additive excludes, `.gitignore`), a display
filter by level, and a user config file for the defaults.

| Feature | Spec | Sub-issue |
|---------|------|-----------|
| `--ignore` / `--include` globs | [ignore-include.md](ignore-include.md) | #249 |
| Additive `--exclude` + `--no-default-excludes` | [exclude.md](exclude.md) | #250 |
| `.gitignore` support + `--no-gitignore` | [gitignore.md](gitignore.md) | #251 |
| `--min-level` display filter | [min-level.md](min-level.md) | #252 |
| Config file `~/.tingle/code_check/config.json` | [config.md](config.md) | #253 |
| Cleanup: remove these specs and the index entry | n/a | #254 |

Out of scope for #247: a `--verbose` / `--list-ignored` debugging mode, output
formats, multiple paths, per-pattern thresholds, a project-level config, and
the migration to `code_check`.

## 2. Merge order

1. #249, then #250, then #251. All three change `FileCollector`
   (`python/check_file_size/file_collector.py`), so they merge one after
   another to avoid rebase churn.
2. #252 does not depend on the others and can merge at any time.
3. #253 merges after #249 to #252, because it maps every flag they add to a
   config key.
4. #254 merges last.

## 3. Flags

These are the final flag names and value types. Existing flags are listed too
because #253 maps them to config keys.

| Flag | Type | Repeatable | Default | Config key (type) |
|------|------|------------|---------|-------------------|
| `path` (positional) | str | no | required | none |
| `--warn N` | int | no | `300` | `warn` (int) |
| `--error N` | int | no | `500` | `error` (int) |
| `--critical N` | int | no | `1000` | `critical` (int) |
| `--top N` | int | no | `0` (all) | `top` (int) |
| `--exclude a,b` | comma-separated str | no | none (adds to `DEFAULT_EXCLUDES`) | `exclude` (list of str) |
| `--no-default-excludes` | `store_true` | no | off | `no_default_excludes` (bool, default `false`) |
| `--no-gitignore` | `store_true` | no | off | `gitignore` (bool, default `true`, the inverse of the flag) |
| `--ignore GLOB` | str | yes (`append`) | `[]` | `ignore` (list of str) |
| `--include GLOB` | str | yes (`append`) | `[]` | `include` (list of str) |
| `--ext .x` | str | yes (`append`) | none (no filter) | `ext` (list of str) |
| `--fail-on LEVEL` | `warn\|error\|critical` | no | none (no gate) | `fail_on` (str or `null`) |
| `--min-level LEVEL` | `ok\|warn\|error\|critical` | no | `ok` | `min_level` (str) |
| `--no-config` | `store_true` | no | off | none (the config file is not read or validated) |

Flags keep being declared in the `FLAGS` list in
`python/check_file_size/executor.py` and parsed by `common/arg_parser.py`.
Choice-valued flags use argparse `choices`, so a bad value is a usage error
(exit 1, see section 7).

## 4. Precedence

- **Single values** (`warn`, `error`, `critical`, `top`, `fail_on`,
  `min_level`): built-in defaults < config < CLI. A flag given on the CLI
  always wins.
- **List values** (`exclude`, `ignore`, `include`, `ext`): the config list and
  the CLI list are concatenated, config first, then deduplicated with the
  first occurrence kept. The CLI never replaces a config list.
- **Booleans** (`no_default_excludes`, `gitignore`): the config may set either
  value. The CLI flags can only turn behaviour **off** (`--no-default-excludes`,
  `--no-gitignore`), and they win over the config.
- To detect "not given on the CLI", single-value flags must default to `None`
  in `FLAGS`, and the built-in default is filled in after merging. The help
  text still shows the built-in default.
- `--no-config` skips the config file entirely (not read, not validated), so
  the order becomes built-in defaults < CLI. See [config.md](config.md).

## 5. Filter pipeline in `FileCollector`

For a directory `<path>`, every regular file found by the walk goes through
these steps in this order. The first step that rejects a file drops it.

1. **Default excludes**: any path component (case-insensitive) equal to an
   entry of `Constants.DEFAULT_EXCLUDES`. Skipped when `no_default_excludes`
   is set.
2. **`--exclude` names**: same path-component match, against the extra names.
3. **`.gitignore`**: the file is in git's ignored set (see
   [gitignore.md](gitignore.md)). Skipped when `gitignore` is `false`.
4. **`--ignore` globs**: the file's path relative to `<path>` matches any
   `--ignore` glob.
5. **`--include` globs and `--ext`**: when `--include` is given, the path must
   match at least one include glob. When `--ext` is given, the last suffix
   must be in the `--ext` set. When both are given, **both** must match.
6. **Binary check**: `SkipChecks.is_binary_file`.

For a single-file `<path>`, the same steps apply, with two differences: globs
match the file's name, and path-component excludes (steps 1 and 2) do not
apply. Glob matching rules are defined in
[ignore-include.md](ignore-include.md).

`FileCollector` receives the resolved values (the final exclude list, globs,
extensions, gitignore on/off). It does not read the config or the CLI itself.

## 6. Display vs counting

- The filters in section 5 decide which files are **analysed**.
- `--min-level` and `--top` only decide which analysed rows are **displayed**.
  `--min-level` is applied first, then `--top` takes the first N of what is
  left (rows stay sorted by line count, largest first).
- The summary line (`N file(s) | ... OK | ... WARN | ...`), the `Total:` line
  and the `--fail-on` gate always use **every analysed file**, whatever
  `--min-level` and `--top` are set to.
- This changes current behaviour, where `--top` also cuts the summary. The
  `Reporter` must therefore receive the full result list for the summary and
  the displayed rows separately. #252 makes this change.

## 7. Exit codes and streams

These are unchanged:

| Code | Meaning |
|------|---------|
| `0` | Success (including "no files found" and "no rows at this level"). |
| `1` | Error: bad option or value (argparse's exit 2 is remapped to 1), path not found, config error. |
| `2` | The `--fail-on` gate failed. |

Errors and warnings go to stderr, and the report goes to stdout. Colours only
appear on a TTY when `NO_COLOR` is not set (`Palette`).

## 8. Docs and tests per sub-issue

Each of #249 to #253 must, in the same PR:

- update the user guide `docs/guides/check_file_size.md` (owned by the
  `guide` agent),
- update the `long_help` of `check_file_size` in `commands/python.json`,
- update the flag help in `FLAGS` and the examples in the `executor.py`
  module docstring,
- add or update tests under `python/tests/check_file_size/`.
