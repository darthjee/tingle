# Shell Plan: code_check php_complexity: duplication column via jscpd

Main plan: [plan.md](plan.md)

## Shared contracts

Produces (consumed by python, documented by product-owner):

- `tool_versions.jscpd == "5.4.1"` from `/usr/local/bin/jscpd --version`; unreadable → exit 1, `tingle_php_complexity: cannot read the jscpd version`.
- `files[i].duplication`: `{"lines": n}` / `null` per the cases in [plan.md](plan.md#shared-contracts).
- On jscpd failure: every `duplication` is `null`, one path-less `{"tool": "jscpd", "message": ...}` warning with the `js_complexity` reasons, exit status unchanged.

## Steps

- [01 — Pin jscpd and add the Node build stage](shell/01-image-node-stage.md)
- [02 — Run jscpd from the entrypoint](shell/02-entrypoint-jscpd.md)
- [03 — Extend the smoke test](shell/03-smoke-test.md)
- [04 — Docker Hub descriptions](shell/04-dockerhub-descriptions.md)

## CI Checks
- `docker/php_complexity/`, `scripts/release_image.sh`: `scripts/release_image.sh build php_complexity && scripts/release_image.sh smoke-test php_complexity` (CI jobs in the php_complexity release workflow, `.circleci/config.yml`).

## Notes
- The Node build stage uses the same pinned `node:24.21.0-slim` digest as `docker/js_complexity/Dockerfile` (Debian 12). The copied binary links only against `libgcc_s`, `libm` and `libc`, so it runs on the trixie-based final image; the smoke test's `command -v node` check proves no Node leaks in.
- `package-lock.json` must be generated inside the Node image (`npm install --package-lock-only`) and list both `jscpd-linux-x64-gnu` and `jscpd-linux-arm64-gnu` `5.4.1`; copying the relevant entries from `docker/js_complexity/package-lock.json` is a good cross-check.
- jscpd only sees `/tmp/stage`, so excluded/ignored files (e.g. `vendor/`) never contribute clones.
