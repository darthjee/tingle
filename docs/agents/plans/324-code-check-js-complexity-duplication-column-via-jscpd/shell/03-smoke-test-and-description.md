# Smoke test and Docker Hub description
In `smoke_test_js_complexity()` in `scripts/release_image.sh`:

- Change the `tool_versions` check: `jscpd` must be `"5.4.1"`, and `escomplex` stays `null`.
- Assert that `duplication.lines >= 20` for `dup_a.js` and `dup_b.js`, and `== 0` for `simple.js` and `empty.js`.
- Assert that `duplication` is `null` for `broken.js`, `latin1.js` and every hostile line's entry (the hostile lines come after the fixture rows, so look them up by index, not through `entries`).
- Assert that there is no `jscpd` warning in the fixture run.
- Update the function's header comment.

Mention jscpd (exact-clone duplication, the `duplication` field) in the Docker Hub descriptions.

## Files to Change
- `scripts/release_image.sh` — duplication assertions, the `tool_versions.jscpd` check, the comment.
- `docker/js_complexity/DOCKERHUB_DESCRIPTION.md` — describe jscpd and the `duplication` field.
- `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` — mention duplication if it fits in 100 characters.
