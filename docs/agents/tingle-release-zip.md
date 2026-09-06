# `tingle` release zip

This is the packaging contract produced by `scripts/release_cli.sh` (sibling
of `scripts/release_image.sh`). #47 (bootstrap/installer) consumes this
contract as its authoritative spec.

- **Build dir**: `dist/` at repo root, git-ignored. `scripts/release_cli.sh
  build` writes `dist/tingle-<tag>.zip` and `dist/tingle-<tag>.zip.sha256`
  there; nothing under `dist/` is committed or packaged into the zip itself.
- **Zip name**: `tingle-<tag>.zip`, where `<tag>` is the plain semver tag
  (`X.Y.Z`, no `v` prefix — per #49).
- **`INCLUDES` allowlist** (fail-closed): top-level `bin commands completions
  shell python node README.md LICENSE`, resolved via `git ls-files` (tracked
  files only), then pruned of:
  - `python/tests/`
  - `python/Dockerfile`
  - `python/pyproject.toml`
  - `python/requirements-dev.txt`
  - every `*/.gitkeep`

  A new runnable language dir must be added to this allowlist explicitly, or
  releases silently omit it.
- **`MANIFEST`**: embedded at the zip root. Sorted (`LC_ALL=C`) list of every
  packaged repo-relative path, one per line; it does not list itself.
- **`.sha256` sidecar**: `tingle-<tag>.zip.sha256`, `sha256sum` format — one
  line `<64-hex>  tingle-<tag>.zip` (two spaces) — so `sha256sum -c` /
  `shasum -a 256 -c` works from `dist/`.
- **GitHub Release**: `draft=false`, `prerelease=false`,
  `generate_release_notes=true`, `tag_name`/`name` = `<tag>`, with a fixed
  two-line body:
  ```
  Install:
  curl -fsSL https://raw.githubusercontent.com/darthjee/tingle/main/install/bootstrap.sh | bash
  ```
- **Asset download URL** (the shape #47 relies on):
  `https://github.com/darthjee/tingle/releases/download/<tag>/tingle-<tag>.zip`
  (and `…/tingle-<tag>.zip.sha256` for the sidecar).
- **CI job**: `build-and-publish-release`, in the `release` workflow,
  `requires: [build-and-publish-linux-image]`. Uses the `GITHUB_RELEASE_TOKEN`
  secret (CircleCI project env var, not a context) to authenticate the
  publish step.
- **Build/publish script**: `scripts/release_cli.sh` (sibling of
  `scripts/release_image.sh`) performs both the `build` and `publish` steps,
  invoked from `.circleci/config.yml`.
