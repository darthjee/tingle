# Architect Plan: CI: build and publish the tingle release zip

Main plan: [plan.md](plan.md)

## Shared contracts

Produces the **packaging contract** consumed by `product-owner` (to document)
and by #47 (to build the bootstrap/installer against):

- Tag: plain semver `X.Y.Z` (`X.Y.Z-<suffix>` allowed) — from `$CIRCLE_TAG` in
  CI, else a positional arg; error if neither. No `v` prefix.
- `build` writes `dist/tingle-<tag>.zip` + `dist/tingle-<tag>.zip.sha256`
  (`sha256sum` format: `<64-hex>  tingle-<tag>.zip`). `dist/` is git-ignored.
- Zip content = `INCLUDES` allowlist: `git ls-files -- bin commands completions
  shell python node README.md LICENSE`, minus `python/tests/`,
  `python/Dockerfile`, `python/pyproject.toml`, `python/requirements-dev.txt`,
  `*/.gitkeep`. `MANIFEST` (sorted `LC_ALL=C`, no self-entry) embedded at the zip
  root via `zip -j`.
- `publish` creates/updates the GitHub Release (`draft=false`,
  `prerelease=false`, `generate_release_notes=true`, `name=<tag>`, fixed 2-line
  install `body`) and uploads both assets. Download URL shape #47 depends on:
  `https://github.com/darthjee/tingle/releases/download/<tag>/tingle-<tag>.zip`.
- New CI job `build-and-publish-release`, `requires:
  [build-and-publish-linux-image]`, `release` workflow, same `filters` block as
  the other `release` jobs after #49.
- Secret `GITHUB_RELEASE_TOKEN` (fine-grained PAT, `darthjee/tingle`,
  Contents: RW), CircleCI project env var; `publish` preflights it.

Depends on **#49** landing first (plain-semver tag convention + the
`.circleci/config.yml` `filters.tags.only` regex this job reuses).

## Implementation Steps

### Step 1 — Add `scripts/release_cli.sh` and git-ignore `dist/`

Create `scripts/release_cli.sh`, modelled on `scripts/release_image.sh`
(`#!/usr/bin/env bash`, `set -euo pipefail`, a `main()` `case` on `$1`, small
single-purpose functions, header comment documenting usage + deps + env vars).
**No `set -x` anywhere.**

Subcommands:

- **`build [<tag>]`**
  - `resolve_tag`: `$CIRCLE_TAG` if set, else `$1`, else `echo "release_cli.sh:
    no tag ($CIRCLE_TAG unset and no argument given)" >&2; exit 1`.
  - `resolve_files`: `git ls-files -- bin commands completions shell python node
    README.md LICENSE` piped through a prune `grep -Ev` for
    `^python/(tests/|Dockerfile$|pyproject\.toml$|requirements-dev\.txt$)` and
    `(^|/)\.gitkeep$`. Sort `LC_ALL=C`.
  - **Sensitive-filename guard**: `grep -Eic` the file list against
    `(^|/)(\.env|\.netrc|\.npmrc|id_[a-z0-9_]+|.*\.pem|.*\.key|.*\.p12|.*\.pfx)$`;
    if it matches, print the offending paths and `exit 1` before zipping.
  - `mkdir -p dist`; remove any stale `dist/tingle-<tag>.zip` first (idempotent).
  - Write the file list to a temp `MANIFEST` (the sorted list, **excluding**
    `MANIFEST` itself), `zip -q dist/tingle-<tag>.zip $(cat list)` then
    `zip -j -q dist/tingle-<tag>.zip "$tmp/MANIFEST"`.
  - Checksum: `sha_tool` = `sha256sum` if present else `shasum -a 256`; run it
    against `tingle-<tag>.zip` **from inside `dist/`** (so the sidecar records a
    bare filename, not `dist/…`), write `dist/tingle-<tag>.zip.sha256`.
- **`publish [--dry-run] [<tag>]`** (also honours `RELEASE_DRY_RUN=1`)
  - Preflight: if `-z "${GITHUB_RELEASE_TOKEN:-}"` and not dry-run →
    `echo "release_cli.sh: GITHUB_RELEASE_TOKEN is not set — add it as a
    CircleCI project env var (Project Settings > Environment Variables)" >&2;
    exit 1`.
  - `resolve_tag` as above; assert `dist/tingle-<tag>.zip` and its `.sha256`
    exist (else instruct to run `build` first).
  - API base `https://api.github.com/repos/darthjee/tingle`, uploads base
    `https://uploads.github.com/repos/darthjee/tingle`. Auth header
    `Authorization: Bearer $GITHUB_RELEASE_TOKEN`, `Accept:
    application/vnd.github+json`, `X-GitHub-Api-Version: 2022-11-28`. Use
    `curl -sS` (capture body to a var; on non-2xx print the body — never the
    request — and exit non-zero). Do not use `-f` alone (it hides the error
    body); check the HTTP code via `-w '%{http_code}'`.
  - Lookup: `GET /releases/tags/<tag>`. If 404 → `POST /releases` with
    `{tag_name,name,draft:false,prerelease:false,generate_release_notes:true,body}`.
    If 200 → `PATCH /releases/<id>` with the same fields (idempotent re-run).
  - For each asset (`tingle-<tag>.zip`, `tingle-<tag>.zip.sha256`): if an asset
    of that name already exists on the release, `DELETE /releases/assets/<id>`
    first, then `POST <uploads>/releases/<id>/assets?name=<file>` with
    `Content-Type: application/zip` (zip) / `text/plain` (sha256) and
    `--data-binary @dist/<file>`.
  - **`--dry-run`**: print each method + URL + the JSON body, with the auth
    header shown as `Authorization: Bearer ***`; make no network call.

Add `dist/` to `.gitignore` (new line under the existing entries).

### Step 2 — Add the `build-and-publish-release` CircleCI job

In `.circleci/config.yml`:

- Under `workflows.release.jobs`, add `build-and-publish-release` with
  `requires: [build-and-publish-linux-image]` and the **same `filters` block**
  the sibling jobs carry after #49 (`tags: { only: <#49's plain-semver regex> }`,
  `branches: { ignore: /.*/ }`). Do not invent a second regex — copy whatever
  #49 set on `build-and-publish-linux-image`.
- Under `jobs`, define `build-and-publish-release` as `machine: true` with steps:
  `checkout`; `run: scripts/release_cli.sh build`; `run: scripts/release_cli.sh
  publish`.
- Leave `build-and-publish-linux-image` and `update-description` untouched.

## Files to Change

- `scripts/release_cli.sh` — **new.** `build` + `publish` subcommands per Step 1.
- `.gitignore` — add `dist/`.
- `.circleci/config.yml` — add the `build-and-publish-release` job + its
  `workflows.release` entry (Step 2); nothing else changes.

## CI Checks

No CI job covers these paths (the `test` workflow is `python/`-only; no
shell-lint job). Local, before opening the PR:

- `bash -n scripts/release_cli.sh && shellcheck scripts/release_cli.sh`
- `circleci config validate .circleci/config.yml`
- `CIRCLE_TAG=0.0.0-test scripts/release_cli.sh build` → assert
  `dist/tingle-0.0.0-test.zip` + `.sha256` exist, `git status` clean,
  `unzip -l` shows the runnable tree + root `MANIFEST` and none of `docs/ .circleci/
  .claude/ scripts/ dist/ AGENTS.md python/tests/`, `(cd dist && sha256sum -c
  tingle-0.0.0-test.zip.sha256)` (or `shasum -a 256 -c`) passes, and unzipping
  into a tmp dir + running `bin/tingle help` works.
- `scripts/release_cli.sh publish --dry-run 0.0.0-test` prints the API calls with
  a redacted auth header and makes no request.
- `git diff -- scripts/release_image.sh .circleci/config.yml` shows the two
  existing jobs unchanged.

## Notes

- Keep `scripts/release_image.sh` byte-unchanged — the `tingle.version`
  unification is explicitly deferred.
- `curl -f` hides the response body needed for good error messages — prefer
  `-sS -w '%{http_code}'` + explicit status check.
- The `body` heredoc must not be logged verbatim in a way that could interleave
  with the token; keep token only in the `-H` arg.
- One real end-to-end `publish` run needs a throwaway `0.0.0-rcN` tag pushed to
  the repo/fork; delete the release + tag afterward. Not part of PR CI.
