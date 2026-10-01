# Specs: `tingle code_check rubycritic`

Parent issue: #290. This file holds the **shared contracts**, meaning
everything that more than one sub-issue depends on. Each feature spec is
readable on its own, but it must not contradict this file. If they disagree,
this file wins and the feature spec must be fixed.

## 1. Overview

`tingle code_check rubycritic <path>` measures the complexity of Ruby code.
Tingle selects the `.rb` files under `<path>` on the host, then runs
[RubyCritic](https://github.com/whitesmith/rubycritic) (Flog, Flay and Reek)
inside the published Docker image `darthjee/tingle_rubycritic`. The host needs
Docker, but no Ruby. The report has the same layout as `file_size`: one row
per file, levels from numeric thresholds on the file's total Flog complexity,
and a summary that adds RubyCritic's overall score.

The RubyCritic contract in these specs comes from a real run of the pinned
versions (`ruby:3.3.12-slim`, `rubycritic 5.0.0`). It is not based on
assumptions. See [section 9](#9-contradictions-with-290) for the places where
the real output differs from #290.

## 2. Sub-issues and merge order

| Sub-issue | Title | Spec | Agents | Depends on |
|-----------|-------|------|--------|------------|
| #292 | Write the specs | none (this folder) | `product-owner` | none |
| #293 | Build the `tingle_rubycritic` Docker image (`docker/rubycritic/`) | [image.md](image.md) | `shell` | #292 |
| #294 | Publish `darthjee/tingle_rubycritic` from the CircleCI release workflow | [release.md](release.md) | `shell`, `product-owner` | #293 |
| #295 | Add the subcommand (runner, report, thresholds) | [subcommand.md](subcommand.md) | `python`, `cli`, `guide` | #292 |
| #296 | Add `--exclude`/`--ignore`/`--include` and `.gitignore` file selection | [file-selection.md](file-selection.md) | `python`, `guide` | #295 |
| #297 | Load options from the `rubycritic` config section | [config.md](config.md) | `python`, `guide` | #296 |
| #298 | Remove `docs/agents/specs/code_check/rubycritic/` | none | `product-owner` | #292 to #297 |

Merge order:

1. #292 merges first.
2. Then two tracks run in parallel:
   - the image track: #293, then #294;
   - the Python track: #295, then #296, then #297.
3. #298 merges last.
4. **Release rule:** #294 must be merged before the tingle release tag that
   ships #295 is pushed. Otherwise the CLI would default to an image tag that
   was never published. #295 may merge to `main` earlier, as long as no
   release tag is pushed in between.

For manual end-to-end tests before #294, #295 uses a local build from #293
through `--image tingle_rubycritic:dev`.

## 3. CLI and flags

```
tingle code_check rubycritic <path> [options]
```

Only `.rb` files are analysed. There is no `--ext` flag and no `ext` config
key.

| Flag | Type | Repeatable | Default | Added by | Config key (type) |
|------|------|------------|---------|----------|-------------------|
| `path` (positional) | str | no | required | #295 | none |
| `--warn N` | number ≥ 0 (float) | no | `100` | #295 | `warn` (number ≥ 0) |
| `--error N` | number ≥ 0 (float) | no | `200` | #295 | `error` (number ≥ 0) |
| `--critical N` | number ≥ 0 (float) | no | `400` | #295 | `critical` (number ≥ 0) |
| `--top N` | int ≥ 0 | no | `0` (all) | #295 | `top` (int ≥ 0) |
| `--min-level LEVEL` | `ok\|warn\|error\|critical` | no | `ok` | #295 | `min_level` (str) |
| `--fail-on LEVEL` | `warn\|error\|critical` | no | none (no gate) | #295 | `fail_on` (str or `null`) |
| `--image IMAGE` | str (non-empty) | no | `darthjee/tingle_rubycritic:<tingle version>` | #295 | `image` (non-empty str) |
| `--exclude a,b` | comma-separated str | no | none (adds to the default excludes) | #296 | `exclude` (list of str) |
| `--no-default-excludes` | `store_true` | no | off | #296 | `no_default_excludes` (bool, default `false`) |
| `--no-gitignore` | `store_true` | no | off | #296 | `gitignore` (bool, default `true`, the inverse of the flag) |
| `--ignore GLOB` | str | yes (`append`) | `[]` | #296 | `ignore` (list of str) |
| `--include GLOB` | str | yes (`append`) | `[]` | #296 | `include` (list of str) |
| `--no-config` | `store_true` | no | off | #297 | none (the config file is not read or validated) |
| `--details [N]` | int ≥ 0, optional value (`nargs='?'`, `const=5`) | no | `None` (off) | #291 | `details` (int ≥ 0 or `null`) |

- The flag names, meanings and argparse style are the same as `file_size`'s
  (`python/code_check/file_size/flags.py`). Single-value flags default to
  `None` in `FLAGS`, and the built-in default is filled in after merging with
  the config. The help text still shows the built-in default.
- `--warn`, `--error` and `--critical` use `type=float` in argparse. A
  negative value is a usage error (exit 1).
- Choice-valued flags use argparse `choices`, so a bad value is a usage error.
  Argparse's exit 2 is remapped to 1, as in `file_size`.
- The precedence rules (CLI over config for single values, concatenation for
  lists) are defined in [config.md](config.md).
- `--details` alone means 5; `--details 0` means all methods; absent means no
  detail lines. A negative value is a usage error (exit 1,
  `Error: --details must be an integer >= 0`). The detail lines under each
  file and the missing-`methods` error are pinned in
  [subcommand.md](subcommand.md#5-rubycritic-json-contract). Method scores
  are informative only: levels, `--fail-on` and the exit codes stay
  file-based.

## 4. Exit codes and streams

| Code | Meaning |
|------|---------|
| `0` | Success, including "no `.rb` files selected" (no container started) and "no rows at this level". `PARSE` rows never change the exit code. |
| `1` | Error: bad option or value, `<path>` missing or unreadable, config error, `docker` not found, Docker daemon not responding, image pull failure, mount failure, container or RubyCritic failure, unparsable container output. |
| `2` | The `--fail-on` gate failed. Only `--fail-on` exits 2. |

- The report goes to stdout. Errors (`Error: <message>`, red) and warnings
  (`Warning: <message>`, yellow) go to stderr, in `file_size`'s style.
- Colours only appear on a TTY when `NO_COLOR` is not set (`Palette`).
- The exact message texts are pinned in
  [subcommand.md](subcommand.md#10-messages) and
  [config.md](config.md#5-error-handling).

## 5. Config keys

The `rubycritic` section of `~/.tingle/code_check/config.json` accepts these
keys, and no others: `warn`, `error`, `critical`, `top`, `exclude`,
`no_default_excludes`, `ignore`, `include`, `gitignore`, `fail_on`,
`min_level`, `image`, `details`. Types are in [section 3](#3-cli-and-flags). The schema,
precedence, list merging and error handling are in [config.md](config.md).

## 6. Default excludes

The default excludes are `file_size`'s `Constants.DEFAULT_EXCLUDES` plus three
Ruby-specific names, in this order:

```
node_modules, dist, build, .git, vendor, third_party, .next, __pycache__,
.cache, coverage, .nuxt, out, target, tmp, log, .bundle
```

They are matched against path components, case-insensitively, as in
`file_size`. `--no-default-excludes` drops all of them. See
[file-selection.md](file-selection.md).

## 7. Filter order

For a directory `<path>`, every regular file found by the walk goes through
these steps in this order. The first step that rejects a file drops it.

1. Default excludes (skipped with `--no-default-excludes`).
2. `--exclude` names.
3. `.gitignore` (skipped with `--no-gitignore`).
4. `--ignore` globs.
5. `--include` globs and the fixed `.rb` suffix: when `--include` is given the
   path must match one include glob, **and** the suffix must be `.rb`
   (case-insensitive).

After the filters, tingle drops symlinks whose target is outside the mount
root and filenames that cannot be sent on stdin (see
[file-selection.md](file-selection.md#6-symlinks-and-unsendable-names)).
Issue #295 ships steps 1 and 5 (default excludes and `.rb` only); issue #296
adds steps 2 to 4, the `--include` part of step 5 and the symlink rule.

## 8. Image contract summary

- **Image:** `darthjee/tingle_rubycritic`. The default tag is the tingle
  version: the trimmed content of `shell/linux/VERSION`, read the same way
  `shell/linux/docker_run.sh` reads it. Every tingle release tag `X.Y.Z`
  publishes `darthjee/tingle_rubycritic:X.Y.Z` (one amd64 + arm64 manifest, no
  `latest`). See [release.md](release.md).
- **Run line** (the canonical one, used by tingle and by the smoke test):

  ```
  docker run --rm -i --pull never --network none --security-opt no-new-privileges \
    --user <uid>:<gid> -v <root>:/src:ro -w /src <image>
  ```

  `<root>` is the resolved `<path>` for a directory, or its parent directory
  for a single file. Tingle pulls the image beforehand when it is missing (see
  [subcommand.md](subcommand.md#3-run-order-preflight-and-pulling)).
- **stdin:** the selected files, one path per line, relative to `<root>`,
  UTF-8, POSIX separators, each line ending in `\n`.
- **stdout:** exactly one JSON object: RubyCritic's `report.json` plus
  `parse_errors` and `methods` (per-method Flog scores, added by #291), both
  added by the entrypoint. See
  [image.md](image.md#4-entrypoint-contract) and
  [subcommand.md](subcommand.md#5-rubycritic-json-contract).
- **stderr:** everything else, including RubyCritic's own progress output
  (RubyCritic writes it to stdout, so the entrypoint redirects it).
- **Exit status:** 0 when the JSON was printed, non-zero on any failure. A
  file with a syntax error is **not** a failure: it is listed in
  `parse_errors`.
- **No git** in the image, so RubyCritic computes no churn.

### Ownership of `docker/`

The new top-level `docker/` folder (one sub-folder per check image, starting
with `docker/rubycritic/`) is owned by the **`shell`** agent. #293 creates it,
extends the scope in `.claude/agents/shell.md`, and adds the folder to
`docs/agents/folder-structure.md`.

## 9. Contradictions with #290

The real RubyCritic 5.0.0 run differs from #290's assumptions in these places.
Each resolution below is binding.

1. **A syntax error aborts the whole run.** Reek raises
   `Reek::Errors::SyntaxError` on the first unparsable file: RubyCritic exits
   1 and writes no `report.json`. Flog only prints `skipping <file>`. RubyCritic
   alone therefore cannot produce the `PARSE` rows #290 describes.
   **Resolution:** the entrypoint pre-parses every file with the same parser
   Reek uses, removes the failures from the RubyCritic run, and lists them in
   a `parse_errors` key added to the JSON on stdout. Tingle shows them as
   `PARSE` rows. Stdout is therefore "`report.json` plus `parse_errors`", not
   the raw `report.json`.
2. **Paths are not `/src/...`.** RubyCritic writes each path as it was passed,
   with a leading `./` removed. Because the entrypoint passes the relative
   paths from stdin, the JSON paths are already relative to `<root>`.
   **Resolution:** tingle maps paths by exact match with the lines it sent. It
   still strips a leading `/src/` or `./` before matching, as a safeguard.
3. **Empty and method-less files are not dropped.** They are present, with
   `complexity` `0.0`, `rating` `"A"` and `methods_count` `0`.
   **Resolution:** the "dropped file → `OK`, complexity 0" rule stays, as a
   safeguard: RubyCritic does silently drop a path it cannot find (exit 0).
4. **`smells` is not Reek-only.** The per-file `smells` list also holds Flay's
   `DuplicateCode` and Flog's `HighComplexity`/`VeryHighComplexity` entries,
   and the JSON has no analyser field.
   **Resolution:** the `Smells` column counts the entries whose `type` is not
   one of those three.
5. **RubyCritic prints to stdout.** Its progress lines, the "no Git
   repository" notice and `Score: NN.NN` all go to stdout.
   **Resolution:** the entrypoint sends RubyCritic's stdout and stderr to its
   own stderr, and prints only the JSON on stdout.
6. **The `CRITICAL` label.** #290's example shows `🚨 CRITICAL`; `file_size`
   uses `🟣 CRITICAL`. **Resolution:** reuse `file_size`'s labels.
7. **Complexity precision.** #290's example shows one decimal. RubyCritic
   rounds to two decimals. **Resolution:** the report prints two decimals, so
   the shown value is the one compared with the thresholds.
