# Guide Plan: update: support updating git-clone installs (git pull)

Main plan: [plan.md](plan.md)

## Shared contracts

This agent relies on the messages and exit codes in the table in [plan.md](plan.md#shared-contracts), and should quote the user-visible lines exactly as they appear there.

## Implementation Steps

### Step 1 — Document the git-checkout path in `docs/guides/update.md`
- Update the intro and the "What it does" section: the command now handles both web installs and git checkouts. Replace the "**Git checkouts are not updated.**" block.
- Add an "Updating a git checkout" section covering: `git pull --ff-only` on the current branch followed by re-running `tingle install`; the up-to-date message; `--check` output (behind/ahead); and each refusal (uncommitted tracked changes, detached HEAD, no upstream, diverged branch, a version pin with the "check out a tag yourself" hint, `--force`) with its message and how to fix it. It should also say that there is no confirmation prompt and that untracked files are fine.
- Prerequisites: `git` for git checkouts; `curl`, `unzip`, `jq` and `sha256sum`/`shasum` for web installs only.
- Scope the existing pin, `--force`, confirmation and checksum sections explicitly to web installs.

### Step 2 — Check cross-links
Update any wording in `docs/guides/README.md` or `docs/guides/install.md` that says git checkouts must be updated by hand.

## Files to Change
- `docs/guides/update.md` — the git-checkout documentation.
- `docs/guides/README.md`, `docs/guides/install.md` — only if they mention updating a git checkout manually.
