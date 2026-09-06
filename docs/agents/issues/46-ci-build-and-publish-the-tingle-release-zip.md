## Description
First of three sub-issues splitting #45 (`Add tingle web install (curl | bash)`).
Adds the release-time packaging and publishing of tingle's runnable tree as a
downloadable zip, so a bootstrap script (#45 sub-issue 2) has something to fetch
and install. Mirrors the sibling `arcanum` project's `build_release_zip.sh` +
`upload_release_asset.sh` pair, adapted to tingle's existing
`scripts/release_image.sh` conventions.

Lands first: sub-issue 2 needs the zip layout, the `MANIFEST` format, the
`.sha256` sidecar, and the Release asset URL to exist and be stable before it
can be built.

## Problem
`tingle` has no distribution artifact for the CLI itself. CI
(`.circleci/config.yml`, `release` workflow) only builds and publishes the
`darthjee/tingle` Docker image on release tags — nothing packages `bin/`,
`commands/`, `completions/`, `shell/`, `python/`, `node/` for a user who has not
cloned the repo. There is also no GitHub Release created for a tag today.

> **Tag format:** this issue consumes the plain-semver tag convention (`X.Y.Z`,
> optionally `X.Y.Z-rcN`) settled by **#49**, which must land first. All
> `<tag>` references below are plain semver, no `v` prefix.

## Expected Behavior
- Pushing a release tag (`X.Y.Z`, per #49) runs a new CircleCI job that builds
  `tingle-<tag>.zip` plus `tingle-<tag>.zip.sha256` and attaches both as assets
  on the GitHub Release for that tag (creating the Release if it does not exist).
- `tingle-<tag>.zip` contains the full runnable tree — `bin/`, `commands/`,
  `completions/`, `shell/`, `python/`, `node/`, `README.md`, `LICENSE` —
  selected by an **`INCLUDES` allowlist** (see `## Packaged file set` below), not
  a denylist. Dev/CI/docs/test paths are absent because they are simply not on
  the allowlist.
- A `MANIFEST` file (one packaged repo-relative path per line, sorted) is
  embedded at the zip root, so the installer can reconcile an install without
  needing `git`.
- The new job is tag-gated with the **same `filters` block as the other
  `release` jobs after #49 lands** (`tags: { only: <plain-semver regex from
  #49> }, branches: { ignore: /.*/ }`) and
  **`requires: build-and-publish-linux-image`** — the zip is not published until
  the matching `darthjee/tingle:<tag>` image publish has succeeded, since the
  installed `tingle linux` pulls that exact tag.
- **The job always builds and publishes the zip on every release tag** — there is
  no `changed_since_previous` skip (unlike `release_image.sh`). Reasons: the zip
  tracks the whole repo, not just `shell/linux/`, so a "changed" check would
  nearly always be true anyway; and the zip's version *is* the tag, so every
  release tag must have a resolvable `tingle-<tag>.zip` asset or
  `TINGLE_VERSION=<that-tag>` in the bootstrap (#47) 404s. This means
  `release_cli.sh` needs no `previous_tag` / `changed_since_previous` / no-op
  logic — it is simpler than `release_image.sh`. Re-running a workflow for an
  already-published tag must stay safe (see the "Release/asset already exists"
  edge cases).
- Manual verification: push a throwaway `0.0.0-rc1` tag on a branch/fork, confirm
  the job builds `tingle-0.0.0-rc1.zip`, the Release is created, the asset is
  attached, and `unzip -l` shows the expected tree plus `MANIFEST` at the root.

### Edge cases
- **Release already exists for the tag** — reuse it (idempotent create), just
  upload/replace the asset.
- **Asset already exists** (re-run of the same tag) — delete-then-upload or
  overwrite, so a job re-run is not fatal.
- **No previous tag** — first-ever release; nothing special beyond building the
  full zip.
- **`build-and-publish-linux-image` no-ops** (the image was unchanged since the
  previous tag) — that is a success for the image job, so the zip job's
  `requires` is still satisfied and it must still publish the zip.
- **`gh` CLI auth conflict** — use raw `curl` REST calls against the GitHub API,
  not `gh` (same reason arcanum avoids it: `GH_TOKEN` auto-auth conflict).

## Solution
- New `scripts/release_cli.sh`, subcommand-dispatched in the style of
  `scripts/release_image.sh` (`build`, `publish`; `main` case statement; `set
  -euo pipefail`):
  - `build` — resolve the tag; resolve the packaged file list from the
    `INCLUDES` allowlist (see `## Packaged file set`); `zip -q
    dist/tingle-<tag>.zip <files...>`; generate `MANIFEST` (the sorted packaged
    path list, not listing itself) and `zip -j -q dist/tingle-<tag>.zip MANIFEST`
    to place it at the zip root; write `dist/tingle-<tag>.zip.sha256` in
    `sha256sum` format (`<hash>  tingle-<tag>.zip`, so `sha256sum -c` works).
  - `publish` — preflight `GITHUB_RELEASE_TOKEN`; `POST`/lookup (then `PATCH`)
    the Release for the tag via the GitHub REST API with the fields in
    `### GitHub Release shape`; upload both `tingle-<tag>.zip` and
    `tingle-<tag>.zip.sha256` to the Release's `upload_url`; all with `curl` +
    the token (a fine-grained PAT scoped to `darthjee/tingle`, Contents:
    Read/write — see `## Security & integrity`). Supports `--dry-run` /
    `RELEASE_DRY_RUN=1`.
- See `## Packaged file set` below for the `INCLUDES` allowlist.
- **Build output goes to a gitignored `dist/`** — `build` writes
  `dist/tingle-<tag>.zip` and `dist/tingle-<tag>.zip.sha256` there, and
  `dist/` is added to `.gitignore`, so a local `build` run never dirties the
  working tree or risks an accidental commit. `dist/` is a build-output dir
  owned by `architect` (same as `scripts/`); it is not on the `INCLUDES`
  allowlist, so the zip never contains a previous build.
- `.circleci/config.yml` — add `build-and-publish-release` to the `release`
  workflow with `requires: [build-and-publish-linux-image]` and the same
  tag/branch `filters` block the other `release` jobs carry after #49; job steps
  just call `scripts/release_cli.sh build` then `scripts/release_cli.sh publish`.
  `machine: true` (needs `zip`, `curl`).
- Version string: `release_cli.sh` resolves the tag from `$CIRCLE_TAG`; if
  unset, from an explicit first positional arg (`release_cli.sh build 1.2.3`);
  if neither is given, it errors. **No coupling to `shell/linux/VERSION`** — the
  two release scripts stay fully independent, and there is no semantic mismatch
  (`shell/linux/VERSION` means "currently published Docker tag", not "tag being
  cut"). Introducing a single top-level `tingle.version` shared by both
  `release_cli.sh` and `release_image.sh` is a **deferred follow-up**, out of
  scope here (it would edit the working image release script).
- Docs: `product-owner` adds a short `docs/agents/` note (parallel to
  `docs/agents/tingle-linux-image.md`) describing the zip name, `MANIFEST`
  format, the `INCLUDES` allowlist, the asset URL shape, and the `requires`
  dependency — this is the shared contract sub-issue 2 reads.

### Packaged file set (`INCLUDES` allowlist)

Fail-closed: the zip contains **only** what the allowlist resolves to, so a
newly committed top-level file or directory is not shipped in releases until it
is explicitly added here.

- **Allowlisted top-level paths:** `bin/`, `commands/`, `completions/`,
  `shell/`, `python/`, `node/`, `README.md`, `LICENSE`.
- **Pruned from within those:** `python/tests/`, `python/Dockerfile`,
  `python/pyproject.toml`, `python/requirements-dev.txt`, and every `**/.gitkeep`.
- **Resolution:** `git ls-files -- bin commands completions shell python node
  README.md LICENSE` piped through the prune filter — tracked files only, no
  raw `find`.
- **Deliberately absent** (not on the allowlist): `.circleci/`, `.claude/`,
  `.github/`, `docs/`, `scripts/`, `dist/`, `AGENTS.md`, `CLAUDE.md`,
  `.gitignore`, `.codacy.yml`, `Makefile`, `docker-compose.yml`,
  `DOCKERHUB_DESCRIPTION.md`.
- **Maintenance cost:** when a genuinely new runnable language dir lands (e.g. a
  future `ruby/`), the PR that adds the first such command must add the dir to
  this allowlist, or releases silently omit it.

### GitHub Release shape

Fields `release_cli.sh publish` sets on `POST /repos/darthjee/tingle/releases`
(and re-asserts on `PATCH` for a re-run):

- **`tag_name`** — the pushed release tag (`X.Y.Z`).
- **`name`** — equal to the tag string.
- **`draft: false`** — required; a draft's assets are not anonymously
  downloadable, which would 404 the `curl | bash` install for that version.
- **`prerelease: false`** — always. Every release tag is a normal release; the
  `X.Y.Z-rcN` throwaway test tags are fine as non-prereleases and are deleted
  after verification.
- **`generate_release_notes: true`** — GitHub appends an auto PR/commit list
  since the previous release.
- **`body`** — a fixed two-line install snippet, which GitHub prepends above the
  generated notes:
  ```
  Install:
  curl -fsSL https://raw.githubusercontent.com/darthjee/tingle/main/install/bootstrap.sh | bash
  ```
- **`make_latest`** — leave the API default (`"true"`); with `prerelease: false`
  every release becomes "Latest".

On a workflow re-run for an existing tag, `publish` `PATCH`es these same fields
(idempotent) rather than failing — see the "Release already exists" edge case.

### Scope
- `scripts/release_cli.sh`:
  - `build` — tag from `$CIRCLE_TAG` or a positional arg; resolve the `INCLUDES`
    file list; sensitive-filename guard; `zip` + embedded `MANIFEST` into
    `dist/`; write `dist/tingle-<tag>.zip.sha256`.
  - `publish` — `GITHUB_RELEASE_TOKEN` preflight; create/ensure the Release;
    upload `dist/tingle-<tag>.zip` and its `.sha256` asset; `--dry-run` /
    `RELEASE_DRY_RUN=1` mode.
- `.gitignore` — add `dist/` (build-output dir, owned by `architect`).
- One new job in `.circleci/config.yml`'s `release` workflow.
- One new CircleCI project env var for the GitHub token (documented; the value
  is set manually in CircleCI project settings, like
  `DOCKER_HUB_USERNAME`/`DOCKER_HUB_PASSWORD`).
- A `docs/agents/` note capturing the packaging contract (zip name, `MANIFEST`
  format, `INCLUDES` allowlist, asset URL shape, `requires` dependency).

### Out of scope
- The `bootstrap.sh` / `installer.sh` scripts and anything that consumes the zip
  — sub-issue 2 of #45 (#47).
- README user-facing docs — sub-issue 3 of #45 (#48).
- The tag-convention switch (`vX.Y.Z` → `X.Y.Z`) and the CI tag-filter regex —
  **#49** (this issue just uses the result).
- An `update` flow.
- Actually pushing the first real release tag — a manual operational step, as
  with the image.

### Dependencies
- **Blocked by #49** — the plain-semver tag convention and the CI tag-filter
  regex must be settled first; this issue's new job reuses that `filters` block
  and its `<tag>` strings are plain semver.
- No code dependency on #47/#48. At **runtime** the new job is sequenced after
  `build-and-publish-linux-image` via `requires`.
- Blocks #47 (it needs the `MANIFEST` format, zip layout, the `.sha256`
  sidecar, and the asset URL).

### Responsible agent(s)
- `architect` — `.circleci/config.yml`, root `scripts/`, `.gitignore`, and the
  new `dist/` build-output dir (all cross-cutting / root-level).
- `product-owner` — the `docs/agents/` packaging note.

## Security & integrity

**GitHub token:**
- A **fine-grained PAT** scoped to `darthjee/tingle` only, permission **Contents:
  Read and write** (the minimum to create a Release and upload assets), nothing
  else. Fine-grained PATs expire in ≤1 year — renewal is a known operational
  chore. A dedicated bot account owning the token is possible but not required
  for this repo.
- Stored as a CircleCI **project-level environment variable**
  `GITHUB_RELEASE_TOKEN` (same as `DOCKER_HUB_USERNAME` / `DOCKER_HUB_PASSWORD`),
  not a shared org context.
- **Config-change protection is inherent:** the `release` workflow is tag-only
  (`branches: ignore /.*/`), so a PR that edits `release_cli.sh` or
  `.circleci/config.yml` cannot run the release job or reach the token — only a
  release-tag push (which requires push access) runs it. CircleCI also withholds
  secrets from forked-PR builds by default.

**Keeping the token out of logs:**
- No `set -x` in `release_cli.sh` (matches `release_image.sh`). The token is
  passed as `-H "Authorization: Bearer $GITHUB_RELEASE_TOKEN"` from the
  environment and never echoed.
- `--dry-run` prints the header redacted as `Authorization: Bearer ***`.
- On failure the script prints the API **response body** (error JSON — no
  secret), not the request; `curl -sS -f`, capture body to a variable.
- The missing-token preflight (see `## Backward compatibility`) prints only the
  variable name, never a value.

**Artifact integrity:**
- `build` also produces `tingle-<tag>.zip.sha256`, and `publish` uploads it as a
  **second Release asset** next to the zip. The installer (#47) can verify the
  download against it. This is a shared contract with #47.
- **Honest limitation:** a `.sha256` sidecar defends against transport
  corruption / truncation, **not** against a compromised release token — an
  attacker with `Contents: write` rewrites both assets. Real authenticity
  (signing with a key that is *not* in CI — GPG / cosign / Sigstore) is
  **out of scope here, tracked as future work**.
- All URLs are `https://` GitHub-hosted; no plaintext transport anywhere.

**No secrets in the zip:**
- The `INCLUDES` allowlist is fail-closed and `git ls-files` packages tracked
  files only — untracked local junk (`.env`, editor swap files) can never be
  included, and whole areas (`.claude/`, `.github/`, `docs/`, CI config) are off
  the list.
- **Belt-and-braces:** after resolving the file list and before zipping, `build`
  scans it for apparent-secret filenames (`.env`, `.netrc`, `.npmrc`, `id_*`,
  `*.pem`, `*.key`, `*.p12`, `*.pfx`) and **fails** if any matched — catching a
  secret committed *inside* an allowlisted directory (e.g. `python/`). Name-based
  only (not a content scanner); ~5 lines, `grep`-only, refine the pattern if a
  legitimate fixture ever trips it.

## Testing strategy

**Static (PR-time — matches the bar PR #44 set for `release_image.sh`):**
- `bash -n` and `shellcheck` on `scripts/release_cli.sh`.
- YAML-parse / `circleci config validate` on `.circleci/config.yml`.
- `git diff` confirms `scripts/release_image.sh` and the existing `release` jobs
  are byte-unchanged.

**`build` — fully local, no secrets:**
- `CIRCLE_TAG=0.0.0-test scripts/release_cli.sh build` in a clean checkout.
- Assert `dist/tingle-0.0.0-test.zip` and `dist/tingle-0.0.0-test.zip.sha256`
  exist; `git status` stays clean (only the gitignored `dist/` changed);
  `unzip -l` shows the runnable tree plus `MANIFEST` at the zip root, and
  **none** of the non-allowlisted paths (`docs/`, `.circleci/`, `.claude/`,
  `scripts/`, `dist/`, `AGENTS.md`, `python/tests/`, …).
- `MANIFEST` equals the sorted list of packaged paths.
- `sha256sum -c dist/tingle-0.0.0-test.zip.sha256` passes (run from `dist/`).
- Re-running `build` is idempotent (clean overwrite, no stale files).
- With no `$CIRCLE_TAG` and no positional arg, `build` errors clearly;
  `release_cli.sh build 0.0.0-test` works.
- **Acceptance check:** unzip into a tmp dir and run `bin/tingle help` and
  `bin/tingle --help linux` from there — proves the packaged tree is actually
  runnable and catches an over-aggressive prune.

**`publish` — real token, real API:**
- Add a **`--dry-run`** flag (and/or `RELEASE_DRY_RUN=1`): resolves the Release
  URL, prints the `curl` calls it would make, and performs no POST/upload. Used
  for local sanity and documented in the script header.
- True end-to-end stays a **manual throwaway-tag** run: push `0.0.0-rcN` on the
  repo (or a fork), verify the Release has both `tingle-<tag>.zip` and
  `tingle-<tag>.zip.sha256` attached and that `sha256sum -c` passes, then delete
  the Release and tag.
- The sensitive-filename guard: a unit-style check that `build` fails when a
  matching path is forced onto the list (e.g. `touch shell/fake.pem &&
  git add -N`).

**Known gap (accepted):** the new job is release-tag-only, so the PR that adds it
gets no CI coverage of the job itself — the same situation as the image job
(#35). Accepted mitigation: the reviewer runs `release_cli.sh build` locally and
pastes `unzip -l` output into the PR; one throwaway-tag run exercises `publish`
once. Wiring `bash -n`/`shellcheck` into the `test` workflow is **not** done here
(tingle has no shell-lint job yet; `docs/agents/todo.md` tracks adding one).

## Backward compatibility

The change is additive; existing release-tag behavior is preserved with these
specifics (the tag-format change itself is #49's concern, not this issue's):

- **GitHub Releases begin to exist.** Today a release tag push produces a git tag
  and a Docker image but no GitHub Release. After this, every release tag gets a
  Release object — the repo's "Releases" tab / "Latest release" sidebar
  populate and `…/releases/latest` starts resolving. Nothing automated consumes
  releases today (only `.circleci` reacts to tags, via `CIRCLE_TAG`), so no
  integration breaks. There are **no git tags in the repo yet**, so there is no
  historical backfill concern — the first release tag pushed is a clean slate.
- **New required secret `GITHUB_RELEASE_TOKEN`.** CircleCI jobs are independent
  unless linked by `requires`, and `update-description` requires only
  `build-and-publish-linux-image`; a missing or invalid token therefore fails
  **only the new job** — the image still builds and publishes — but the tag's
  overall workflow goes red. **Decision: hard-fail is intended.** A release
  without its zip is incomplete, so the token is required setup, same tier as
  `DOCKER_HUB_USERNAME` / `DOCKER_HUB_PASSWORD`. `release_cli.sh publish` must
  do a **preflight check** and exit non-zero with an explicit
  `GITHUB_RELEASE_TOKEN is not set` message (and a pointer to CircleCI project
  settings) rather than surfacing a raw `curl` 401. The token value is set
  manually in CircleCI project settings before the first release tag is pushed.
- **`requires: [build-and-publish-linux-image]`** is new coupling but not a
  regression (the job did not exist before). The image job's
  no-op-when-`shell/linux/`-unchanged path still exits 0, so `requires` stays
  satisfied and the zip job still runs.
- **`scripts/release_image.sh` is left untouched** by this issue. The
  `tingle.version` unification (see the Version string note under `## Solution`)
  is **deferred** — not done here — so the existing image-release path has zero
  diff and zero risk.
- **`git clone` + `tingle install` from a checkout keep working unchanged.** The
  zip is purely additive distribution.
- **`.circleci/config.yml`** gains one job and one workflow entry; the `test`
  workflow (lint/tests on every push) and the existing `release` jobs are
  unmodified. The config uses no YAML anchors/executors that a new job could
  disturb.

## Benefits
- Produces the artifact the whole web-install flow depends on.
- Reuses the established `scripts/release_image.sh` shape, so CI logic stays out
  of the YAML and is locally runnable.
- The embedded `MANIFEST` gives the installer (and a future `update` flow) a
  git-free way to know exactly what a release contains.
