# Issue: code_check js_complexity: duplication column via jscpd

## Description
Add duplication data to `tingle code_check js_complexity` (parent #315). [jscpd](https://github.com/kucherenko/jscpd) runs in the image and fills an information-only `Dup` column. It is the counterpart of RubyCritic's Flay-based `Duplication` column.

Spec (authoritative for every exact value below): `docs/agents/specs/code_check/js_complexity/duplication.md`.

## Problem
FTA scores complexity only. Copy-pasted code is a major maintainability signal, and the report does not show it. The merged JSON already has `files[].duplication` and `tool_versions.jscpd`, and the Python parser already validates them, but the entrypoint always sets them to `null`.

## Expected Behavior
- **Image** (`docker/js_complexity/`):
  - `jscpd` `5.4.1` is pinned exactly in `package.json`. `package-lock.json` is regenerated and lists both `jscpd-linux-x64-gnu` and `jscpd-linux-arm64-gnu` `5.4.1`.
  - After FTA, when at least one file is staged, the entrypoint runs jscpd on `/tmp/stage` with the pinned options from spec section 2. The report is written to `/tmp/jscpd/jscpd.json`, and jscpd's stdout and stderr go to the entrypoint's stderr.
  - `tool_versions.jscpd` is read from `node_modules/jscpd/package.json`.
  - `files[].duplication.lines` counts the distinct lines of the file that any clone covers, so each line counts once. The value is `{"lines": 0}` for a file read by jscpd that is in no clone, including a file FTA dropped. It is `null` for files over 1 MiB, `parse_error` files and refused lines.
  - A jscpd failure (any case in spec section 5) never fails the run. Every file then gets `duplication: null`, `tool_versions.jscpd` is kept, and one `{"tool": "jscpd", "message": ...}` warning (no `path`) is added.
  - The smoke test in `scripts/release_image.sh` asserts `tool_versions.jscpd == "5.4.1"`. It asserts `duplication.lines >= 20` for `dup_a.js`/`dup_b.js`, `0` for `simple.js`/`empty.js`, and `null` for `broken.js`, `latin1.js` and the hostile lines.
  - The Docker Hub description mentions jscpd.
- **Subcommand** (`python/code_check/js_complexity/`):
  - A new `Dup` column (`{:>5}`) sits between `Lines` and `Assessment`, with the header and separator from spec section 4. It shows `duplication.lines`. `0` means checked with no clone, and `-` means not available (`null`, and every `PARSE` row). The column is information only: it never sets the level or the exit code. The summary is unchanged.
  - For each `jscpd` warning without a `path`, stderr gets `Warning: jscpd failed in <image>; duplication data is not available: <message>`. The exit code is unchanged.
  - Only the selected files are compared, so clones with excluded or ignored files never count.
- **Docs and tests:** the `Dup` column is added to `docs/guides/code_check/js_complexity.md`, the `long_help` text and `docs/agents/tingle-js-complexity-image.md`. Python tests cover the column with a number, `0` and `null`, `PARSE` rows, and the path-less jscpd warning with an unchanged exit code.

## Solution
The image and the Python side change **in the same PR**. The image is published under the same tingle tag, so the CLI and the image stay in sync. The duplicated-block fixture (`dup_a.js`/`dup_b.js`) is already in `docker/js_complexity/fixture/`.

Depends on the release pipeline (#319) and subcommand core (#320) sub-issues, which are both merged.

### Agents
- `shell`: `package.json`/lock, the entrypoint (a new `lib/jscpd.js` next to `lib/fta.js`), the Docker Hub description and the smoke test.
- `python`: the reporter column, the warning, `long_help` and the tests.
- `guide`: `docs/guides/code_check/js_complexity.md`.
- `product-owner`: `docs/agents/tingle-js-complexity-image.md`.

## Benefits
- The report matches what RubyCritic gives Ruby users: complexity plus duplication.
