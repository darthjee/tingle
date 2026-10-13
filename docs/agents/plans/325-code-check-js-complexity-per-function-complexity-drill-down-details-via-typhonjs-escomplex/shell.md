# Shell Plan: code_check js_complexity: per-function complexity drill-down (--details) via typhonjs-escomplex

Main plan: [plan.md](plan.md)

## Shared contracts

The image must produce the merged JSON described in [plan.md](plan.md#shared-contracts), `tool_versions.escomplex`, `files[].functions` and the `escomplex` warnings. The spec, [`docs/agents/specs/code_check/js_complexity/details.md`](../../../../docs/agents/specs/code_check/js_complexity/details.md) §1–3, §6 and §8, is authoritative for the module options, the parser plugins and the field mapping.

## Steps

- [01 — Pin typhonjs-escomplex](shell/01-pin-escomplex.md)
- [02 — Write the escomplex wrapper](shell/02-escomplex-wrapper.md)
- [03 — Wire the wrapper into the entrypoint](shell/03-entrypoint-wiring.md)
- [04 — Smoke test and Docker Hub description](shell/04-smoke-test-and-description.md)

## CI Checks
- `docker/js_complexity`: `scripts/release_image.sh build js_complexity && scripts/release_image.sh smoke-test js_complexity` (CircleCI js_complexity image jobs: Build image, Smoke test)

## Notes
- The wrapper must run as a separate `node` process (`spawnSync`) so that an escomplex crash or out-of-memory error can't take the entrypoint down. Follow `lib/jscpd.js` for the soft-failure pattern (a dedicated error class, and one path-less warning).
- SFC staging (`/tmp/stage/sfc/...`) belongs to #326, which is still open. Choose plugins by the staged file's **last** extension so SFC virtual modules work later without changes.
- Regenerate `package-lock.json` with the pinned Node (24.21.0), and check the resolved tree against spec §1.
