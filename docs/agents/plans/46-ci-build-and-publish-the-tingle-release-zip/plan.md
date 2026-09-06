# Plan: CI: build and publish the tingle release zip

Issue: [46-ci-build-and-publish-the-tingle-release-zip.md](../../issues/46-ci-build-and-publish-the-tingle-release-zip.md)

## Overview

Add `scripts/release_cli.sh` (`build` + `publish`) and a `build-and-publish-release`
job in `.circleci/config.yml`'s `release` workflow that, on every plain-semver
tag and gated `requires: build-and-publish-linux-image`, packages tingle's
runnable tree (fail-closed `INCLUDES` allowlist, embedded `MANIFEST`, `.sha256`
sidecar) into a gitignored `dist/` and publishes it as GitHub Release assets via
`curl` REST. Mirrors the shape of the existing `scripts/release_image.sh`, which
stays byte-unchanged. `product-owner` records the packaging contract under
`docs/agents/` so #47 (bootstrap/installer) has a stable spec to build against.

## Agents involved

- [architect](architect.md) — `scripts/release_cli.sh`, `.circleci/config.yml`, `.gitignore` / `dist/`
- [product-owner](product-owner.md) — `docs/agents/` packaging-contract note and folder-structure update

## Shared contracts

The **packaging contract**: produced by `architect`'s `release_cli.sh`, written
down by `product-owner`, consumed by #47.

- **Tag format**: plain semver `X.Y.Z` (optionally `X.Y.Z-<suffix>`), settled by
  **#49** (blocks this issue). No `v` prefix anywhere.
- **Build output dir**: `dist/` at repo root, git-ignored. `build` writes
  `dist/tingle-<tag>.zip` and `dist/tingle-<tag>.zip.sha256`.
- **Zip name**: `tingle-<tag>.zip`. **Checksum sidecar**: `tingle-<tag>.zip.sha256`
  in `sha256sum` format — one line `<64-hex>  tingle-<tag>.zip` (two spaces), so
  `sha256sum -c` / `shasum -a 256 -c` works from `dist/`.
- **`MANIFEST`**: embedded at the zip root (added via `zip -j`). One packaged
  repo-relative path per line, sorted (`LC_ALL=C`), and it does **not** list
  itself.
- **`INCLUDES` allowlist** (fail-closed): top-level `bin commands completions
  shell python node README.md LICENSE`, resolved with
  `git ls-files -- <those paths>` (tracked files only, no `find`), then pruned of
  `python/tests/`, `python/Dockerfile`, `python/pyproject.toml`,
  `python/requirements-dev.txt`, and every `*/.gitkeep`. A new runnable
  language dir must be added here explicitly or releases omit it.
- **Release object** (`POST`/`PATCH` `…/repos/darthjee/tingle/releases`):
  `tag_name=<tag>`, `name=<tag>`, `draft=false`, `prerelease=false`,
  `generate_release_notes=true`, and a fixed two-line `body`:
  ```
  Install:
  curl -fsSL https://raw.githubusercontent.com/darthjee/tingle/main/install/bootstrap.sh | bash
  ```
- **Asset download URL** (#47 relies on this exact shape):
  `https://github.com/darthjee/tingle/releases/download/<tag>/tingle-<tag>.zip`
  (and `…/tingle-<tag>.zip.sha256`).
- **CI job**: `build-and-publish-release`, in the `release` workflow,
  `requires: [build-and-publish-linux-image]`, same `filters` block as the other
  `release` jobs after #49 (`tags` = the plain-semver regex #49 introduces,
  `branches: ignore /.*/`).
- **Secret**: `GITHUB_RELEASE_TOKEN` — a fine-grained PAT scoped to
  `darthjee/tingle`, permission Contents: Read and write. CircleCI **project**
  env var (not a context). `publish` preflights it and hard-fails with an
  explicit message if unset.

## CI Checks

No CI job covers `scripts/` or `.circleci/` in this repo (the `test` workflow is
`python/`-only; there is no shell-lint job — see `docs/agents/todo.md`). Local
checks only:

- `scripts/`: `bash -n scripts/release_cli.sh` and `shellcheck scripts/release_cli.sh`
- `.circleci/`: `circleci config validate .circleci/config.yml` (or a YAML parse)
- `scripts/release_image.sh` + existing jobs: `git diff` shows them byte-unchanged

## Notes

- **Blocked by #49** — do not land before the plain-semver tag convention + CI
  regex exist. If #46 is implemented first, the job's `filters.tags.only` would
  have to carry an interim regex and be reconciled later.
- **`sha256` tool portability** — the maintainer's dev machine is macOS, which
  has `shasum -a 256`, not GNU `sha256sum`; the CircleCI `machine` executor
  (Ubuntu) has `sha256sum`. `release_cli.sh` must pick whichever exists
  (`command -v sha256sum || shasum -a 256`) for both generating and (in tests)
  verifying the sidecar.
- **`machine` executor tooling** — confirm `zip` is present on the CircleCI
  `machine` image (it is on `ubuntu-2204`); `git`, `curl`, `python3` are.
- **`generate_release_notes` on the first release** — with no previous release,
  GitHub lists everything since repo start; acceptable one-off.
- **No PR-time CI coverage of the new job** (tag-only), same as the image job
  (#35). Reviewer runs `release_cli.sh build` locally and pastes `unzip -l`.
- `shell` specialist may advise on the Bash of `release_cli.sh`, but the file
  lives under `scripts/` (CI/release tooling, architect-owned), not `shell/`.
