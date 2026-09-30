# Write image.md (#293)
Create `docs/agents/specs/code_check/rubycritic/image.md`, linking #293 at the top.

It must specify:
- **Location:** `docker/rubycritic/`. The build context and the file set are `Dockerfile`, `Gemfile`, `Gemfile.lock`, the entrypoint script and the smoke-test fixture, with their paths given.
- **Base image:** the exact pinned `ruby:3.3.N-slim` tag and the pinned RubyCritic version, both from step 01. Bumping either one is a deliberate change.
- **No git** in the image, and why: no churn, and no "dubious ownership" error.
- **Runtime user:** the image must work under an arbitrary `--user <uid>:<gid>`, including any environment step 01 found necessary (e.g. `HOME=/tmp`).
- **Entrypoint contract:**
  - It reads relative paths from stdin, one per line, and ignores blank lines.
  - It runs RubyCritic with `--format json --no-browser -p /tmp/out` on those paths.
  - It prints `report.json` only on stdout; RubyCritic's own output and warnings go to stderr.
  - Exit status: 0 on success; non-zero when RubyCritic fails or the report is missing. Say what happens on empty stdin, although tingle never starts the container with no files.
- **Smoke-test fixture:** where it lives and what it contains (reuse step 01's set), plus the expected assertions (the JSON parses and contains the expected files).
- **Local build:** a `Makefile` target or compose service that builds `tingle_rubycritic:dev` for use with `--image`.

## Files to Change
- `docs/agents/specs/code_check/rubycritic/image.md`: new.
