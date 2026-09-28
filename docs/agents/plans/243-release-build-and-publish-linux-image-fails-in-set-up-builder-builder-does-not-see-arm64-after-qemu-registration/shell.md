# Shell Plan: release: build-and-publish-linux-image fails in "Set up builder" — builder does not see arm64 after QEMU registration

Main plan: [plan.md](plan.md)

## Shared contracts

Implement the `setup-builder` steps exactly as written in [plan.md](plan.md#shared-contracts): check → register → stop and check again → remove, recreate and check again → fail. Keep these the same:
- the log lines `Restarting builder tingle-builder to detect new platforms` / `Recreating builder tingle-builder to detect new platforms`;
- the final `Builder tingle-builder ready for: <csv>`;
- the `Builder tingle-builder still does not support: <archs>` error (stderr, exit 1).

`product-owner` documents the same steps in `docs/agents/tingle-linux-image.md`.

## Implementation Steps

### Step 1 — Re-detect platforms after QEMU registration
In `cmd_setup_builder` (`scripts/release_image.sh:137`), keep the create-if-missing and the first `missing_platform_archs` check unchanged. Also keep the early success when nothing is missing, so there's no privileged container and no restart on Docker Desktop or on re-runs.

After `docker run --privileged --rm "$BINFMT_IMAGE" --install "$missing"`:
1. `echo "Restarting builder $BUILDER_NAME to detect new platforms"`, `docker buildx stop "$BUILDER_NAME"`, then `missing=$(missing_platform_archs)` (its `inspect --bootstrap` starts the container again).
2. If `$missing` is still not empty: `echo "Recreating builder $BUILDER_NAME to detect new platforms"`, `docker buildx rm "$BUILDER_NAME"`, `docker buildx create --name "$BUILDER_NAME" --driver docker-container`, then `missing=$(missing_platform_archs)`.
3. If it's still not empty, keep the existing `still does not support` error and `exit 1`.

Keep it readable. For example, pull the create call into a small `create_builder` helper used by both the initial create and the recreate, so the `--driver docker-container` flags live in one place. Don't change `missing_platform_archs`'s matching logic; that's #244.

Update the header comment's `setup-builder` paragraph (`scripts/release_image.sh:21-24`) to describe the real order: it creates and starts the builder, registers QEMU only for missing platforms, then stops the builder so BuildKit checks platforms again, and recreates it once as a fallback (the only path that loses the cache). Note that a restart interrupts any build using the builder at that moment, and that Docker Desktop still runs no privileged container.

### Step 2 — Add a `setup-builder` CI job to the `test` workflow
In `.circleci/config.yml`, add a `setup-builder` job and list it under `workflows.test.jobs` next to `lint` and `tests` (no filters, so it runs on every branch):

```yaml
  setup-builder:
    machine:
      image: ubuntu-2404:current
    steps:
      - checkout
      - run:
          name: Set up builder
          command: scripts/release_image.sh setup-builder
```

It needs no credentials and publishes nothing. Don't change the `build-and-publish-linux-image` job or the `release` workflow.

## Files to Change
- `scripts/release_image.sh` — `cmd_setup_builder` restart/recreate logic, an optional `create_builder` helper, and the `setup-builder` paragraph of the header comment.
- `.circleci/config.yml` — new `setup-builder` job and its entry in the `test` workflow.

## CI Checks
- `scripts/release_image.sh`: `shellcheck scripts/release_image.sh` (no CI job yet — see `docs/agents/todo.md`) and `bash -n scripts/release_image.sh`.
- `.circleci/config.yml`: `circleci config validate` if the CLI is available locally.
- `setup-builder` (the new CI job) on the PR is the real check. It must pass on the fresh `ubuntu-2404:current` machine.

## Notes
- The fix can't be reproduced on Docker Desktop (QEMU is built in). The new CI job is the check. If possible, the PR's CI history should show the job failing with `still does not support: arm64` before the fix and passing after it. Say in the PR description which path (restart or recreate) fixed it, based on the job log.
- If the log shows that `buildx stop` alone isn't enough, the recreate fallback covers it. No further change is needed.
- Out of scope: pinning binfmt by digest, platform-matching fixes (#244), recovering the 0.2.0 release, and any other change to the release job.
