# Write scripts/release_image.sh

Create the new top-level `scripts/` directory and a single dispatch script,
`scripts/release_image.sh`, that holds all the build/publish/description
logic currently inlined in `.circleci/config.yml`'s `run:` blocks. Dispatch
by first CLI argument (subcommand), mirroring the shape referenced in the
issue's Solution section (a scaled-down version of the Majora
`bin/image.sh qemu|build|push` pattern — no multi-image/arch parameters,
since tingle has exactly one image).

Required behavior, translated from the current inline steps
(`.circleci/config.yml` lines 56-96 today) plus the new guard/validation
logic from the issue:

- **Tag resolution**: `$CIRCLE_TAG` when set (CI), else the trimmed
  content of `shell/linux/VERSION` (local dev). This is the single
  function every other subcommand calls to get "the tag to act on."
- **`previous_tag()`**: `git tag --sort=-creatordate | awk 'NR==2{print;
  exit}'` — finds the release tag immediately before the current one (the
  current tag, if just pushed, sorts first). Empty result is valid (no
  previous release yet — see Edge cases in the issue).
- **`changed_since_previous()`** (the build-needed guard): if
  `previous_tag()` is empty, return "changed" (proceed unconditionally —
  first release). Otherwise `git diff --quiet <prev>..HEAD -- shell/linux/`
  — non-empty diff means "changed." Called at the top of the `build` and
  `publish` subcommands so each is independently a safe no-op (exit 0,
  success) when nothing changed.
- **`verify_version_pin()`**: only when `$CIRCLE_TAG` is set (CI context).
  Compares `shell/linux/VERSION`'s trimmed content against `$CIRCLE_TAG`
  with exact string equality. Mismatch: print a clear error to stderr and
  exit non-zero (hard fail — no build, no publish). Called before `build`
  and `publish` proceed with any real work.
- **`build` subcommand**: `docker build -t darthjee/tingle:<tag> -f
  shell/linux/Dockerfile .` (same command as today, `<tag>` from tag
  resolution above). Calls `verify_version_pin` and
  `changed_since_previous` first (no-ops out early if unchanged).
- **`smoke-test` subcommand**: both checks from the current inline steps —
  `docker run --rm darthjee/tingle:<tag> sed --version | grep -qi "GNU
  sed"`, and the non-root uid check (`docker run --rm
  darthjee/tingle:<tag> id -u` must not be `0`). Keep the exact assertions
  as they are today — only their location moves.
- **`publish` subcommand**: `verify_version_pin` +
  `changed_since_previous` guard, then `echo "$DOCKER_HUB_PASSWORD" |
  docker login -u "$DOCKER_HUB_USERNAME" --password-stdin` followed by
  `docker push darthjee/tingle:<tag>` (unchanged from today).
- **`update-description` subcommand**: move the current
  `update-description` job's inline curl/python verbatim (Docker Hub JWT
  login, then `PATCH .../repositories/darthjee/tingle/` with
  `DOCKERHUB_DESCRIPTION.md`'s content as `full_description`) into this
  subcommand, unchanged in behavior.
- `set -euo pipefail` at the top, matching the repo's existing shell script
  convention (per `docs/agents/contributing.md`).

## Files to Change
- `scripts/release_image.sh` (new) — all subcommands and helper functions
  described above.
