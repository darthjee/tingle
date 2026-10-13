# Shell Plan: code_check js_complexity: duplication column via jscpd

Main plan: [plan.md](plan.md)

## Shared contracts

Produces the filled `tool_versions.jscpd`, `files[].duplication` and the path-less `jscpd` failure warning exactly as in [plan.md](plan.md#shared-contracts). The JSON shape and the exit-status rules of `entrypoint.js` do not change.

## Steps

- [01 — Pin jscpd 5.4.1](shell/01-pin-jscpd.md)
- [02 — Run jscpd in the entrypoint](shell/02-run-jscpd-in-entrypoint.md)
- [03 — Smoke test and Docker Hub description](shell/03-smoke-test-and-description.md)

## CI Checks
- `docker/js_complexity`, `scripts/release_image.sh`: `scripts/release_image.sh build js_complexity && scripts/release_image.sh smoke-test js_complexity` (CI: the js_complexity release job's Build and Smoke test steps). Run at least on the local platform (`PLATFORMS=linux/<arch>`).

## Notes
- jscpd 5.4.1 is a Rust binary shipped as per-platform optional npm packages. Check that `npm ci --omit=dev` in the `deps` stage installs the right binary on both amd64 and arm64. The lock must list both `jscpd-linux-x64-gnu` and `jscpd-linux-arm64-gnu`.
- jscpd prints its summary on stdout even with `--silent`. The entrypoint's stdout must stay exactly one JSON object, so send jscpd's stdout to stderr.
