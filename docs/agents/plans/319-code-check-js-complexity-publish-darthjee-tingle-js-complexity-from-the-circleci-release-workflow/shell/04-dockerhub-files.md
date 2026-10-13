# Write the Docker Hub description files

Write `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt`: one line, 1–100 characters after trimming, describing FTA only for now (e.g. `FTA complexity as JSON for tingle code_check js_complexity.`). Write `docker/js_complexity/DOCKERHUB_DESCRIPTION.md`, in the style of `docker/rubycritic/DOCKERHUB_DESCRIPTION.md`. It covers what the image is for, the stdin/stdout contract, the canonical run line, the pinned Node and FTA versions (from the Dockerfile), the tag strategy (same semver as tingle, every tag published, no `latest`) and a link to https://github.com/darthjee/tingle. Add both files to `docker/js_complexity/.dockerignore` so they stay out of the build context.

## Files to Change
- `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` — new.
- `docker/js_complexity/DOCKERHUB_DESCRIPTION.md` — new.
- `docker/js_complexity/.dockerignore` — exclude both description files.
