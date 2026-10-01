# Shell Plan: code_check rubycritic: remove docs/agents/specs/code_check/rubycritic/

Main plan: [plan.md](plan.md)

## Shared contracts

Point comments at sections of `docs/agents/tingle-rubycritic-image.md`:
`Contract` (`#contract`), `Smoke test` (`#smoke-test`), `Bumping versions`
(`#bumping-versions`). Use the plain path form, as in `shell/linux/Dockerfile:25`.

## Implementation Steps

### Step 1 — Repoint the code comments
Comment-only changes:
- `docker/rubycritic/Dockerfile:14-15` — "See docs/agents/specs/code_check/rubycritic/image.md (section 8) for the bump procedure." → "See docs/agents/tingle-rubycritic-image.md (\"Bumping versions\") for the bump procedure."
- `docker/rubycritic/entrypoint.rb:26` — "Contract: docs/agents/specs/code_check/rubycritic/image.md (section 4)." → "Contract: docs/agents/tingle-rubycritic-image.md (\"Contract\")."
- `scripts/release_image.sh:412-414` — "Runs the fixture checks from docs/agents/specs/code_check/rubycritic/image.md (section 6) ..." → cite docs/agents/tingle-rubycritic-image.md ("Smoke test"); reflow the comment.

## Files to Change
- `docker/rubycritic/Dockerfile` — comment.
- `docker/rubycritic/entrypoint.rb` — comment.
- `scripts/release_image.sh` — comment.

## CI Checks
- No CI job lints these files on push; locally run `shellcheck scripts/release_image.sh` and `ruby -c docker/rubycritic/entrypoint.rb`.

## Notes
- Do not touch `docs/agents/` or `.claude/agents/`.
