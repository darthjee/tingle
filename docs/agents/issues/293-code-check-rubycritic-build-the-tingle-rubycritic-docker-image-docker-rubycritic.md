# Issue: code_check rubycritic: build the tingle_rubycritic Docker image (docker/rubycritic/)

## Description
Create the source of the `darthjee/tingle_rubycritic` Docker image in a new top-level folder, `docker/rubycritic/` (parent #290). The image runs [RubyCritic](https://github.com/whitesmith/rubycritic) for the future `tingle code_check rubycritic` subcommand: tingle sends a list of Ruby files on stdin and reads one JSON object on stdout.

The binding contract is [`docs/agents/specs/code_check/rubycritic/image.md`](../specs/code_check/rubycritic/image.md), with the shared rules in [`README.md`](../specs/code_check/rubycritic/README.md) of the same folder. Where this issue and the spec disagree, the spec wins.

Depends on #292 (specs, merged). Followed by #294 (publishing from CircleCI).

## Problem
`tingle code_check rubycritic` needs RubyCritic without asking users to install Ruby. There is no image for it yet, and RubyCritic 5.0.0 has quirks the image must hide: it aborts the whole run on the first file with a syntax error, prints its progress and score on stdout, and fails with git's "dubious ownership" error under a foreign uid.

## Expected Behavior
- `make rubycritic-image` builds `tingle_rubycritic:dev` for the host architecture.
- Running the image with the canonical line, with a file list on stdin:

  ```
  docker run --rm -i --pull never --network none --security-opt no-new-privileges \
    --user <uid>:<gid> -v <root>:/src:ro -w /src tingle_rubycritic:dev
  ```

  prints exactly one JSON object on stdout (RubyCritic's `report.json` plus a `parse_errors` key) and exits 0, for any uid/gid, with no network and a read-only `/src`.
- Files with syntax or encoding errors show up in `parse_errors` and do not fail the run.
- Everything else (RubyCritic's progress, the git notice, `Score:`) goes to stderr.
- Failures exit non-zero with nothing on stdout.

## Solution
All paths are under `docker/rubycritic/`, and the build context is that folder (`docker buildx build -t <tag> docker/rubycritic`).

### Files
- `Dockerfile`:
  - `ARG BASE_IMAGE=ruby:3.3.12-slim@sha256:379ffc9c…`, the full digest from spec section 2.
  - Two stages. The `build` stage installs a pinned `build-essential` (prism compiles a native extension) and runs `bundle install`. The final stage copies `/usr/local/bundle` and the Gemfile pair and installs no apt package.
  - `BUNDLE_GEMFILE=/opt/tingle_rubycritic/Gemfile` and `BUNDLE_FROZEN=true` in both stages.
  - No git anywhere, and `LANG=C.UTF-8` is kept.
  - `USER 1000:1000`, `ENTRYPOINT ["ruby", "/opt/tingle_rubycritic/entrypoint.rb"]` and no `CMD`.
- `Gemfile`: `gem "rubycritic", "5.0.0"` only.
- `Gemfile.lock`: committed, with the platforms `x86_64-linux` and `aarch64-linux` and without `ruby`. Generate it inside the base image. The expected gem versions are in spec section 3.
- `entrypoint.rb`:
  - Reads stdin as UTF-8, one path per line. Blank lines are dropped and duplicates are kept once, at their first position.
  - Pre-parses each path with Reek's parser. Failures go to `parse_errors` as `{path, message}`.
  - Runs `bundle exec rubycritic --format json --no-browser -p /tmp/out <surviving paths>` and sends its stdout and stderr to stderr. It never runs RubyCritic with zero paths.
  - Prints `report.json` plus `parse_errors`. With no surviving paths, it prints the empty object from spec section 4. Exit codes follow the spec's table.
- `fixture/`: `simple.rb`, `complex.rb`, `dup_a.rb`, `dup_b.rb`, `broken.rb`, `empty.rb` and `constants_only.rb` (spec section 6).
- `.dockerignore`: excludes `fixture/`.
- Root `Makefile`: a `rubycritic-image` target running `docker build -t tingle_rubycritic:dev docker/rubycritic`.

### Ownership and docs
- Extend `.claude/agents/shell.md`'s scope to own `docker/` (one sub-folder per check image).
- Add `docker/` to `docs/agents/folder-structure.md` (done by `product-owner`).

### Verification
- `docker buildx build --platform linux/amd64 docker/rubycritic` and the same for `linux/arm64` succeed.
- Run the spec section 6 smoke-test checks by hand against `tingle_rubycritic:dev`, with `--user 501:20`:
  - exit 0 and valid JSON;
  - `metadata.rubycritic.version == "5.0.0"`;
  - six analysed paths, and `parse_errors == [broken.rb]`;
  - a score between 0 and 100;
  - the per-file expectations hold;
  - `command -v git` fails inside the image;
  - empty stdin prints the empty object.

### Out of scope
- Publishing, CircleCI and the scripted `smoke_test_rubycritic` step (#294).
- The Python subcommand (#295 onwards).

### Agents
- `shell`: everything under `docker/rubycritic/`, the `Makefile` target and the scope update in `.claude/agents/shell.md`.
- `product-owner`: the `docker/` entry in `docs/agents/folder-structure.md`.

## Benefits
- Users get Ruby complexity checks with only Docker installed.
- The image is reproducible, because everything is pinned by digest and lockfile.
- It runs safely: no network, read-only source, any uid.
- The JSON contract is stable, so the Python side (#295) can rely on it.
