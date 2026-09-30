# Architect Plan: update: remove docs/agents/specs/update_command/ for #263

Main plan: [plan.md](plan.md)

## Shared contracts

- Code is the truth: `install/update.sh` `update_main` sets the preflight
  order.
- `version: "unknown"` installs do not track hashes.

## Implementation Steps

### Step 1 — Fix the install/installer.sh header comment
Comments only:
- Preflight order (header :34-41): the code checks the target folder
  (`update_check_target`) **before** taking the lock (`update_take_lock`).
  Reorder the bullets to match, and reword "nothing changes except the lock"
  if needed.
- Optional: next to "decided by format", note that a `version: "unknown"`
  install has no hashes (installer-update-mode.md:83).

## Files to Change
- `install/installer.sh`: header comment only.

## CI Checks
- `bash -n install/installer.sh`.

## Notes
- `install/` is root-level config (AGENTS.md:40-41), so the architect owns
  it, as the issue's Solution says. This is the only coordinator-owned work
  in the plan.
