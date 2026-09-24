# Issue: Codacy: Use of assert detected (Bandit B101) in python/tests/ (294 occurrences)

## Description
Codacy's Bandit reports `Bandit_B101` (category Security, severity High): "Use of assert detected. The enclosed code will be removed when compiling to optimised byte code." There are 294 findings, all under `python/tests/`:

| File | Findings |
|---|---|
| `python/tests/kube/test_config.py` | 32 |
| `python/tests/check_file_size/test_executor.py` | 26 |
| `python/tests/kube/test_scope.py` | 25 |
| `python/tests/check_file_size/test_reporter.py` | 24 |
| `python/tests/kube/test_executor_list_pods.py` | 19 |
| `python/tests/kube/test_configure.py` | 18 |
| `python/tests/kube/test_completion.py` | 15 |
| `python/tests/kube/test_executor_shell.py` | 14 |
| `python/tests/kube/test_inventory.py` | 12 |
| `python/tests/kube/test_exec.py` | 11 |
| `python/tests/kube/test_executor_list_namespace.py` | 11 |
| `python/tests/check_file_size/test_file_collector.py` | 11 |
| `python/tests/check_file_size/test_palette.py` | 11 |
| `python/tests/check_file_size/test_file_analyzer.py` | 11 |
| `python/tests/kube/test_executor_switch.py` | 11 |
| `python/tests/common/test_arg_parser.py` | 9 |
| `python/tests/kube/test_auth.py` | 8 |
| `python/tests/check_file_size/test_skip_checks.py` | 6 |
| `python/tests/kube/test_parser.py` | 6 |
| `python/tests/kube/test_validation.py` | 5 |
| `python/tests/kube/test_matching.py` | 4 |
| `python/tests/kube/test_binaries.py` | 2 |
| `python/tests/check_file_size/test_main.py` | 2 |
| `python/tests/kube/test_executor_dispatch.py` | 1 |

## Problem
These are pytest test files, where plain `assert` is the idiomatic and required way to write assertions. They are never run with `python -O`. B101 is meaningful for production code but pure noise in tests. These findings make up about 83% of the repository's open Codacy issues and bury the real ones.

## Expected Behavior
Bandit B101 is not reported for files under `python/tests/`, and it stays active for production code under `python/check_file_size/`, `python/common/` and `python/kube/`.

## Solution
Scope Bandit out of the test tree only, and do not disable B101 globally:
- Add a per-engine exclusion to `.codacy.yml`: `engines.bandit.exclude_paths: ["python/tests/**"]`, with a comment explaining why (pytest's plain `assert` is idiomatic and tests never run under `python -O`). Other Codacy tools (Prospector, Pylint, Lizard, etc.) keep analysing the tests.
- Update the `.codacy.yml` header comment, which currently says "No exclusions yet".
- A `.bandit` file or `[tool.bandit]` config is **not** used: Bandit's `skips` is global (it cannot be limited to one directory), and a repo-level tool config file would override the patterns selected in the Codacy UI.
- Production code (`python/check_file_size/`, `python/common/`, `python/kube/`) keeps full Bandit coverage, including B101, and its existing targeted `# nosec` comments.

Do not rewrite the asserts.

## Benefits
Removes 294 false-positive High findings in one change, so the Codacy dashboard reflects the real issues.

