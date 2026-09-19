# Issue: Codacy: File has 563 non-comment lines of code (python/tests/kube/test_executor.py:1)

## Description
Codacy flags `python/tests/kube/test_executor.py` for having 563 non-comment
lines of code, over the `Lizard_file-nloc-medium` threshold (Complexity,
Warning). The file holds unit tests for every static method on
`kube.executor.Kube` — `_switch`, `_list_namespace`, `_list_pods`, `_shell`,
`_configure` (dispatch only), and `run` — in a single module (28 test
functions, 683 total lines including comments/blank lines).

## Problem
Every other test file under `python/tests/kube/` maps to a single concern
(e.g. `test_configure.py` tests `kube.configure`, `test_scope.py` tests
`kube.scope`), but `kube/executor.py` bundles many `Kube` static methods in
one module, so its test file absorbed all of their tests and grew past both
Codacy's `Lizard_file-nloc-medium` limit and this repo's own
`check_file_size` error threshold (`DEFAULT_ERROR = 500` lines, see
`python/check_file_size/constants.py:57`). This mirrors the pattern already
fixed for the production side of this same file in #70/#103
(`_shell` method length), but on the test side it's the whole file, not one
method, that's oversized.

## Expected Behavior
`python/tests/kube/test_executor.py` (and any file replacing it) stays under
the Codacy/`check_file_size` thresholds, with no loss of test coverage or
change in test behavior — this is a pure reorganization.

## Solution
Split `test_executor.py` into one file per `Kube` method under test, keeping
all existing test bodies and assertions unchanged:

- `test_executor_switch.py` — `_switch` (4 tests)
- `test_executor_list_namespace.py` — `_list_namespace` (5 tests)
- `test_executor_list_pods.py` — `_list_pods` (10 tests)
- `test_executor_shell.py` — `_shell` (8 tests)
- `test_executor_dispatch.py` — `_configure` dispatch + `run` (4 tests)

The shared `_config`/`_pod` builder helpers currently defined at the top of
`test_executor.py` should move to a `python/tests/kube/conftest.py` (none
exists yet in this directory) so all five files can reuse them without
duplication. Exact filenames/grouping are an implementation detail for
whoever plans this issue — the constraint is that no resulting file exceeds
the `check_file_size` warn/error thresholds.

## Benefits
- Resolves the Codacy finding and brings the file under the repo's own
  `check_file_size` thresholds.
- Each new file maps to one `Kube` method, matching the one-file-per-concern
  convention already used by the rest of `python/tests/kube/`.
- Shared fixtures in `conftest.py` remove duplication instead of copy-pasting
  `_config`/`_pod` into five files.
