# Product-owner Plan: linux: user docs, Docker Hub descriptions and release 0.1.0

Main plan: [plan.md](plan.md)

## Shared contracts

- Version `0.1.0` (set by the architect via `scripts/bump-version.sh 0.1.0`).
- User-facing tool list and host-integration details live in
  `docs/guides/linux.md` (`## What's inside the shell`). The agent doc keeps
  the implementation view and may link to the guide.

## Implementation Steps

### Step 1 — Final consistency pass over `docs/agents/tingle-linux-image.md`
Check the doc against what #232–#235 shipped (`shell/linux/Dockerfile`,
`entrypoint.sh`, `executor.sh`, `docker_run.sh`, `completion.sh`,
`scripts/release_image.sh`, `.circleci/config.yml`) and fix drift:
- Banner bullet: "`<VERSION>` is read from `shell/linux/VERSION`
  (`0.0.3` since #235)" → `0.1.0`, first released version with the toolbox
  and host integration.
- "Bumping versions": state that the release version lives in three places
  kept in sync by `scripts/bump-version.sh` (README, `install/bootstrap.sh`,
  `shell/linux/VERSION`), so `VERSION` must not be hand-edited alone (#235 did
  that, leaving `0.0.3` untagged). Include keeping `LINUX_TOOLS`, the
  Dockerfile header, this doc's toolbox groups, the guide's
  "What's inside the shell" and `DOCKERHUB_DESCRIPTION.md` in sync when
  tools change.
- Confirm the toolbox groups, tag strategy, entrypoint/hardening and
  host-integration table still match the code. Change only what's wrong.
- Add a short pointer to the user guide for the user-facing view.

## Files to Change
- `docs/agents/tingle-linux-image.md` — version reference, version-sync rule, tool-list sync list, guide pointer, any drift found

## Notes
- If `docs/agents/architecture.md` or `docs/agents/flow.md` mention the image
  contents or the release flow in a way that is now wrong, fix them in the
  same pass. Otherwise leave them alone.
