## Description
Part of #263. Write the specs for the whole `tingle update` idea under
`docs/agents/specs/update_command/`, following the conventions in
[`docs/agents/specs.md`](docs/agents/specs.md). The implementation
sub-issues of #263 (#264, #265, #266, #267) implement against these specs.

The specs cover both the user-visible behaviour **and** the key technical
decisions recorded in #263 (approach, edge cases E1–E15, self-replacement
safety S1–S3, atomicity phases, latest-release resolution), so the
implementation sub-issues just follow them. The source of truth for the
content is the body of #263.

**Merge order:** this lands **first**, before #264.

## Problem
The decisions for `tingle update` currently live only in the body of #263.
#264–#267 are implemented by different agents (architect, shell, cli,
guide), and several contracts span them: the `tingle.json` schema, the
installer update-mode env vars, the version rules. Without one agreed spec
in the repo, each sub-issue could interpret #263 differently.

## Expected Behavior
### Layout
The idea is split across files as needed rather than one large file. The
proposed split is below; the author may adjust it, but each file must be
readable on its own.

### `docs/agents/specs/update_command/README.md` (shared contracts)
- Overview, links to the parent #263 and to every sub-issue, and the merge
  order: #269 (specs) → #264 → #265 → #266 → #267 → #270 (specs
  cleanup). #264–#266 must all be merged
  before the **0.4.0** tag.
- Scope: in and out of scope, including the git-clone follow-up (#268).
- The rules for #267: what `docs/guides/update.md` must cover, and the new
  "run `tingle update`" message in `install/installer.sh`. There is no
  separate spec file for the user guide.
- Shared contracts every sub-issue must agree on:
  - the `MANIFEST` line format (`<hash>  <path>`) and the `tingle.json`
    schema (`{path, sha256}` manifest entries, plus reading the old
    path-only format; "tracks hashes" decided by format, not version);
  - the installer update-mode env vars: `TINGLE_UPDATE_TARGET`,
    `TINGLE_UPDATE_FORCE`, `TINGLE_REPO`, `TINGLE_VERSION`;
  - the `tingle update` CLI: `[--check] [--force] [<version>]`,
    `TINGLE_VERSION`, `TINGLE_ASSUME_YES`;
  - the test-only hooks `TINGLE_RELEASE_API_URL` and
    `TINGLE_RELEASE_BASE_URL`, and their defaults;
  - the version rules: `X.Y.Z` or `X.Y.Z-<suffix>`, the 0.4.0 floor,
    `"unknown"` treated as out of date;
  - exit codes and "nothing changed" guarantees.

### One spec per feature (proposed)
- `manifest-hashes.md` (#264): the `MANIFEST` and `tingle.json` formats,
  portable hashing (`sha256sum` / `shasum -a 256`), and the two-format reader.
- `installer-update-mode.md` (#265): the trigger, and the preflight / stage /
  swap / prune / commit / wire phases. Also the edited-file check (E1,
  including the incoming-hash rule), S2 and S3, the lock and stale-lock
  handling (E15), E3, E5, E11–E13, and recovery by re-running.
- `update-command.md` (#266): the CLI, resolving the latest release through
  the GitHub API, pins and the 0.4.0 floor, `--check`, `--force`, the
  up-to-date no-op, the y/N prompt, download plus `.sha256` check, the test
  hooks, the `exec` handoff (S1), the git-checkout and unknown-install
  messages, and E2, E4, E6–E10, E14.
- Each spec must include behaviour, examples, edge cases, technical decisions,
  rejected alternatives where #263 recorded them, and test expectations.

### Permanent docs the specs must point to
Specs are temporary, so each spec must name the **permanent** docs its
implementation sub-issue has to update, so nothing is lost when the specs
folder is removed:
- `docs/agents/tingle-release-zip.md` documents `MANIFEST` as a sorted
  (`LC_ALL=C`) path-only list. #264 must update it to the `<hash>  <path>`
  format (keeping the `LC_ALL=C` sort by path) and describe the new
  `tingle.json` schema.
- The `install/installer.sh` and `shell/update/` header comments, and
  `long_help` in `commands/shell.json`, are the permanent home for the
  update-mode env vars, the test-only hooks and the CLI.
- `docs/guides/update.md` (#267) is the permanent home for user-visible
  behaviour.
- #270 removes the specs once everything is merged, after checking these
  permanent homes cover them. So the specs must be complete enough for that
  check.

### `docs/agents/specs.md`
Add an `update_command` row to **Current specs** (Topic, Specs, Parent issue,
Sub-issues), linking `docs/agents/specs/update_command/README.md`, #263 and
the sub-issues (#264–#267, #269, #270). #270 removes the row.

### Style
Specs are normative: write "must" / "is", not "could" / "might".

## Solution
- `product-owner` agent: write `docs/agents/specs/update_command/*.md` and
  the new row in `docs/agents/specs.md`.
- No code changes.

## Benefits
- The sub-issues share one agreed contract, so the installer update mode
  and the `tingle update` command can be built against the same env vars,
  formats and phases.
- The decisions from #263 live in the repo while the work is in progress,
  not only in a GitHub issue body.
