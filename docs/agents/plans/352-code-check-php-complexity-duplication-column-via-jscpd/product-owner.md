# Product-Owner Plan: code_check php_complexity: duplication column via jscpd

Main plan: [plan.md](plan.md)

## Shared contracts

Documents what shell produces (see [plan.md](plan.md#shared-contracts)): `tool_versions.jscpd`, `files[].duplication`, the path-less `jscpd` warning and its reasons, and the version-read entrypoint failure.

## Implementation Steps

### Step 1 — Update the image doc
In `docs/agents/tingle-php-complexity-image.md`: remove "It has no duplication data yet"; describe the build-only Node stage and the copy of the native jscpd binary (no Node in the final image); the jscpd pin and its bump procedure (update `package.json`, regenerate `package-lock.json` inside the Node image with `npm install --package-lock-only`, keep it equal to `docker/js_complexity/`'s version); the jscpd invocation and options; the `duplication` computation and cases; the failure reasons; and the extra smoke-test assertions. Update the Merged JSON section and its example values.

## Files to Change
- `docs/agents/tingle-php-complexity-image.md` — jscpd stage, pin/bump procedure, duplication contract, smoke test.

## Notes
- The specs folder stays in place; its removal is #353.
