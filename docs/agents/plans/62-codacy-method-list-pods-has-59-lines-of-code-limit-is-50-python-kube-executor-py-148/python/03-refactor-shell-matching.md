# Refactor _shell to use the shared helper

In `Kube._shell`, replace the inline `match_pods(...)` call plus the following discarded-candidates block (currently computed only when `not matched`) with a single call to `_match_pods_for_alias` (from step 01), passing `alias_config` for the resolved `pod_alias`. Keep the surrounding control flow (single-match vs. multiple-match prompt, "no pods matched" message with discarded candidates) exactly as-is — only the matching/discarded computation itself is delegated to the shared helper.

No behavior change: existing tests in `python/tests/kube/test_executor.py` (`test_shell_*`) must keep passing unmodified, including the ones asserting `mock_list_pods.assert_called_once_with(...)` and the discarded-candidates print format.

## Files to Change
- `python/kube/executor.py` — update `_shell` to call `_match_pods_for_alias` instead of its inline matching/discarded logic.
