# Product-owner Plan: code_check js_complexity: duplication column via jscpd

Main plan: [plan.md](plan.md)

## Shared contracts

Describes the image's jscpd behaviour as in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Update the image doc
In `docs/agents/tingle-js-complexity-image.md`:
- the image now runs FTA **and** jscpd (around line 11);
- the `package.json` row lists `jscpd` `5.4.1` (line 36);
- the merged-JSON example and its field notes (lines 145–171): `tool_versions.jscpd` is `"5.4.1"`, and `files[].duplication` follows its rules;
- the path-less `jscpd` warning;
- the fixture and smoke-test expectations (around lines 281–319): `dup_a.js`/`dup_b.js` get 22, the other staged files 0, and `null` for parse errors and refused lines.

Keep only `escomplex` (#325) and `.vue` (#326) as "not yet".

## Files to Change
- `docs/agents/tingle-js-complexity-image.md` — jscpd in the image, the JSON fields, the warning and the smoke-test expectations.
