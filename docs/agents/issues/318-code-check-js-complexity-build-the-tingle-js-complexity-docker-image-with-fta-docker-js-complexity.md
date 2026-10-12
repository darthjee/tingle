# Issue: code_check js_complexity: build the tingle_js_complexity Docker image with FTA (docker/js_complexity/)

## Description
Build the `darthjee/tingle_js_complexity` Docker image under `docker/js_complexity/`. It is the analysis runtime for `tingle code_check js_complexity` (parent #315). This first version runs **FTA only**. Later sub-issues of #315 add jscpd (#324), typhonjs-escomplex (#325) and Vue/Svelte/Astro script extraction (#326).

**Normative spec:** [`docs/agents/specs/code_check/js_complexity/image.md`](../specs/code_check/js_complexity/image.md). It takes precedence over this body; also read the "Deviations from #315" section of the specs [`README.md`](../specs/code_check/js_complexity/README.md#11-deviations-from-315), items 1–4.

## Problem
Tingle cannot assume Node is installed on the host. Like `docker/rubycritic/` for Ruby, the JS analysis needs a self-contained image with a stable stdin → stdout contract that the Python side (#320) can rely on.

## Expected Behavior
### Files (`image.md` §1)
`docker/js_complexity/` contains:
- `Dockerfile` (`image.md` §2), multi-stage:
  - **FTA stage:** a pinned Rust image (`ARG RUST_IMAGE`, tag + digest) runs `cargo install fta --version 3.1.0 --locked --root /opt/fta`. FTA is built from the crate, **not** installed from `fta-cli`, because the npm package's arm64 binary needs musl (deviation 1).
  - **npm stage** (`deps`): `npm ci --omit=dev --no-audit --no-fund` from the committed lock.
  - **Final stage:** `ARG BASE_IMAGE=node:24.21.0-slim@sha256:…` (exact digest from the spec), Debian slim, no apt packages and **no git**. It copies `fta` to `/usr/local/bin/fta`, `/opt/tingle_js_complexity/` from `deps`, and the entrypoint. It ends with `USER 1000:1000` and `ENTRYPOINT ["node", "/opt/tingle_js_complexity/entrypoint.js"]`, with no `CMD`.
  - It never uses `npx`.
- `package.json` (`"private": true`, the Node engine, **no** npm tool dependency yet) and `package-lock.json` (lockfile v3, generated inside the base image with `npm install --package-lock-only`).
- `entrypoint.js`, which may `require` helpers from `lib/`.
- `fixture/`, the smoke-test fixture (`image.md` §9).
- `.dockerignore`, which excludes `fixture/` from the build context.

### Entrypoint contract (`image.md` §4–8)
- **Input:** it reads stdin as bytes (non-UTF-8 stdin → exit 1), splits on `\n` and trims nothing. It takes no arguments.
- **Refused lines:** an empty line, an absolute path, a `..` segment, a duplicate line, a path that is not a regular file under `/src` (real path), or an unsupported extension. Each one gets its `files` entry (`parse_error: false`, `fta: null`) plus an `entrypoint` warning with the exact message from §4.
- **Staged tree:** each accepted line `<n>` is **copied** (not symlinked) to `/tmp/stage/plain/<n>.<ext>`, with a lower-cased extension. This opaque name bypasses FTA's built-in filters (deviations 2–3). Non-UTF-8 files are not staged; they become `parse_error: true` with the `file is not valid UTF-8` warning.
- **FTA run:** it writes `/tmp/fta.json` (`{"extensions": [".mjs", ".cjs", ".mts", ".cts"]}`), then runs `fta /tmp/stage --json --config-path /tmp/fta.json --score-cap 1000000000 --exclude-under 0 --include-comments false` from `/tmp`, with `DEBUG` unset. FTA runs only if something was staged.
- **Parse errors:** they are read from FTA's stderr (`Failed to analyze /tmp/stage/(plain|sfc)/(\d+)\.\S*: (.*)# Issue: code_check js_complexity: build the tingle_js_complexity Docker image with FTA (docker/js_complexity/)

## Description
Build the `darthjee/tingle_js_complexity` Docker image under `docker/js_complexity/`. It is the analysis runtime for `tingle code_check js_complexity` (parent #315). This first version runs **FTA only**. Later sub-issues of #315 add jscpd (#324), typhonjs-escomplex (#325) and Vue/Svelte/Astro script extraction (#326).

**Normative spec:** [`docs/agents/specs/code_check/js_complexity/image.md`](../specs/code_check/js_complexity/image.md). It takes precedence over this body; also read the "Deviations from #315" section of the specs [`README.md`](../specs/code_check/js_complexity/README.md#11-deviations-from-315), items 1–4.

## Problem
Tingle cannot assume Node is installed on the host. Like `docker/rubycritic/` for Ruby, the JS analysis needs a self-contained image with a stable stdin → stdout contract that the Python side (#320) can rely on.

) and mapped back by `<n>`. Results are mapped back by `<n>`, never by stripping a prefix.
- **Output:** exactly one merged JSON object on stdout (`image.md` §7). It has every key from day one: `tool_versions` (`fta` from `fta --version`, `jscpd: null` and `escomplex: null`), one `files` entry per input line in input order (`path`, `parse_error`, `fta: {score, cyclo, lines, assessment}` or `null`, `duplication: null`, `functions: null`), and `warnings`.
- **Exit status:** `0` when the JSON was printed. When FTA exits non-zero, the entrypoint exits with FTA's status. Any other failure exits `1` with a `tingle_js_complexity: <reason>` line on stderr. In both failure cases, stdout stays empty. Empty stdin prints empty `files`/`warnings` and exits 0.
- **Writes:** only under `/tmp`. It works with a read-only root file system and `/src` mounted read-only.

### Build, run and docs
- The `Makefile` gets a `js-complexity-image` target (added to `.PHONY`), next to `rubycritic-image`: `docker build -t tingle_js_complexity:dev docker/js_complexity`.
- It works with `docker run --rm -i --network none --user <uid>:<gid> -v <path>:/src:ro -w /src tingle_js_complexity:dev`.
- `docs/agents/folder-structure.md` lists `docker/js_complexity/`, and `.claude/agents/shell.md` names it in the `shell` agent's scope.

### Verification (`image.md` §12)
- `docker buildx build --platform linux/amd64 docker/js_complexity` succeeds, and the same for `linux/arm64`.
- The §9 smoke checks are run **by hand** and pass against `tingle_js_complexity:dev`: the fixture list plus the five hostile lines, `--user 501:20`, `/src` read-only, the per-file expectations for the `fta` column, no git, and empty stdin.
  The PR description records the commands and their results. Nothing else is committed for this: #319 turns these checks into `smoke_test_js_complexity`.
- There are no unit tests for the entrypoint, the same as `docker/rubycritic/`. The fixture smoke test is the check.

## Solution
Follow `docker/rubycritic/`'s layout and conventions, with a Node entrypoint (`entrypoint.js`) instead of Ruby. Implement exactly what `image.md` pins: versions, digests, options, messages and JSON shape. If something in the spec turns out to be wrong during implementation, raise it on this issue; do not deviate silently.

### Out of scope
- The release pipeline: `release_image.sh`'s `js_complexity` selector, CircleCI jobs, the scripted `smoke_test_js_complexity`, `DOCKERHUB_*` files and `docs/agents/tingle-js-complexity-image.md`. They all belong to #319.
- jscpd, escomplex and SFC extraction (#324, #325, #326).
- Any Python changes (#317, #320).

### Agents
- `shell`: the Dockerfile, `package.json`/lock, entrypoint, fixture, `.dockerignore`, Makefile target and `.claude/agents/shell.md`.
- `product-owner`: the `docs/agents/folder-structure.md` row.

## Benefits
- The Python track (#320) can test end to end with `--image tingle_js_complexity:dev` before anything is published.
- The release pipeline (#319) only has to wrap an image that already meets its contract.
