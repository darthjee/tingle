# Product-owner Plan: code_check js_complexity: per-function complexity drill-down (--details) via typhonjs-escomplex

Main plan: [plan.md](plan.md)

## Shared contracts

The image doc describes the merged JSON's `tool_versions.escomplex`, `files[].functions` and the `escomplex` warnings, exactly as in [plan.md](plan.md#shared-contracts) and [`docs/agents/specs/code_check/js_complexity/details.md`](../../../../docs/agents/specs/code_check/js_complexity/details.md).

## Implementation Steps

### Step 1 — Document escomplex in the image doc
Document the following in `docs/agents/tingle-js-complexity-image.md`:
- the typhonjs-escomplex 0.1.0 pin and its lock tree;
- the wrapper (a separate process, its stdin/stdout contract, the pinned module options and the parser plugins by extension);
- the `functions` field mapping;
- per-file and whole-wrapper failure handling;
- the smoke-test expectations.

Follow the shape the jscpd section got in #324.

### Step 2 — Reconcile the specs
If the implementation reveals a grounding difference (e.g. function counts), correct `docs/agents/specs/code_check/js_complexity/details.md` and `image.md` the way #324 did. Otherwise, leave the specs alone.

## Files to Change
- `docs/agents/tingle-js-complexity-image.md`: the escomplex section.
- `docs/agents/specs/code_check/js_complexity/details.md`, `docs/agents/specs/code_check/js_complexity/image.md`: only if the grounding values change.
