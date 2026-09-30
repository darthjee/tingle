# Product-owner Plan: code_check: clean up stale check_file_size mentions in docs and tests

Main plan: [plan.md](plan.md)

## Shared contracts

None. After the change, `check_file_size` may be mentioned only as the deprecated
alias, the legacy config key, or in migration notes.

## Implementation Steps

### Step 1 — Update the shim note in architecture.md

In `docs/agents/architecture.md`, in the `code_check` section (the bullet that
starts "When an existing command becomes a subcommand", around line 138), replace
"with unchanged behaviour and no deprecation warning" with text that says the shim:

- prints `Warning: 'tingle check_file_size' is deprecated; use 'tingle code_check file_size'.`
  on stderr;
- keeps stdout and exit codes unchanged;
- is kept until a future issue removes the alias.

The completion note around line 56 ("the `check_file_size` alias, `install`") is
still correct, so leave it as it is.

### Step 2 — Sweep for other stale mentions

Run:

```bash
grep -rn check_file_size --exclude-dir=.git --exclude-dir=.codacy --exclude-dir=issues --exclude-dir=plans .
```

Fix anything in `docs/agents/`, `AGENTS.md` or `README.md` that still calls
`check_file_size` the current command, or that describes the alias without its
deprecation warning. The last check found no others: the `README.md` table row
and the guides already describe the alias as deprecated.

## Files to Change

- `docs/agents/architecture.md` — update the shim note to describe the deprecation warning.

## Notes

- Do not edit `docs/agents/issues/` or `docs/agents/plans/`, because they are historical records.
- Update the `Last updated` line only if the file already has one.
