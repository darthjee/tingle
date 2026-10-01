# Plan: code_check rubycritic: build the tingle_rubycritic Docker image (docker/rubycritic/)

Issue: [293-code-check-rubycritic-build-the-tingle-rubycritic-docker-image-docker-rubycritic.md](../../issues/293-code-check-rubycritic-build-the-tingle-rubycritic-docker-image-docker-rubycritic.md)

## Overview

Create the source of the `tingle_rubycritic` image in a new top-level folder,
`docker/rubycritic/`, following the binding spec
[`image.md`](../../specs/code_check/rubycritic/image.md). The image is a two-stage Ruby 3.3.12-slim build
with RubyCritic 5.0.0 locked for amd64 and arm64, and no git. Its
`entrypoint.rb` reads file paths from stdin, pre-parses them, runs RubyCritic
and prints one JSON object on stdout. The `shell` agent builds the image, the
fixture and the `make rubycritic-image` target, and takes ownership of
`docker/`. The `product-owner` agent records the new folder in
`docs/agents/folder-structure.md`.

## Agents involved

- [shell](shell.md)
- [product-owner](product-owner.md)

## Shared contracts

- **New top-level folder:** `docker/`, one sub-folder per check image. The
  first one is `docker/rubycritic/`, the build context of the
  `tingle_rubycritic` image.
- **Owner:** the `shell` agent. `shell` extends its own scope in
  `.claude/agents/shell.md`, and `product-owner` writes the
  folder-structure entry. Both must use the same wording for the folder:
  "Docker images for `tingle code_check` checks, one sub-folder per image
  (`docker/rubycritic/` builds `tingle_rubycritic`). Owned by the `shell`
  agent."
- **Local build target:** `make rubycritic-image` builds
  `tingle_rubycritic:dev` from `docker/rubycritic`.
- **Out of scope:** publishing, CircleCI and the scripted
  `smoke_test_rubycritic` step (#294), and the Python subcommand (#295 and
  later).
