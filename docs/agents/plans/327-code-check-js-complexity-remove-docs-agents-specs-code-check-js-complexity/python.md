# Python Plan: code_check js_complexity: remove docs/agents/specs/code_check/js_complexity/

Main plan: [plan.md](plan.md)

## Shared contracts

- The merged-JSON contract moves to the `### Merged JSON` subsection of
  `docs/agents/tingle-js-complexity-image.md` (product-owner step 01).

## Implementation Steps

### Step 1 — Repoint the sample_output.py docstring
`python/tests/code_check/js_complexity/sample_output.py` line 1:
`"""Container output sample (docs/agents/tingle-js-complexity-image.md, "Merged JSON")."""`.
Also check `python/` for any other reference with the verification grep from
[plan.md](plan.md#shared-contracts), and repoint it the same way.

## Files to Change
- `python/tests/code_check/js_complexity/sample_output.py` — docstring only.

## CI Checks
- `python/`: `ruff check .` (CI job: `lint`) and the test suite (`pytest`).
