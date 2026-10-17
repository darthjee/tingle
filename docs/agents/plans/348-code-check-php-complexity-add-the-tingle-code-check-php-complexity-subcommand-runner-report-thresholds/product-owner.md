# Product-owner Plan: code_check php_complexity: add the tingle code_check php_complexity subcommand (runner, report, thresholds)

Main plan: [plan.md](plan.md)

## Shared contracts

Describes the package and module layout from [plan.md § Shared contracts](plan.md#shared-contracts) and [`cli.md`](../../specs/code_check/php_complexity/cli.md) §1.

## Implementation Steps

### Step 1 — Architecture doc
Document the `python/code_check/php_complexity/` package in `docs/agents/architecture.md`, next to `js_complexity`: its modules, the bindings to `docker_check`, the PDepend image, and the total-CCN level. Cross-link `docs/agents/tingle-php-complexity-image.md`.

### Step 2 — README table
Add `code_check php_complexity` to the command table in the root `README.md`, the same way `js_complexity` was added in #320.

## Files to Change
- `docs/agents/architecture.md` — the new package
- `README.md` — command table row
