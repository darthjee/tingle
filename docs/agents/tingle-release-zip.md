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
  install shell python node README.md LICENSE`, resolved via `git ls-files` (tracked
  files only), then pruned of:
  - `python/tests/`
  - `python/Dockerfile`
  - `python/pyproject.toml`
  - `python/requirements-dev.txt`
  - every `*/.gitkeep`

  A new runnable language dir must be added to this allowlist explicitly, or
  releases silently omit it.
- **`MANIFEST`**: embedded at the zip root, in `sha256sum` format — one line
  `<64-hex>  <path>` (lowercase hex, two spaces, repo-relative plain path) per
  packaged file, sorted with `LC_ALL=C` by path; it does not list itself.
  Consumers split each line on the **first two spaces only**: the hash is the
  text before them and the path is everything after them, including any
  further spaces. The hash is SHA-256, computed with `sha256sum` (falling
  back to `shasum -a 256`) over the same file that is zipped. `MANIFEST`
  holds the plain path, never the `\`-prefixed escaped form `sha256sum`
  prints for names containing a backslash or a newline. Paths containing a
  newline are not supported.
- **`tingle.json`**: written by `install/installer.sh` into the install
  folder:
  `{"version": "X.Y.Z", "repo": "owner/repo", "manifest": [{"path": "...", "sha256": "<64-hex>"}]}`.
  Paths are JSON-escaped (backslashes and double quotes). `version`, `repo`
  and `manifest` are required: a `tingle.json` that can't be parsed, lacks
  any of them, or whose `manifest` is not an array is corrupt, and
  `tingle update` refuses it. `manifest` is `[]` when the release has no
  `MANIFEST` (or an empty one); `"manifest": []` means the install does not
  track hashes. `version` defaults to `"unknown"` (the `TINGLE_VERSION`
  default when installing from a checkout), which is always treated as out
  of date. 0.3.x and earlier wrote a path-only `"manifest": ["path", ...]`,
  which readers still accept as entries without a hash. Whether an install tracks hashes is decided from this format, never
  from the `version` string. The helpers that hash files, convert `MANIFEST`
  to JSON and read both `tingle.json` formats live in the sourced library
  `install/manifest.sh`.
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
