# Guide Plan: linux: tab completion does not offer subcommands (shell, sed)

Main plan: [plan.md](plan.md)

## Shared contracts

- **Relies on** the linux handler protocol in `plan.md`: `tingle linux <TAB>` offers `shell` and `sed`, `tingle linux sed <TAB>` completes file and folder names, and `tingle linux shell <TAB>` offers nothing.

## Implementation Steps

### Step 1 — Mention Tab completion in the linux guide
In `docs/guides/linux.md`, right after the code block in `## Usage`, add a short paragraph in the style of `docs/guides/kube.md` ("If you enabled bash completion with `tingle install`, pressing Tab ..."). Say that Tab completes the `shell` and `sed` subcommands, and file and folder names for `sed` arguments.

## Files to Change
- `docs/guides/linux.md` — Tab-completion note under Usage.
