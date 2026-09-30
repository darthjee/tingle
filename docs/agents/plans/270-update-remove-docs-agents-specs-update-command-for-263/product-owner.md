# Product-owner Plan: update: remove docs/agents/specs/update_command/ for #263

Main plan: [plan.md](plan.md)

## Shared contracts

- Runs **last**, after guide, shell, cli and architect have filled their
  gaps.
- `"manifest": []` means the install does not track hashes.
  `version: "unknown"` is always out of date.

## Implementation Steps

### Step 1 — Fill the gaps in docs/agents/tingle-release-zip.md
Check each point against `scripts/release_cli.sh`, `install/installer.sh`
and `install/manifest.sh`:
- Name the algorithm as SHA-256, computed with the `sha256sum` /
  `shasum -a 256` fallback over the same file that is zipped
  (manifest-hashes.md:31-33, README.md:126-129).
- `MANIFEST` holds the plain path, never `sha256sum`'s `\`-escaped
  form. Paths containing a newline are unsupported
  (manifest-hashes.md:114-116).
- Paths are JSON-escaped (backslashes and double quotes) in `tingle.json`
  (manifest-hashes.md:45-47, 112-113).
- A corrupt `tingle.json` (unparseable, a missing field, or `manifest`
  not an array) is refused (README.md:116-117).
- `"manifest": []` means the install does not track hashes
  (manifest-hashes.md:117-118).
- `version` defaults to `"unknown"`, which is always out of date
  (installer.sh:130-131, README.md:194).

### Step 2 — Delete the specs and update the index
- `git rm -r docs/agents/specs/update_command/`. Git tracks no empty folders, so this removes
  `docs/agents/specs/` completely.
- In `docs/agents/specs.md`, replace the "Current specs" table (the header
  and the `update_command` row) with `No specs in progress.`, as after
  #254. Leave everything above it unchanged.
- Check that `git grep specs/update_command` returns nothing.

## Files to Change
- `docs/agents/tingle-release-zip.md`: the gaps above.
- `docs/agents/specs/update_command/README.md`, `installer-update-mode.md`, `manifest-hashes.md`,
  `update-command.md`: deleted.
- `docs/agents/specs.md`: the table replaced.

## Notes
- `AGENTS.md`, `CLAUDE.md`, `docs/agents/folder-structure.md` and
  `.claude/agents/product-owner.md` describe `specs/` generically. They
  stay as they are.
- The PR body must contain `Fix #270` and `Closes #263`.
