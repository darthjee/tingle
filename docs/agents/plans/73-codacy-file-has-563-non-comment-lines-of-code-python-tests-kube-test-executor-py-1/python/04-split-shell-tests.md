# Split `_shell` tests into their own file

Create `python/tests/kube/test_executor_shell.py`, moving the 8 tests that
cover `kube.executor.Kube._shell` out of `test_executor.py`:
`test_shell_aborts_when_aws_precheck_fails`,
`test_shell_single_match_resolves_and_execs`,
`test_shell_warns_when_pod_alias_namespace_conflicts_with_argument`,
`test_shell_pass_through_pod_alias_uses_literal_pod_name`,
`test_shell_zero_matches_prints_error_and_suggestions`,
`test_shell_multiple_matches_prompts_for_choice`,
`test_shell_non_running_pod_warns_but_still_execs`,
`test_shell_get_pod_error_aborts_before_exec` (currently at lines 310-552,
including their `@patch` decorators — note `test_shell_multiple_matches_prompts_for_choice`
also patches `kube.executor.prompt_pod_choice`).

Give the new file its own module docstring (e.g. `"""Unit tests for
kube.executor.Kube._shell."""`), the imports these tests actually use, and
local copies of the `_config` and `_pod` helpers. Do not change any test
body, assertion, or mock call.

Do **not** delete these tests from `test_executor.py` yet — cleanup happens
in step 05.

## Files to Change

- `python/tests/kube/test_executor_shell.py` — new file with the 8 `_shell`
  tests and local `_config`/`_pod` helpers.
