# Smoke test and Docker Hub description
In the `js_complexity` smoke test, replace the `escomplex is null` assertion and add the spec §8 checks:
- `tool_versions.escomplex == "0.1.0"`.
- `complex.ts` has at least 20 functions, including one named `reducer` and one starting with `Store.`.
- `[]` for `empty.js` and `short.js`.
- `null` for `broken.js` and `latin1.js` (and for the refused lines).
- Every `line`, `cyclo` and `sloc` is an int ≥ 1.
- There is no path-less `escomplex` warning.

Mention escomplex and per-function data in the Docker Hub descriptions.

## Files to Change
- `scripts/release_image.sh`: the js_complexity smoke-test assertions.
- `docker/js_complexity/DOCKERHUB_DESCRIPTION.md`, `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt`: mention escomplex.
