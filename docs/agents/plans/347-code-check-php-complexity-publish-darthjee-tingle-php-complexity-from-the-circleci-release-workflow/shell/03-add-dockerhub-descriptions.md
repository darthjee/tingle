# Add the Docker Hub description files

Create `docker/php_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt`, one line of 1 to 100 characters after trimming (for example `PDepend complexity metrics as JSON for tingle code_check php_complexity.`). Also create `docker/php_complexity/DOCKERHUB_DESCRIPTION.md`, modelled on `docker/js_complexity/DOCKERHUB_DESCRIPTION.md`. It covers what the image is for, the stdin/stdout contract, the canonical run line, the pinned PHP and PDepend versions (no jscpd yet), the tag strategy (same tag as tingle, no `latest`) and a link to the tingle repository.

Add both files to `docker/php_complexity/.dockerignore`, which currently excludes `fixture/` and `vendor/`.

## Files to Change
- `docker/php_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` — new.
- `docker/php_complexity/DOCKERHUB_DESCRIPTION.md` — new.
- `docker/php_complexity/.dockerignore` — exclude both description files.
