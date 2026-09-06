# Plan: Release: switch tag convention from vX.Y.Z to X.Y.Z

Issue: [49-release-switch-tag-convention-from-vx-y-z-to-x-y-z.md](../issues/49-release-switch-tag-convention-from-vx-y-z-to-x-y-z.md)

## Overview

Flip tingle's release tag convention from `v`-prefixed (`v1.9.0`) to plain semver
(`1.9.0`) before any git tag or Docker image exists, so there is zero migration
cost. The change is a fixed 4-file / 8-line edit: the CircleCI `release` workflow
tag filters, the `shell/linux/VERSION` pin file, comment-only wording in
`scripts/release_image.sh`, and the two docs that describe the convention. No
runtime code changes — `scripts/release_image.sh` and `shell/linux/docker_run.sh`
already treat the tag string format-agnostically.

## Agents involved

- [architect](architect.md) — `.circleci/config.yml`, `shell/linux/VERSION`, `scripts/release_image.sh` comments, `DOCKERHUB_DESCRIPTION.md`
- [product-owner](product-owner.md) — `docs/agents/tingle-linux-image.md`

## Shared contracts

Both agents must describe **the same tag format**, verbatim wherever a regex or
example appears:

- **Accepted tag format**: plain semver core `X.Y.Z`, optional pre-release
  suffix — no `v` prefix, no `+build` metadata. The published Docker tag equals
  the git tag string.
- **CircleCI filter regex** (architect lands it; product-owner's prose must
  match its meaning): `/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/`
  - Anchored (`^…$`) though CircleCI already full-matches — kept for
    self-documentation and verbatim reuse by #46/#47.
  - Left **unquoted** in YAML (matches the current `only: /v.*/`); double-quoting
    would make `\.` a YAML escape error.
  - Pre-release class is `[0-9A-Za-z.]` — deliberately no `-`.
- **`VERSION` file content**: `0.0.1` (plain, trailing newline as today).
- **"`v*` tag does nothing" note** — recorded in exactly two places with
  parallel wording:
  - architect: a one-line comment directly above the CircleCI filter, e.g.
    `# plain semver only — a v-prefixed tag (v1.9.0) is silently ignored`
  - product-owner: one clause in `tingle-linux-image.md`'s *Tag strategy*
    bullet — "a `v`-prefixed tag triggers no release (silently ignored by the
    CircleCI tag filter)".
  - **Not** in `DOCKERHUB_DESCRIPTION.md` — its audience pulls the image and
    never pushes release tags.

## CI Checks

- No CI job gates these paths on a pull request: `.circleci/config.yml`'s `lint`
  and `tests` jobs run only against `python/`, and the `release` workflow jobs
  trigger only on tag pushes. There is no shell/YAML lint job.
- Post-merge verification is manual (per the issue): push a throwaway
  `0.0.0-rc1` tag on a branch/fork and confirm the `release` workflow starts;
  confirm a `v0.0.0-rc1` tag does not.

## Notes

- Blocks #46 (release zip) and #47 (bootstrap/installer) — both adopt the regex
  this issue lands.
- Out of scope: `scripts/release_cli.sh` / release-zip job (#46), the
  bootstrap/installer (#47), a shared `tingle.version` file (deferred), and
  cutting the first real release tag (manual op).
- After the edits, the verification-gate grep
  `grep -rnI -E 'v[0-9]+\.[0-9]+|/v\.\*/|v-prefix' . --exclude-dir=.git` should
  return only intentional matches: the CI comment's `(v1.9.0)` example, the
  `tingle-linux-image.md` "triggers no release" clause, and the issue/plan
  files.
