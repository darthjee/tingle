# Python Plan: code_check php_complexity: remove docs/agents/specs/code_check/php_complexity/

Main plan: [plan.md](plan.md)

## Shared contracts

Link to `docs/agents/tingle-php-complexity-image.md` → `Merged JSON`.

## Implementation Steps

### Step 1 — Repoint the sample's docstring

`python/tests/code_check/php_complexity/sample_output.py` line 1:
`"""Container output sample (docs/agents/specs/code_check/php_complexity/image.md §7).`
→ `"""Container output sample (docs/agents/tingle-php-complexity-image.md, "Merged JSON").`
Keep the line within the project's line-length limit (wrap if needed).
Docstring only, no data changes.

## Files to Change

- `python/tests/code_check/php_complexity/sample_output.py`: docstring

## CI Checks

- `python/`: the Python test/lint job (run the php_complexity tests to confirm nothing changed)
