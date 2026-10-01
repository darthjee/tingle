# Shell Plan: code_check rubycritic: build the tingle_rubycritic Docker image (docker/rubycritic/)

Main plan: [plan.md](plan.md)

## Shared contracts

- You create and own the new top-level `docker/` folder, starting with
  `docker/rubycritic/` as the build context
  (`docker buildx build -t <tag> docker/rubycritic`).
- Extend your scope in `.claude/agents/shell.md` with this description:
  "Docker images for `tingle code_check` checks, one sub-folder per image
  (`docker/rubycritic/` builds `tingle_rubycritic`). Owned by the `shell`
  agent." `product-owner` writes the matching
  `docs/agents/folder-structure.md` row, so do not edit that file.
- `make rubycritic-image` builds `tingle_rubycritic:dev`.
- The spec [`image.md`](../../specs/code_check/rubycritic/image.md) is binding. If this plan and the spec
  disagree, follow the spec.

## Steps

- [01 — Gemfile and lock](shell/01-gemfile-and-lock.md)
- [02 — Dockerfile and .dockerignore](shell/02-dockerfile.md)
- [03 — Entrypoint](shell/03-entrypoint.md)
- [04 — Fixture, Makefile target and agent scope](shell/04-fixture-makefile-scope.md)
- [05 — Verify the image](shell/05-verify.md)

## CI Checks

- No CircleCI job covers `docker/` on regular commits. The release jobs
  arrive with #294.
- Codacy runs `shellcheck` and `markdownlint`. Neither covers the
  Dockerfile or the Ruby files, so check them by building and running the
  image (step 05).

## Notes

- The digests and gem versions come from a real run when the specs were
  written. If `ruby:3.3.12-slim@sha256:379ffc9c…` no longer resolves on
  both platforms, or the lock resolves to other gem versions, stop and report
  it. Do not bump silently: a bump is a deliberate change (spec section 8).
- `build-essential` must be version-pinned, as hadolint DL3008 requires.
  Use the version in the `ruby:3.3.12-slim` (trixie) archive, `12.12`
  when the spec was written.
