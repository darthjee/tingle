# architect Plan: Docker: script-ify the tingle-linux release build and add a build-needed check

Main plan: [plan.md](plan.md)

## Shared contracts

- Produces `scripts/release_image.sh`, which `shell`'s `docker_run.sh`
  relies on indirectly only insofar as both must agree on the
  `darthjee/tingle:<tag>` image reference convention and on
  `shell/linux/VERSION` being the source of truth for `<tag>` — see the
  full contract in [plan.md](plan.md)'s `## Shared contracts`.
- Consumes `shell/linux/VERSION` (created by `shell`) to determine the
  build tag locally and to validate `$CIRCLE_TAG` in CI.

## Steps

- [01 — Write scripts/release_image.sh](architect/01-write-release-image-script.md)
- [02 — Rewire .circleci/config.yml to call the script](architect/02-rewire-circleci-config.md)
- [03 — Tighten DOCKERHUB_DESCRIPTION.md's tag wording](architect/03-fix-dockerhub-description-wording.md)

## CI Checks

No CI job currently covers `.circleci/config.yml` or `scripts/` changes
themselves (the `test` workflow only runs the Python `lint`/`tests` jobs;
the `release` workflow only runs on a real `v*` tag push). Verify locally:
- `bash -n scripts/release_image.sh` (syntax check) and, if `shellcheck` is
  available, `shellcheck scripts/release_image.sh` — no CI job enforces
  this yet, but `docs/agents/contributing.md` names `shellcheck` as the
  expected tool for Shell scripts.
- End-to-end verification requires actually pushing a `v*` tag, per the
  issue's "Manual verification" note — not something a local check can
  substitute for.

## Notes

- The CI job/workflow structure itself (job names, `requires:`, tag
  filters) does not change — only the `run:` step bodies move into script
  calls.
- `scripts/release_image.sh` must work identically whether invoked from CI
  (`$CIRCLE_TAG` set) or locally on a dev machine (`$CIRCLE_TAG` unset,
  falls back to reading `shell/linux/VERSION` directly) — see Edge cases in
  the issue file.
