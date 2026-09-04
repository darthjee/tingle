# Issue: Docker: script-ify the tingle-linux release build and add a build-needed check

## Description

`build-and-publish-linux-image` in `.circleci/config.yml` currently inlines
build/smoke-test/publish bash directly in the CI YAML, and rebuilds +
republishes the `darthjee/tingle` image on every `v*` tag regardless of
whether `shell/linux/` actually changed since the previous release.

This extracts that logic into a script (`scripts/release_image.sh`),
invoked from a slimmer `.circleci/config.yml`, and adds a build-needed
guard so a release tag that doesn't touch `shell/linux/` no-ops instead of
rebuilding/republishing an identical image.

While investigating, a related bug surfaced: `shell/linux/docker_run.sh`
hardcodes `TINGLE_LINUX_IMAGE="darthjee/tingle:0.0.1"`, which matches
neither CI's actual published tag format (`$CIRCLE_TAG`, e.g. `v1.0.0`,
with a `v`) nor the docs (`docs/agents/tingle-linux-image.md` claims plain
semver, `1.0.0`, no `v`). Three different conventions exist today with
nothing keeping them in sync. This issue folds in fixing that drift too,
since a "the image exists and is current" guarantee is hollow if the CLI's
own consumer pins the wrong tag.

Scoped-down relative to the general build-script pattern this is modeled
on: no multi-image/arch `requires:` fan-out (tingle has one image and one
downstream job, `update-description`, which already correctly `requires:`
the build job), and no separate "is this a release" script check (already
handled by the workflow's `filters: tags: only: /v.*/`).

Confirmed via Docker Hub's public API
(`GET /v2/repositories/darthjee/tingle/tags` → `"object not found"`): the
`darthjee/tingle` repository does not exist on Docker Hub at all yet. No
image has ever actually been published through this pipeline (no `v*` git
tag has ever been pushed either). So `tingle linux` is currently
non-functional for any real user today, since `docker_run.sh` points at an
image that was never published — this issue doesn't cause that breakage,
but it also doesn't fix it: a human still needs to push the first real
`v0.0.1` tag after this merges to make `tingle linux` actually work. That
first release is an operational follow-up, not part of this issue's scope.

## Expected Behavior

- `.circleci/config.yml`'s `build-and-publish-linux-image` **and**
  `update-description` jobs both delegate to `scripts/release_image.sh`;
  no bash logic beyond simple invocations remains inline in the YAML for
  either job (the Docker Hub description push currently inlined in
  `update-description` moves into the same script, e.g. as a separate
  subcommand).
- When a `v*` tag is pushed but nothing under `shell/linux/` changed since
  the previous `v*` tag, the release script no-ops successfully (the CI job
  still goes green — a "nothing to do" success, not a failure) and does
  **not** rebuild/republish the image.
- When `shell/linux/` did change (or this is the first-ever release tag),
  the script builds, smoke-tests (GNU sed check + non-root check, same as
  today), and publishes as before.
- A single pin file (`shell/linux/VERSION`, containing just the tag, e.g.
  `v1.0.0`) becomes the one source of truth for "what tag is currently
  published":
  - the CI script validates that this pin file's value matches
    `$CIRCLE_TAG` before publishing (hard-fails the job on mismatch — no
    build, no publish — catching someone tagging without bumping the pin),
    and
  - `shell/linux/docker_run.sh` reads the image reference from this same
    file instead of the current hardcoded `0.0.1`.
- `docs/agents/tingle-linux-image.md` and `DOCKERHUB_DESCRIPTION.md` are
  reconciled to state one consistent tag convention (the `v`-prefixed one
  CI actually produces, e.g. `v1.0.0`), and mention `shell/linux/VERSION`
  as the source of truth.
- Manual verification: push a no-op `v*` tag (nothing under `shell/linux/`
  changed) and confirm the release job completes without a new Docker Hub
  push; then change `shell/linux/Dockerfile` and push another `v*` tag and
  confirm it does build+publish, `docker_run.sh` picks up the new pin, and
  `docker run darthjee/tingle:<new-tag> sed --version` still passes the
  existing smoke-test assertions.

### Edge cases

- **No git tag has ever actually been pushed in this repo** (`git tag`
  returns empty today). So "first-ever release" is the guaranteed real
  state the very first run of this pipeline will hit, not a rare fallback:
  the change-detection guard's no-previous-tag path must proceed
  unconditionally.
- **`shell/linux/VERSION` / `$CIRCLE_TAG` mismatch**: hard fail, nothing
  built or published. Recovery: fix `VERSION`, commit it, then push a new
  (or corrected) tag — the script never auto-corrects or publishes under a
  mismatched tag.
- **Local invocation without `$CIRCLE_TAG`** (e.g. running
  `scripts/release_image.sh build` on a dev machine): `shell/linux/VERSION`
  is the primary source of truth for which tag to build; `$CIRCLE_TAG` is
  only used in CI to *validate against* that file. Keeps local and CI
  invocations of the same script consistent.
- **A tag that reverts `shell/linux/` to an earlier state**: `git diff
  --quiet <prev-tag>..HEAD -- shell/linux/` still shows a non-empty diff (a
  revert is a real change relative to the immediately preceding release),
  so it correctly triggers a rebuild — no special-casing needed.
- **Initial `shell/linux/VERSION` seed value**: `v0.0.1` — preserves
  continuity with the existing (never actually published) `0.0.1`
  placeholder, corrected to the `v`-prefixed convention CI actually
  produces.

## Solution

- New `scripts/release_image.sh` (new top-level `scripts/` directory —
  `bin/` stays reserved for the CLI's own dispatch layer per
  `docs/agents/architecture.md`), dispatched by subcommand:
  - a change-detection function (find the previous `v*` tag via
    `git tag --sort=-creatordate`, then `git diff --quiet <prev>..HEAD --
    shell/linux/`), called at the top of the build/publish entry points so
    each is independently a safe no-op.
  - a pin-file validation step (compare `shell/linux/VERSION` to
    `$CIRCLE_TAG`, hard-failing on mismatch).
  - build, smoke-test, and publish logic moved from the current inline
    `run:` blocks in `.circleci/config.yml`.
- `.circleci/config.yml`: both `build-and-publish-linux-image` and
  `update-description` job steps become thin calls into
  `scripts/release_image.sh <subcommand>` (e.g. `build`, `publish`,
  `update-description`). Keep `update-description`'s existing
  `requires: [build-and-publish-linux-image]` — that wiring is already
  correct and doesn't need to change.
- `docs/agents/folder-structure.md`: add the new top-level `scripts/`
  directory to its table, same as any other root-level folder — it's
  currently undocumented there.
- `shell/linux/docker_run.sh`: replace the hardcoded
  `TINGLE_LINUX_IMAGE="darthjee/tingle:0.0.1"` with a read from
  `shell/linux/VERSION`.
- `shell/linux/VERSION` (new file, seeded to `v0.0.1`): single line, the
  currently-published tag, bumped manually as part of cutting each release
  (same manual-release model as today — just one authoritative place to
  bump instead of three drifting conventions).
- Update `docs/agents/tingle-linux-image.md` and
  `DOCKERHUB_DESCRIPTION.md` to state the `v`-prefixed tag convention
  consistently, and mention the `shell/linux/VERSION` pin file.

### Out of scope
- Any multi-image / multi-architecture build wiring (`requires:` fan-out,
  QEMU cross-arch builds) — tingle has one image and doesn't need it.
- A separate tingle-app-release process distinct from the image's own `v*`
  tag — `v*` tag push is "the release."
- Changing the smoke-test assertions themselves (GNU sed / non-root check)
  — only their location moves (YAML → script), not their content.
- Pushing the first real `v0.0.1` release tag — an operational follow-up
  after this issue merges, not part of the code change itself.

### Dependencies
- None — self-contained follow-up to the already-merged issues #34–#38
  (tingle linux epic).

### Responsible agent(s)
- `architect` — owns `.circleci/config.yml` and the new top-level
  `scripts/` directory (cross-cutting, root-level concerns per
  `docs/agents/architecture.md`).
- `shell` specialist — touches `shell/linux/docker_run.sh` and
  `shell/linux/VERSION`.

## Benefits

- `.circleci/config.yml` stays clean and thin; build/publish logic lives in
  a testable, locally-runnable script instead of inline YAML bash.
- No more wasted rebuild+republish of an unchanged image on every tag.
- Closes a real, already-present drift bug (three disagreeing conventions
  for the image tag) via one source-of-truth pin file, which is also what
  finally makes `tingle linux` capable of working once a release is cut.
