# Docker Hub descriptions
Mention jscpd in the image's Docker Hub texts: the tools it runs (PHP parser, PDepend, jscpd), `tool_versions.jscpd` now `"5.4.1"`, `duplication` as `{"lines": n}` (lines in exact clones among the sent files) or `null`, and that a jscpd failure adds a path-less `jscpd` warning instead of failing. Remove the "always `null`" wording. Keep the short description within 100 characters.

## Files to Change
- `docker/php_complexity/DOCKERHUB_DESCRIPTION.md` — jscpd and `duplication` description.
- `docker/php_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` — mention duplication (jscpd) if it fits.
