## Description
Third of three sub-issues splitting #45 (`Add tingle web install (curl | bash)`).
Documents the web install in `README.md` so it is discoverable — the user-facing
half of #45. Lands last, once sub-issues 1 and 2 have defined the real behavior
this section describes.

## Problem
`README.md` has no "Installation" section at all. The only install path it
mentions is `tingle install` under `## Commands`, which assumes an already-cloned
repo. A visitor has no documented way to get `tingle` without cloning.

## Expected Behavior
- `README.md` gains an **Installation** section (placed before `## Structure` or
  right after the intro) containing:
  - The one-liner:
    ````
    curl -fsSL https://raw.githubusercontent.com/darthjee/tingle/main/install/bootstrap.sh | bash
    ````
  - What it does, in one or two sentences: downloads the pinned release zip,
    unpacks it to `~/.tingle`, and wires `tingle` into `~/.bashrc` via
    `tingle install`.
  - The override env vars, shown as one-off command prefixes (not `export`):
    `TINGLE_VERSION` (pin a release), `TINGLE_REPO` (install from a fork),
    `TINGLE_ASSUME_YES` (skip the `y/N` prompt).
  - Prerequisites: `curl`, `unzip`, `bash`; `jq` for `bin/tingle`; `docker` for
    `tingle linux`.
  - A note that it installs to `~/.tingle` and that `source ~/.bashrc` (or a new
    shell) is needed afterward.
- `## Scripts` / `## Commands` are refreshed so the `install` row and the
  `tingle install` paragraph read correctly alongside the new section (e.g.
  clarify that `tingle install` is the shell-wiring step the web installer
  finishes with).
- No behavior change — docs only.
- Manual verification: `README.md` renders correctly on GitHub; the one-liner is
  copy-pasteable; the override examples match the flag names implemented in
  sub-issue 2.

### Edge cases
- **Wording must match reality** — the env var names, default install dir, and
  prompt behavior must match what sub-issue 2 actually shipped; write this
  section against the merged sub-issue 2, not against this issue's description.
- **`AGENTS.md` says new scripts get a `README.md` table row** — decide whether
  `install/bootstrap.sh` warrants a `## Scripts` row or is covered by the new
  Installation section (likely the latter, since it is not a `tingle`
  subcommand).

## Solution
- Edit `README.md` only: add the `## Installation` section and adjust the
  `## Scripts` table / `## Commands` prose as needed.
- Keep the house voice of the existing README (short, plain, example-first).

### Scope
- `README.md`.

### Out of scope
- `install/bootstrap.sh` / `install/installer.sh` behavior — sub-issue 2.
- CI / zip packaging — sub-issue 1.
- `docs/agents/` documentation — covered by sub-issue 1's packaging note and
  owned by `product-owner`.

### Dependencies
- **Depends on sub-issues 1 and 2** — it documents their finished behavior;
  should be written/merged after both.

### Responsible agent(s)
- `architect` — owns root-level files including `README.md`.

## Benefits
- Makes the web install discoverable — without it, the whole feature is
  effectively hidden.
- Gives users the supported override knobs in one place.
