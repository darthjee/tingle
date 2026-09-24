# Product-owner Plan: Docker: set Docker Hub short description, refresh DOCKERHUB_DESCRIPTION.md and harden update-description

Main plan: [plan.md](plan.md)

## Shared contracts

- Relies on the `shell` agent to produce `DOCKERHUB_SHORT_DESCRIPTION.txt`
  (one line, at most 100 characters) and `DOCKERHUB_DESCRIPTION.md` at repo
  root.
- On release tags, `scripts/release_image.sh update-description` pushes both
  files: the short file as `description` and the Markdown as
  `full_description`. It fails the job on missing files, an over-long
  summary, or HTTP errors.

## Implementation Steps

### Step 1 — Document the Docker Hub description in `tingle-linux-image.md`
Add a **Docker Hub description** bullet to
`docs/agents/tingle-linux-image.md`. It should say:
- the short description lives in `DOCKERHUB_SHORT_DESCRIPTION.txt` and is
  limited to 100 characters
- the full description lives in `DOCKERHUB_DESCRIPTION.md`
- `scripts/release_image.sh update-description` pushes both, through the
  `update-description` CircleCI job on release tags
- Docker Hub links must be absolute URLs

Also extend the **Release script** bullet to list `update-description`
alongside build, smoke test, and publish. Reword the "published manually"
phrase in **Tag strategy** so it's clear that the git tag is pushed by hand
and CircleCI then builds and publishes the image.

## Files to Change
- `docs/agents/tingle-linux-image.md`: document both description files, the
  push mechanism, and the corrected tag-strategy wording

## Notes
- `docs/agents/folder-structure.md` lists folders, not individual root
  files, so it needs no change.
