# Python Plan: Codacy: Method _list_pods has 59 lines of code (limit is 50) (python/kube/executor.py:148)

Main plan: [plan.md](plan.md)

## Overview
`Kube._list_pods` (`python/kube/executor.py:148-214`) is 59 lines, exceeding the project's 50-line Lizard complexity limit. It duplicates per-alias pod-matching and "discarded by id_pattern" lookup logic between its JSON and text branches, and `Kube._shell` (`python/kube/executor.py:216-297`) duplicates the same matching/discarded logic again even though it wasn't flagged. The fix pulls the shared matching/discarded logic into static helpers reusable by both methods, and splits `_list_pods`'s output building into its own small helpers — no behavior change, no output difference for any existing case.

## Context
- `_list_pods` filters `config.data["pods"]` aliases scoped to the active namespace, then for each alias calls `match_pods(...)` and, when nothing matches, recomputes a "discarded" list of pod names that share the alias's prefix but were filtered out by `id_pattern`. This happens once to build the JSON payload and again to build the text output.
- `_shell` performs the identical `match_pods(...)` + discarded-candidates computation for a single alias/pod when resolving `pod_alias`.
- Existing tests in `python/tests/kube/test_executor.py` call `Kube._list_pods(...)` / `Kube._shell(...)` directly and assert on `capsys` output and mock call args (e.g. `mock_list_pods.assert_called_once_with(...)`) — none of them patch or inspect internal helper methods, so extracting private static helpers is safe as long as printed output and `list_pods`/`match_pods` call arguments stay identical.

## Steps

- [01 — Extract shared pod-matching and discarded-candidates helper](python/01-extract-shared-matching-helper.md)
- [02 — Refactor _list_pods to use the shared helper and split output building](python/02-refactor-list-pods-output.md)
- [03 — Refactor _shell to use the shared helper](python/03-refactor-shell-matching.md)

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- Keep all new helpers `@staticmethod`s on `Kube`, matching the existing style in `executor.py`.
- No new tests are required if existing coverage of `_list_pods`/`_shell` output stays green, but add direct unit tests for the new shared helper if it makes the discarded-candidates behavior easier to verify in isolation.
- Re-check line counts after the refactor (e.g. via the Lizard rule locally or `ruff`/`radon` if available) to confirm `_list_pods` and any new helper are at or under 50 lines.
