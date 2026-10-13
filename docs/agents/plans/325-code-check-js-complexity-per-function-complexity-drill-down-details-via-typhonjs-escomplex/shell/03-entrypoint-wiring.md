# Wire the wrapper into the entrypoint
After `applyJscpd`, call `applyEscomplex(files, staged, warnings)`:
- Spawn the wrapper with the staged paths (JSON on stdin) and a large `maxBuffer`.
- Map each result back to its entry through `staging.stagedNumber`. Fill `entry.functions` only for staged entries whose `parse_error` is false. A wrapper `error` keeps `null` and adds `{tool: "escomplex", path: <line>, message}`.
- On a non-zero exit, a kill, stdout that isn't a JSON object, or an unknown path: set every `functions` back to `null` and add one path-less `escomplex` warning. Never change the exit status.
- Set `tool_versions.escomplex` to `escomplexVersion()`.
- Update the header comment (output, dependencies, contract links).

## Files to Change
- `docker/js_complexity/entrypoint.js`: call `applyEscomplex`, set the version, update the comment.
- `docker/js_complexity/lib/staging.js`: only if a helper is needed to list staged paths (reuse what jscpd uses).
