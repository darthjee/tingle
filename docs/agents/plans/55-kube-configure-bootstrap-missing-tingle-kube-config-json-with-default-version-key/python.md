# Python Plan: kube configure: bootstrap missing ~/.tingle/kube/config.json with default version key

Main plan: [plan.md](plan.md)

## Steps

- [01 — Add CURRENT_VERSION and bootstrap the missing-file case](python/01-bootstrap-missing-config.md)
- [02 — Print the bootstrap notice unconditionally](python/02-print-bootstrap-notice.md)
- [03 — Add/update test coverage](python/03-test-coverage.md)

## CI Checks

- `python`: `pytest` (CI job: `tests`)
- `python`: `ruff check .` (CI job: `lint`)

## Notes

- A missing file and a malformed file must stay distinguishable: only "file does not exist" gets bootstrapped; invalid JSON, a non-dict payload, or a structurally invalid (but present) file must keep falling back to pass-through mode exactly as today.
- Bootstrapping happens for every kube command, not only `configure` — `kube switch`/`list`/`shell` run against a fresh `KubeConfig()` too and should see the file created on first use, per the clarifying-question decision recorded in the issue.
- `executor.py`'s `_configure` handler instantiates a second, independent `KubeConfig()` after `run()`'s own instance already bootstrapped the file — by the time that second instantiation happens the file exists on disk, so it reads normally and prints no second notice. No change needed there beyond Step 2's notice-printing condition.
