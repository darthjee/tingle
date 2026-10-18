# Architect Plan: code_check php_complexity: remove docs/agents/specs/code_check/php_complexity/

Main plan: [plan.md](plan.md)

## Shared contracts

Link to `docs/agents/tingle-php-complexity-image.md#bumping-versions`.

## Implementation Steps

### Step 1 — Repoint `.claude/agents/shell.md`

Replace (~lines 36–38) "follow the \"Bumping versions\" section of
[`docs/agents/specs/code_check/php_complexity/image.md`](../../docs/agents/specs/code_check/php_complexity/image.md#13-bumping-versions)
until #347 adds `docs/agents/tingle-php-complexity-image.md`." with
"follow the \"Bumping versions\" section of
[`docs/agents/tingle-php-complexity-image.md`](../../docs/agents/tingle-php-complexity-image.md#bumping-versions)."
This matches the js_complexity sentence just above it.

## Files to Change

- `.claude/agents/shell.md`: repoint the bump-procedure link and drop the "until #347" wording

## Notes

- Same as #298, where architect repointed the shell agent's RubyCritic bump procedure.
