# Python Plan: Codacy: Starting a process with a partial executable path (python/kube/inventory.py:24)

Main plan: [plan.md](plan.md)

## Implementation Steps

### Step 1 — Verify the flagged finding against the current code

Confirm whether `python/kube/inventory.py`'s `subprocess.run` call sites
(`list_namespaces`, `get_pod`, `list_pods`) still invoke `kubectl` by a bare
name. Prior work for issue #58 (PR #78) already introduced
`python/kube/binaries.resolve()` and routed all three call sites in this
file through it, updating the `# nosec` annotations to
`B603, B607`. If the current code already resolves the executable and
carries the `B607` annotation, this Codacy finding is stale (raised against
a pre-#78 commit) and no functional code change is required.

### Step 2 — Confirm test coverage still reflects the fix

Check `python/tests/kube/test_inventory.py` patches/asserts against
`binaries.resolve("kubectl")` (rather than a bare `"kubectl"` literal) for
all three functions, consistent with the #78 test updates. If coverage is
already in place, no test changes are needed; only add/adjust assertions if
a gap is found.

## Files to Change

- `python/kube/inventory.py` — no change expected (already resolves
  `kubectl` via `binaries.resolve()` with `# nosec B603, B607`); revisit
  only if verification in Step 1 finds a regression.
- `python/tests/kube/test_inventory.py` — no change expected; revisit only
  if verification in Step 2 finds a gap.

## CI Checks

- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes

- This issue is expected to be a duplicate of already-resolved work from
  issue #58 / PR #78. If verification confirms the code and tests are
  already correct, the resulting PR may contain no functional diff — only
  the issue/plan doc additions from the auto-fix-all pipeline — and should
  be treated as a confirmation/no-op fix rather than a regression.
