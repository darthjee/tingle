# Python Plan: Codacy: subprocess call - check for execution of untrusted input (python/kube/inventory.py:24)

Main plan: [plan.md](plan.md)

## Steps

- [01 — Add Kubernetes name validation module](python/01-add-validation-module.md)
- [02 — Wire validation into inventory.py](python/02-wire-validation-into-inventory.md)
- [03 — Add tests](python/03-add-tests.md)

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- Namespace max length is 63 chars per Kubernetes rules; other resource names (e.g. pod names) are capped at 253 — the validator should accept a configurable/parameterized max length rather than hardcoding 63 everywhere.
- Keep the existing `# nosec B603, B607` comments on the `subprocess.run` calls in `inventory.py` untouched — they remain accurate for the shell-injection/partial-path angles this change does not replace.
- `list_namespaces()` takes no caller-supplied arguments, so it needs no validation call.
