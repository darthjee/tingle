# Issue: code_check rubycritic: remove docs/agents/specs/code_check/rubycritic/

## Description
Final cleanup sub-issue of #290. All other sub-issues (#291–#297) are closed, so the temporary specs for `tingle code_check rubycritic` under `docs/agents/specs/code_check/rubycritic/` can be removed, following the cleanup rule in `docs/agents/specs.md`.

## Problem
Several permanent files still point into the specs, and some of them rely on content that exists only there:

- `docs/agents/tingle-rubycritic-image.md` links `subcommand.md` §5 (RubyCritic JSON contract), and its "Bumping versions" section already says the JSON contract moves into that doc "once the specs are removed".
- `docs/agents/architecture.md` links `subcommand.md` §3–4 for the full Docker runner contract.
- `.claude/agents/shell.md` points at `image.md` §8 for version bumps.
- Code comments in `docker/rubycritic/Dockerfile` (`image.md` §8), `docker/rubycritic/entrypoint.rb` (`image.md` §4) and `scripts/release_image.sh` (`image.md` §6) cite the specs.

Deleting the folder as-is would leave broken links and lose the JSON contract.

## Expected Behavior
- `docs/agents/specs/code_check/rubycritic/` is deleted, and `docs/agents/specs/code_check/` too, since it becomes empty.
- The `code_check rubycritic` row is removed from the Current specs table in `docs/agents/specs.md` (the index itself stays).
- No file in the repo (docs, agent definitions, code comments) references `docs/agents/specs/code_check/`.
- Contract content that is still normative lives in permanent docs.

## Solution
1. Move the RubyCritic JSON contract (`subcommand.md` §5, the sample JSON and the field rules) into `docs/agents/tingle-rubycritic-image.md` as its own section. Point the doc's existing link at that section and update the "Bumping versions" note so it no longer mentions the spec.
2. In `architecture.md`, keep the short Docker runner summary and drop the link to `subcommand.md` §3–4; the code and tests are the reference for the full rules.
3. Repoint `.claude/agents/shell.md` and the comments in `docker/rubycritic/Dockerfile`, `docker/rubycritic/entrypoint.rb` and `scripts/release_image.sh` to the matching sections of `docs/agents/tingle-rubycritic-image.md` (Contract, Smoke test, Bumping versions).
4. Delete the specs folder and the `specs.md` row.
5. Verify with `grep -rn 'specs/code_check' .` (only historical `docs/agents/issues`/`plans` files may match).

### Agents
- `product-owner`: `docs/agents/` changes.
- `shell`: comments in `docker/rubycritic/` and `scripts/release_image.sh`.
- `architect`: `.claude/agents/shell.md`.

## Benefits
Closes out #290 without broken links and without losing the contracts that the code, tests and future version bumps still rely on.
