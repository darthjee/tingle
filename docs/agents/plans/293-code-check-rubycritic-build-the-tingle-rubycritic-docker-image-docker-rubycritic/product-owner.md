# Product Owner Plan: code_check rubycritic: build the tingle_rubycritic Docker image (docker/rubycritic/)

Main plan: [plan.md](plan.md)

## Shared contracts

- The new top-level folder is `docker/`, with one sub-folder per check image.
  The first is `docker/rubycritic/`, and the `shell` agent owns it.
- The folder description to use: "Docker images for `tingle code_check`
  checks, one sub-folder per image (`docker/rubycritic/` builds
  `tingle_rubycritic`). Owned by the `shell` agent."

## Implementation Steps

### Step 1 — Add `docker/` to the folder-structure table

Add a `docker/` row to the "Project Root" table in
`docs/agents/folder-structure.md`, after `scripts/` / `dist/` and before
`shell/`. Use the shared description. Do not create a
`docs/agents/tingle-rubycritic-image.md` page yet: until #298 removes the
specs, they stay the source of truth.

## Files to Change

- `docs/agents/folder-structure.md`: add the `docker/` row.

## CI Checks

- Codacy runs `markdownlint` on the changed Markdown. No CircleCI job applies.

## Notes

- Keep the table's column alignment the same as the rows around it.
