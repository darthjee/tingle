# Shell Plan: code_check php_complexity: remove docs/agents/specs/code_check/php_complexity/

Main plan: [plan.md](plan.md)

## Shared contracts

Link to `docs/agents/tingle-php-complexity-image.md` sections `Contract`,
`Merged JSON`, `Smoke test` and `Bumping versions` (kept stable by
product-owner).

## Implementation Steps

### Step 1 — Repoint comments (comment-only)

- `docker/php_complexity/Dockerfile` (~line 26): "See
  docs/agents/specs/code_check/php_complexity/image.md (\"Bumping versions\")"
  → "See docs/agents/tingle-php-complexity-image.md (\"Bumping versions\")".
- `docker/php_complexity/entrypoint.php` (~lines 53–54): "Contract:
  …specs…/image.md and …specs…/duplication.md." → "Contract:
  docs/agents/tingle-php-complexity-image.md (\"Contract\" and \"Merged JSON\")."
- `scripts/release_image.sh` (~line 878): "the fixture checks from
  docs/agents/specs/code_check/php_complexity/image.md (section 9)" → "the
  fixture checks from docs/agents/tingle-php-complexity-image.md (\"Smoke test\")".

No code changes. The image tag/version stays the same, since only comments change.

## Files to Change

- `docker/php_complexity/Dockerfile`: comment
- `docker/php_complexity/entrypoint.php`: comment
- `scripts/release_image.sh`: comment

## Notes

- The shell agent's own scope note says "Do NOT touch … `docs/agents/`".
  This plan stays within that: only code-file comments change.
