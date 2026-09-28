# Add the permanent specs index
Create `docs/agents/specs.md`. It is **permanent**: #254 removes only the `check_file_size` entry, not this file.

Content:
- What specs are: temporary, feature-level design documents for a split issue. They live under `docs/agents/specs/<topic>/` (a `README.md` with the shared contracts, plus one file per feature) while the sub-issues are in progress, and are removed by the split's final cleanup sub-issue once the user guide and code cover everything.
- Conventions: folder name = the command/topic (e.g. `check_file_size`); link the parent GitHub issue; a new split adds an entry here, and its cleanup removes it.
- A "Current specs" table: `check_file_size` → [`specs/check_file_size/README.md`](specs/check_file_size/README.md), parent issue #247, sub-issues #249–#254.

Also add `specs.md` / `specs/` to the `docs/agents/` row in `docs/agents/folder-structure.md` (it currently says "architecture, flow, plans, issues").

## Files to Change
- `docs/agents/specs.md` — new permanent index.
- `docs/agents/folder-structure.md` — mention specs in the `docs/agents/` row.
