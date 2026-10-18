# Issue: code_check php_complexity: remove docs/agents/specs/code_check/php_complexity/

## Description
Remove the temporary specs `docs/agents/specs/code_check/php_complexity/` (parent #344), now that every other sub-issue of #344 (#345–#352) has landed. This is the final cleanup sub-issue of the split and merges last, following the same pattern as the RubyCritic cleanup (#298).

## Problem
The spec folder (`README.md`, `cli.md`, `config.md`, `details.md`, `duplication.md`, `image.md`, `release.md`, `selection.md`) is temporary by convention (see `docs/agents/specs.md`). Several permanent files still link to it:

- `docs/agents/specs.md` — the `code_check/php_complexity` row in *Current specs*.
- `docs/agents/architecture.md` — links to `cli.md`, `config.md` and `selection.md`.
- `.claude/agents/shell.md` — points to `image.md` "Bumping versions" "until #347 adds `docs/agents/tingle-php-complexity-image.md`" (that doc now exists).
- Code comments: `docker/php_complexity/Dockerfile`, `docker/php_complexity/entrypoint.php` (contract: `image.md`, `duplication.md`), `scripts/release_image.sh` (fixture checks from `image.md`), `python/tests/code_check/php_complexity/sample_output.py` (`image.md` §7).

## Expected Behavior
- Before deleting, check that nothing still needed lives only in the specs. Anything worth keeping moves to `docs/agents/tingle-php-complexity-image.md` (image contract: merged JSON, smoke-test fixture, bumping versions), `docs/agents/architecture.md` (CLI/config/selection design) or `docs/guides/code_check/php_complexity.md` (user-visible behaviour).
- Delete `docs/agents/specs/code_check/php_complexity/`, and `docs/agents/specs/code_check/` since it becomes empty.
- Remove the `code_check/php_complexity` row from `docs/agents/specs.md` (keep the index and an empty table).
- Repoint every remaining link to the specs:
  - `docs/agents/architecture.md` → the permanent docs/guide.
  - `.claude/agents/shell.md` → `docs/agents/tingle-php-complexity-image.md#bumping-versions` (and drop the "until #347" wording).
  - Comments in `docker/php_complexity/Dockerfile`, `docker/php_complexity/entrypoint.php`, `scripts/release_image.sh` and `python/tests/code_check/php_complexity/sample_output.py` → the matching section of `docs/agents/tingle-php-complexity-image.md`.
- After the change, `grep -rn 'specs/code_check/php_complexity'` finds nothing outside `docs/agents/issues/` and `docs/agents/plans/`.

### Out of scope
- Any behaviour change. Comment-only edits in code files (to repoint links) are allowed; nothing else in code changes.
- Rewriting historical issue/plan files under `docs/agents/issues/` and `docs/agents/plans/`.

## Benefits
- No dangling links once the temporary specs are gone.
- The permanent docs become the single source of truth for `php_complexity`.
