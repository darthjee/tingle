# Add the Docker Hub description files
Add the description files for `darthjee/tingle_rubycritic`, as specified in [release.md section 5](../../../specs/code_check/rubycritic/release.md#5-docker-hub).

- `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt`: one line, 1 to 100 characters after trimming, e.g. `RubyCritic (Flog, Flay, Reek) as JSON for tingle code_check rubycritic.`
- `docker/rubycritic/DOCKERHUB_DESCRIPTION.md`:
  - what the image is for;
  - the stdin/stdout contract (paths on stdin, `report.json` plus `parse_errors` on stdout);
  - the canonical run line;
  - the pinned Ruby (3.3.12) and RubyCritic (5.0.0) versions;
  - the tag strategy (same semver tag as tingle, no `latest`);
  - a link to https://github.com/darthjee/tingle.

  Use the root `DOCKERHUB_DESCRIPTION.md` as the style reference.
- `docker/rubycritic/.dockerignore`: add both files next to `fixture/`.

## Files to Change
- `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt` — new.
- `docker/rubycritic/DOCKERHUB_DESCRIPTION.md` — new.
- `docker/rubycritic/.dockerignore` — exclude the two description files.
