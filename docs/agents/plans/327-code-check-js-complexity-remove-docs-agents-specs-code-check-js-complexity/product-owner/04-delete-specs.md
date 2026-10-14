# Delete the specs and their index row
Run this last, after the shell, python and architect repoints.

- Delete `docs/agents/specs/code_check/js_complexity/` and the now-empty
  `docs/agents/specs/code_check/` folder.
- In `docs/agents/specs.md`, remove the `code_check js_complexity` row from
  the Current specs table, keep the table header and add `None currently.`
  below it, as #298 left the file (`git show 6f84b0b -- docs/agents/specs.md`).
  The issue calls this "No specs in progress."; the #298 wording wins for
  consistency.
- Run the verification grep from [plan.md](../plan.md#shared-contracts). It
  must print nothing.

## Files to Change
- `docs/agents/specs/code_check/js_complexity/` — deleted (10 files).
- `docs/agents/specs.md` — row removed, `None currently.` restored.
