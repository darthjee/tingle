# Point the root README to the guides

Replace the body of the root `README.md` "Usage" section ("Each script is
independent and can be run directly. Check each script's header for usage
instructions and dependencies.") with a pointer to
[`docs/guides/README.md`](docs/guides/README.md), the per-command user
guides. You may keep a short mention of `tingle --help <command>`. Do not
link the Scripts table rows to individual guides; the per-command
sub-issues do that.

## Files to Change
- `README.md` — rewrite the "Usage" section to point to the guides index.
