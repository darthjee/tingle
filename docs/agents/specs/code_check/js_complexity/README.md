# Specs: `tingle code_check js_complexity`

Parent issue: #315. Specs sub-issue: #316. This file holds the **shared
contracts**, meaning everything that more than one sub-issue depends on. Each
feature spec is readable on its own, but it must not contradict this file. If
they disagree, this file wins and the feature spec must be fixed.

These specs are normative and take precedence over the bodies of #315 and of
the sub-issues #317 to #327. Every place where they change #315 is listed in
[section 11](#11-deviations-from-315).

## 1. Overview

`tingle code_check js_complexity <path>` measures the complexity of
JavaScript and TypeScript code. Tingle selects the files on the host, then
runs three pinned tools inside the published Docker image
`darthjee/tingle_js_complexity`:

- [FTA](https://ftaproject.dev/) is the primary, per-file analyser. Its
  `fta_score` sets each file's level.
- [jscpd](https://github.com/kucherenko/jscpd) adds duplication data (the
  `Dup` column, #324).
- [typhonjs-escomplex](https://github.com/typhonjs-node-escomplex/typhonjs-escomplex)
  adds per-function data (`--details`, #325).

The host needs Docker, but no Node. The report has the same layout as
`file_size` and `rubycritic`: one row per file, levels from numeric
thresholds on `fta_score`, and a summary with the average and maximum FTA
score.

The contracts in these specs come from a real run of the pinned versions
(`node:24.21.0-slim`, FTA `3.1.0`, jscpd `5.4.1`, typhonjs-escomplex `0.1.0`)
on the fixture listed in [image.md](image.md#9-smoke-test-fixture). They are
not based on assumptions. The commands, versions and raw results of that run
are in [image.md](image.md#10-grounding-run).

## 2. Sub-issues and merge order

| Sub-issue | What | Spec | Depends on |
|---|---|---|---|
| #316 | Specs (this issue) | — | — |
| #317 | Extract `python/code_check/docker_check/` from rubycritic | [docker-check.md](docker-check.md) | #316 |
| #318 | Image `docker/js_complexity/`, FTA only | [image.md](image.md) | #316 |
| #319 | Release pipeline for `darthjee/tingle_js_complexity` | [release.md](release.md) | #318 |
| #320 | Subcommand core | [subcommand.md](subcommand.md) | #317 (local image from #318) |
| #321 | File selection flags | [file-selection.md](file-selection.md) | #320 |
| #322 | Config section `js_complexity` | [config.md](config.md) | #321 |
| #323 | Skip minified bundles | [file-selection.md](file-selection.md) | #321 |
| #324 | Duplication via jscpd | [duplication.md](duplication.md) | #319, #320 |
| #325 | `--details` via typhonjs-escomplex | [details.md](details.md) | #319, #322 |
| #326 | `.vue/.svelte/.astro` support | [sfc.md](sfc.md) | #324, #325 |
| #327 | Cleanup: remove the specs | — | #316–#326 |

**Merge order**

- After #316, three tracks run in parallel: #317, #318 → #319, and
  #320 → #321 → #322 (after #317).
- #319 must be merged before the tingle tag that ships #320 is pushed.
  Otherwise the CLI would default to an image tag that was never published.
  #320 may merge to `main` earlier, as long as no release tag is pushed in
  between.
- #324, #325 and #326 each change the image and the Python side in the same
  PR. The image and the CLI are always released under the same tingle tag, so
  they stay in sync.
- #327 merges last. It removes `docs/agents/specs/code_check/js_complexity/`
  and the row in [`docs/agents/specs.md`](../../../specs.md).

For manual end-to-end tests before #319, #320 uses a local build from #318
through `--image tingle_js_complexity:dev`.

## 3. CLI and flags

```
tingle code_check js_complexity <path> [options]
```

There is no `--ext` flag and no `ext` config key: the extensions are fixed
(section 4).

| Flag | Type | Repeatable | Default | Added by | Config key (type) |
|------|------|------------|---------|----------|-------------------|
| `path` (positional) | str | no | required | #320 | none |
| `--warn N` | number ≥ 0 (float) | no | `50` | #320 | `warn` (number ≥ 0) |
| `--error N` | number ≥ 0 (float) | no | `60` | #320 | `error` (number ≥ 0) |
| `--critical N` | number ≥ 0 (float) | no | `75` | #320 | `critical` (number ≥ 0) |
| `--top N` | int ≥ 0 | no | `0` (all) | #320 | `top` (int ≥ 0) |
| `--min-level LEVEL` | `ok\|warn\|error\|critical` | no | `ok` | #320 | `min_level` (str) |
| `--fail-on LEVEL` | `warn\|error\|critical` | no | none (no gate) | #320 | `fail_on` (str or `null`) |
| `--image IMAGE` | str (non-empty) | no | `darthjee/tingle_js_complexity:<tingle version>` | #320 | `image` (non-empty str) |
| `--exclude a,b` | comma-separated str | no | none (adds to the default excludes) | #321 | `exclude` (list of str) |
| `--no-default-excludes` | `store_true` | no | off | #321 | `no_default_excludes` (bool, default `false`) |
| `--no-gitignore` | `store_true` | no | off | #321 | `gitignore` (bool, default `true`, the inverse of the flag) |
| `--ignore GLOB` | str | yes (`append`) | `[]` | #321 | `ignore` (list of str) |
| `--include GLOB` | str | yes (`append`) | `[]` | #321 | `include` (list of str) |
| `--no-config` | `store_true` | no | off | #322 | none (the config file is not read or validated) |
| `--details [N]` | int ≥ 0, optional value | no | off; `5` when given without `N`; `0` = all | #325 | `details` (int ≥ 0 or `null`) |

- The flag names, meanings and argparse style are `rubycritic`'s
  (`python/code_check/rubycritic/flags.py`). Single-value flags default to
  `None` in `FLAGS`, and the built-in default is filled in after merging with
  the config. The help text still shows the built-in default.
- `--warn`, `--error` and `--critical` apply to FTA's per-file `fta_score`,
  rounded to one decimal (see [subcommand.md](subcommand.md#2-flags-and-levels)).
  They use `type=float`; a negative value is a usage error (exit 1).
- `--top`, `--min-level` and `--details` only change the display. The
  summary and the `--fail-on` gate always count every selected file.
- Choice-valued flags use argparse `choices`. Argparse's exit 2 is remapped
  to 1, as in `rubycritic`.
- The precedence rules (CLI over config for single values, concatenation for
  lists) are in [config.md](config.md#3-precedence).

**Thresholds and FTA's bands.** FTA labels each file with an `assessment`
(`utils::get_assessment` in FTA 3.1.0): `"Needs improvement"` when
`fta_score > 60`, `"Could be better"` when `fta_score > 50`, else `"OK"`.
The defaults `warn=50` and `error=60` line up with these bands. `critical=75`
is tingle's own: FTA has no third band. Tingle's levels use `>=`, like
`file_size`, so a score of exactly `50.0` is `WARN` in tingle and `"OK"` in
FTA's label. The label is information only and never sets the level.

## 4. Extensions

Matching is on the file name, case-insensitive (`.JS` is analysed).

| Rule | Names | Added by | Turned off by |
|------|-------|----------|---------------|
| Core extensions (analysed) | `.js .mjs .cjs .jsx .ts .mts .cts .tsx` | #320 | never |
| Declaration files (always skipped) | names ending in `.d.ts`, `.d.mts`, `.d.cts` | #320 | never (not even `--no-default-excludes`) |
| Minified bundles (skipped by default) | names ending in `.min.js`, `.min.mjs`, `.min.cjs` | #323 | `--no-default-excludes` or `"no_default_excludes": true` only |
| Single-file components (analysed) | `.vue .svelte .astro` | #326 | never |

- `--include` only ever narrows the selection. It never brings back a
  declaration file or a minified bundle.
- The same rules apply to a single-file `<path>`: a declaration file is
  never analysed, and a minified file is analysed only with
  `--no-default-excludes`.
- Details: [file-selection.md](file-selection.md#2-extensions-and-skip-rules).

## 5. Default excludes

`file_size`'s `Constants.DEFAULT_EXCLUDES` plus six JS tooling output
directories, in this order (19 names):

```
node_modules, dist, build, .git, vendor, third_party, .next, __pycache__,
.cache, coverage, .nuxt, out, target, .turbo, .svelte-kit, .output,
.vercel, .parcel-cache, storybook-static
```

They are matched against path components, case-insensitively, as in
`file_size`. `--no-default-excludes` drops all of them, and the minified
skip with them. See [file-selection.md](file-selection.md#3-default-excludes).

## 6. Filter order

For a directory `<path>`, every regular file found by the walk goes through
these steps in this order. The first step that rejects a file drops it.

1. Default excludes (skipped with `--no-default-excludes`).
2. `--exclude` names.
3. `.gitignore` (skipped with `--no-gitignore`).
4. `--ignore` globs.
5. `--include` globs and the extension list: when `--include` is given the
   path must match one include glob, **and** the extension must be in the
   list from section 4.
6. Skip rules: declaration files (always), then minified bundles (unless
   `--no-default-excludes`).
7. Symlink confinement: a file resolving outside the mount root is dropped.

After the filters, tingle drops the file names that cannot be sent on stdin
(a newline, or not valid UTF-8). #320 ships steps 1, 5 (extensions only), 6
(declaration files only) and 7; #321 adds steps 2 to 4 and the `--include`
part of step 5; #323 adds the minified rule of step 6. See
[file-selection.md](file-selection.md#5-filter-order).

## 7. Config keys

The `js_complexity` section of `~/.tingle/code_check/config.json` accepts
these keys, and no others: `warn`, `error`, `critical`, `top`, `exclude`,
`no_default_excludes`, `ignore`, `include`, `gitignore`, `fail_on`,
`min_level`, `image` (all from #322) and `details` (from #325). `ext` is an
unknown key. The rules are `rubycritic`'s. The schema, precedence and error
handling are in [config.md](config.md).

## 8. Exit codes and streams

| Code | Meaning |
|------|---------|
| `0` | Success, including "no file selected" (no container started) and "no rows at this level". `PARSE` rows and secondary-tool warnings never change the exit code. |
| `1` | Error: bad option or value, `<path>` missing or unreadable, config error, `docker` not found, Docker daemon not responding, image pull failure, mount failure, container or FTA failure, unparsable container output. |
| `2` | The `--fail-on` gate failed. Only `--fail-on` exits 2. |

- The report goes to stdout. Errors (`Error: <message>`, red, then exit 1)
  and warnings (`Warning: <message>`, yellow) go to stderr, in `rubycritic`'s
  style. The Docker messages are `rubycritic`'s, produced by the shared
  `docker_check` package (see [docker-check.md](docker-check.md)).
- A jscpd or escomplex failure is never fatal: the report is printed from
  FTA's data, and one warning naming the tool goes to stderr.
- Colours only appear on a TTY when `NO_COLOR` is not set (`Palette`).
- The exact message texts are in
  [subcommand.md](subcommand.md#10-messages),
  [duplication.md](duplication.md#5-failure-handling),
  [details.md](details.md#6-failure-handling) and
  [config.md](config.md#5-error-handling).

## 9. Image contract summary

- **Image:** `darthjee/tingle_js_complexity`. The default tag is the tingle
  version: the trimmed content of `shell/linux/VERSION`. Every tingle release
  tag `X.Y.Z` publishes `darthjee/tingle_js_complexity:X.Y.Z` (one amd64 +
  arm64 manifest, no `latest`). See [release.md](release.md).
- **Run line** (the same as `rubycritic`'s, used by tingle and by the smoke
  test):

  ```
  docker run --rm -i --pull never --network none --security-opt no-new-privileges \
    --user <uid>:<gid> -v <root>:/src:ro -w /src <image>
  ```

  `<root>` is the resolved `<path>` for a directory, or its parent directory
  for a single file.
- **stdin:** the selected files, one path per line, relative to `<root>`,
  UTF-8, POSIX separators, each line ending in `\n`, sorted.
- **Tool input:** the entrypoint copies each file into a staged tree under
  `/tmp/stage/` and runs every tool on that tree, never on `/src`. Files are
  staged under opaque names (`/tmp/stage/plain/<n>.<ext>`, `<n>` being the
  stdin line number), and results are mapped back by `<n>`. See
  [image.md](image.md#5-staged-tree).
- **stdout:** exactly one JSON document, the **merged JSON** (below).
- **stderr:** everything else, including the tools' own output.
- **Exit status:** 0 when the JSON was printed; non-zero when FTA fails or
  the entrypoint fails, with nothing on stdout. A jscpd or escomplex failure
  is reported in `warnings` and does not change the exit status.
- **No git** in the image.

### Merged JSON summary

The full definition is in [image.md](image.md#7-merged-json). The rules
every sub-issue relies on:

- **Fixed shape from day one.** #318 already emits every key below. #324 and
  #325 only fill in their parts (`duplication`, `functions`,
  `tool_versions.jscpd`, `tool_versions.escomplex`); they never add or rename
  a key.
- **No version field and no negotiation.** The image and the CLI are always
  released under the same tingle tag. A key that is missing, or of the wrong
  type, is an unparsable-output error (exit 1).
- **One entry per stdin line, in stdin order**, even for files a tool dropped
  or failed on, and even for lines the entrypoint refused.
- **`null` means not available; `[]` or `0` means available and empty.**
  The report tells them apart: `Dup` shows `-` for `null` and `0` for 0;
  `--details` shows `(per-function data unavailable)` for `null` and nothing
  for `[]`.

```json
{
  "tool_versions": {"fta": "3.1.0", "jscpd": null, "escomplex": null},
  "files": [
    {
      "path": "complex.ts",
      "parse_error": false,
      "fta": {"score": 71.25291592210418, "cyclo": 136, "lines": 245, "assessment": "Needs improvement"},
      "duplication": null,
      "functions": null
    },
    {"path": "broken.js", "parse_error": true, "fta": null, "duplication": null, "functions": null},
    {"path": "empty.js", "parse_error": false, "fta": null, "duplication": null, "functions": null}
  ],
  "warnings": [
    {"tool": "fta", "path": "broken.js", "message": "Error { error: (36..37, Expected(\",\", \"numeric literal (1, 1)\")) }"}
  ]
}
```

After #324 and #325 the parts are filled in, for example
`"duplication": {"lines": 22}` and
`"functions": [{"name": "reducer", "line": 9, "cyclo": 12, "sloc": 27}]`.

Per-file states:

| `parse_error` | `fta` | Report |
|---|---|---|
| `false` | object | normal row |
| `true` | `null` | `⛔ PARSE` row |
| `false` | `null` | dropped by FTA, or refused by the entrypoint → `OK`, score 0 |

`warnings` entries are `{"tool": <"entrypoint" | "fta" | "jscpd" | "escomplex">, "message": <str>, "path": <str, optional>}`.

## 10. Pinned tools

| Component | Version | Added by | Pinned by |
|-----------|---------|----------|-----------|
| Node (base image) | `node:24.21.0-slim` (Debian 12 bookworm, Node 24 "Krypton", the active LTS line) | #318 | `ARG BASE_IMAGE` with the index digest |
| FTA | `3.1.0` (crate `fta`, built from source) | #318 | `cargo install fta --version 3.1.0 --locked` in a `rust:1.99.0-slim-bookworm` stage |
| jscpd | `5.4.1` | #324 | `package.json` + `package-lock.json` |
| typhonjs-escomplex | `0.1.0` (with `@babel/parser` `7.29.9`) | #325 | `package.json` + `package-lock.json` |

Every option that affects the results is pinned in the entrypoint and
recorded in the spec of the sub-issue that adds the tool
([image.md](image.md#6-fta-invocation),
[duplication.md](duplication.md#2-jscpd-invocation),
[details.md](details.md#2-escomplex-wrapper)). Changing one is a deliberate
change, the same as a version bump.

## 11. Deviations from #315

Each item below changes #315's body or a sibling issue body. Each resolution
is binding. "Grounding" means the real run recorded in
[image.md](image.md#10-grounding-run).

1. **FTA is built from source, not installed from `fta-cli`** (#318,
   [image.md](image.md#2-dockerfile)). Grounding: `fta-cli` 3.1.0's Linux
   arm64 binary is dynamically linked against musl
   (`/lib/ld-musl-aarch64.so.1`) and fails on Debian slim, first with
   `ENOENT`, then, with Debian's `musl` package added, with
   `Error loading shared library libgcc_s.so.1`. The amd64 binary is static
   and works. #315's reason for a glibc base ("FTA ships a native binary") is
   therefore not accurate: FTA's npm binaries are musl builds.
   **Resolution:** keep the decided Debian slim base, and build FTA 3.1.0 from
   the `fta` crate with `cargo install --locked` in a pinned Rust stage, for
   both platforms. The source build and `fta-cli`'s amd64 binary gave
   identical results on the whole fixture. An Alpine base also works, but it
   was rejected to keep the decided base.
2. **Staged files keep their content but not their relative path** (#318,
   #326, [image.md](image.md#5-staged-tree)). The decided choice was
   `/tmp/stage/<same relative path>`, mapped back by stripping the prefix.
   Grounding: FTA's built-in filters cannot be turned off. A config file only
   adds to them, so FTA always drops directories named `dist`, `bin` or
   `build`, names ending in `.d.ts`, `.min.js` or `.bundle.js`, hidden files
   (through the `ignore` crate's standard filters), and extensions it matches
   case-sensitively. With relative paths, FTA silently dropped
   `build/out.js`, `bundle.min.js`, `ext/types.d.ts` and `ext/UPPER.JS`.
   **Resolution:** each stdin line `<n>` (1-based) is copied to
   `/tmp/stage/plain/<n>.<ext>`, `<ext>` being its lower-cased extension. SFC
   virtual modules go to their own subtree, `/tmp/stage/sfc/<n>.<ext>.<ts|js>`.
   Every tool still runs on the staged tree only, and nothing is written
   outside `/tmp`. Results are mapped back by `<n>` to the stdin line.
3. **Copies, not symlinks** (#318). The decided choice left this to the
   grounding run. FTA does not follow symlinks (it returned `[]` for a tree
   of symlinks). **Resolution:** the entrypoint copies the files.
4. **Parse errors are not in FTA's JSON** (#318, #320). Grounding: FTA logs
   `WARN  fta] Failed to analyze <path>: <error>` on stderr, drops the file
   from its JSON and exits 0. It drops a file that is not valid UTF-8 with no
   message at all. **Resolution:** the entrypoint reads FTA's stderr for
   those lines, checks UTF-8 itself, and sets `parse_error: true` for both
   cases, with the reason in `warnings`.
5. **Which files FTA drops** (#318, #320). #315 says FTA silently drops
   "empty files, files with no statements". Grounding: FTA drops every file
   with at most `exclude_under` lines (default 6), counting non-blank,
   non-comment lines only. **Resolution:** the entrypoint pins
   `--exclude-under 0`, so only files with no code line (empty, blank or
   comment-only) are dropped. They are `OK` with a score of 0. A file with
   one statement gets a normal row.
6. **FTA's score cap** (#318). FTA exits 1 when any file scores above its
   `score_cap` (default 1000). **Resolution:** the entrypoint pins
   `--score-cap 1000000000`, so a huge bundle analysed with
   `--no-default-excludes` never fails the run.
7. **`Lines` is FTA's `line_count`** (#320). It counts non-blank,
   non-comment lines, not physical lines. The column shows it as reported;
   tingle never recounts.
8. **jscpd details** (#324, [duplication.md](duplication.md)). jscpd 5.4.1
   is a Rust binary shipped as per-platform optional npm packages
   (`jscpd-linux-x64-gnu`, `jscpd-linux-arm64-gnu`). It prints its summary
   on stdout even with `--silent`, does not compare JavaScript with
   TypeScript unless `--cross-formats` is set, and needs `--formats-exts` to
   read `.mjs/.cjs/.mts/.cts`. **Resolution:** the entrypoint sends jscpd's
   stdout to stderr and pins `--cross-formats js-ts` and the extension map.
9. **escomplex details** (#325, [details.md](details.md)). Its default
   parser options enable `jsx` and `typescript` together, which fails on
   `<T>value` type assertions in `.ts` files (`Unterminated JSX contents`).
   Its `sloc` is an object (`logical`, `physical`), and class methods are
   reported apart from functions. **Resolution:** the wrapper pins one plugin
   set per extension; `sloc` is the physical count; class methods are listed
   with functions, as `<Class>.<method>`.
10. **The SFC line map is the identity** (#326, [sfc.md](sfc.md#4-line-map)).
    The decided choice keeps a line map from the virtual module back to the
    original file. **Resolution:** the virtual module is the original file
    with every character outside the script blocks replaced by a space and
    every line break kept, so its line numbers are the original ones. FTA
    ignores blank lines, so its results are the same as for the bare script.
    This was checked with CRLF line endings and a BOM.
11. **The `CRITICAL` label** (#320). #315's example shows `🚨 CRITICAL`.
    **Resolution:** reuse `file_size`'s labels (`🟣 CRITICAL`), as
    `rubycritic` does.
12. **Score precision** (#320). FTA's score is a raw float
    (`71.25291592210418`). **Resolution:** tingle rounds it to one decimal
    when parsing, and the rounded value is used for the level, the sort, the
    `--fail-on` gate and the summary, so the shown value is the one compared
    with the thresholds.
13. **The `--details` line layout** (#325, [details.md](details.md#4-report)).
    #315's example (`cyclo 18  reducer  (L120)`) is replaced with
    `rubycritic`'s layout plus the sloc: `cyclo 12  sloc 27  reducer  (src/store.ts:9)`.
14. **A minified single file** (#323). #315 does not say what happens to a
    minified `<path>` given as a single file. **Resolution:** it follows the
    same rule as in a directory: skipped unless `--no-default-excludes`.
    This differs from the directory excludes, which never apply to a single
    file.
