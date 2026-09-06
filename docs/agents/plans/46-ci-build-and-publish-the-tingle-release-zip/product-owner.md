# Product-Owner Plan: CI: build and publish the tingle release zip

Main plan: [plan.md](plan.md)

## Shared contracts

Document (do not design) the **packaging contract** `architect`'s
`scripts/release_cli.sh` produces, so #47 (bootstrap/installer) has one
authoritative spec:

- Zip: `dist/tingle-<tag>.zip`, published as a GitHub Release asset at
  `https://github.com/darthjee/tingle/releases/download/<tag>/tingle-<tag>.zip`.
- Checksum sidecar: `tingle-<tag>.zip.sha256`, `sha256sum` format, same URL
  pattern.
- `MANIFEST` at the zip root: sorted (`LC_ALL=C`) list of packaged
  repo-relative paths, one per line, not listing itself.
- `INCLUDES` allowlist: `bin commands completions shell python node README.md
  LICENSE`, minus `python/tests/`, `python/Dockerfile`, `python/pyproject.toml`,
  `python/requirements-dev.txt`, `*/.gitkeep`.
- Tag: plain semver `X.Y.Z` (per #49). Release is `draft=false`,
  `prerelease=false`, `generate_release_notes=true`.
- CI: `build-and-publish-release` job, `requires:
  [build-and-publish-linux-image]`.

## Implementation Steps

### Step 1 — Add `docs/agents/tingle-release-zip.md`

New doc, parallel in style to `docs/agents/tingle-linux-image.md` (bulleted,
terse). Cover: the zip name and `dist/` build dir; the `INCLUDES` allowlist and
prune list; the embedded `MANIFEST` format; the `.sha256` sidecar format; the
GitHub Release shape (draft/prerelease/notes/body); the asset download URL
shape; the `build-and-publish-release` CI job and its `requires:
[build-and-publish-linux-image]` dependency and `GITHUB_RELEASE_TOKEN` secret;
and a one-line note that `scripts/release_cli.sh` is the build/publish script
(sibling of `scripts/release_image.sh`). State explicitly that this contract is
what #47 consumes.

### Step 2 — Update `docs/agents/folder-structure.md`

- Extend the `scripts/` row: it now also holds `scripts/release_cli.sh`, the
  CLI release-zip build/publish script (add a pointer to
  `docs/agents/tingle-release-zip.md`).
- Add a `dist/` row: git-ignored build-output directory for
  `scripts/release_cli.sh` (`tingle-<tag>.zip` + `.sha256`); not committed, not
  packaged.

## Files to Change

- `docs/agents/tingle-release-zip.md` — **new.** The packaging contract (Step 1).
- `docs/agents/folder-structure.md` — `scripts/` row extended, new `dist/` row
  (Step 2).

## Notes

- Keep it descriptive of the agreed contract only — no new decisions. If an
  implementation detail differs from this plan once `architect` writes the
  script, the doc follows the script.
- `docs/agents/architecture.md` needs no change (it already describes `.circleci/`
  as architect-owned and does not enumerate `scripts/` contents).
