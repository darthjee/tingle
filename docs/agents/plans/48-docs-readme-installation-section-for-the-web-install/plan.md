# Plan: Docs: README installation section for the web install

Issue: [48-docs-readme-installation-section-for-the-web-install.md](../../issues/48-docs-readme-installation-section-for-the-web-install.md)

## Overview
Add an `## Installation` section to `README.md` documenting the
`curl | bash` web install (one-liner, override env vars, prerequisites,
`source ~/.bashrc` note), and adjust the existing `## Commands` prose and
`## Scripts` table so they read correctly alongside it. Docs-only — no
behavior change.

## Context
This is the third of three sub-issues splitting #45. Sub-issue 1 (#46)
publishes the release zip; sub-issue 2 (#47) adds `install/bootstrap.sh` and
`install/installer.sh`, which implement the exact behavior this section
describes: `TINGLE_REPO` / `TINGLE_VERSION` / `TINGLE_ASSUME_YES` overrides,
install to `~/.tingle`, then `exec "<target>/bin/tingle" install` to wire
`~/.bashrc`. This issue must land after #46 and #47 merge, and the wording
must match their actual shipped behavior rather than this plan's description
of it.

Today `README.md` has no Installation section — the only install-related
content is the `install` row in the `## Scripts` table (`README.md:43`) and
the `tingle install` paragraph under `## Commands` (`README.md:61-65`), both
of which assume an already-cloned repo.

## Implementation Steps

### Step 1 — Add the `## Installation` section
Insert a new `## Installation` section into `README.md`, placed right after
the intro (before `## Name Origin`) so it's the first thing a visitor without
the repo sees. Content:
- The one-liner:
  ```
  curl -fsSL https://raw.githubusercontent.com/darthjee/tingle/main/install/bootstrap.sh | bash
  ```
- One or two sentences on what it does: downloads the pinned release zip,
  unpacks it to `~/.tingle`, and wires `tingle` into `~/.bashrc` via
  `tingle install`.
- Override env vars as one-off command prefixes (not `export`):
  `TINGLE_VERSION` (pin a release), `TINGLE_REPO` (install from a fork),
  `TINGLE_ASSUME_YES` (skip the `y/N` prompt) — e.g.
  `TINGLE_VERSION=v0.1.0 curl -fsSL ... | bash`.
- Prerequisites: `curl`, `unzip`, `bash`; `jq` for `bin/tingle`; `docker` for
  `tingle linux`.
- A closing note: installs to `~/.tingle`; run `source ~/.bashrc` (or start a
  new shell) afterward.

Verify the exact flag names/behavior against the merged `install/bootstrap.sh`
and `install/installer.sh` (sub-issue 2) before writing final wording, not
against this plan.

### Step 2 — Refresh `## Commands` / `## Scripts` references
- In the `## Scripts` table, leave the existing `install` row
  (`README.md:43`, `shell/install/executor.sh` — unchanged behavior) as-is;
  no new row for `install/bootstrap.sh`/`install/installer.sh`, since they
  are covered by the new `## Installation` section rather than being a
  `tingle` subcommand.
- In the `## Commands` paragraph about `tingle install` (`README.md:61-65`),
  clarify that this is the shell-wiring step the web installer finishes with
  (i.e. `install/installer.sh` ends by running `tingle install`), so the two
  sections read as one coherent flow rather than two unrelated install paths.

## Files to Change
- `README.md` — add `## Installation` section; adjust `## Commands` prose
  around `tingle install`.

## Notes
- Blocked on #46 and #47 merging first — this plan's exact wording (flag
  names, default dir, prompt behavior) must be checked against their final
  shipped scripts before implementation, not assumed from this plan or from
  the sub-issue 2 draft.
- No CI job covers `README.md` (`.circleci/config.yml` only runs Python
  lint/tests and the release-image jobs) — no `## CI Checks` section needed.
  Manual verification: `README.md` renders correctly on GitHub, the
  one-liner is copy-pasteable, and the override examples match the flags
  actually implemented in #47.
