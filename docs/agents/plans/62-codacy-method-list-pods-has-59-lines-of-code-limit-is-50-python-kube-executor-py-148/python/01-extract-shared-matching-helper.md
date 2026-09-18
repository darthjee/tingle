# Extract shared pod-matching and discarded-candidates helper

Add a static helper to `Kube` (e.g. `_match_pods_for_alias(items, alias_config, default_id_pattern)`) that runs `match_pods(items, prefix, alias_config.get("id_pattern"), default_id_pattern)` and returns `(matched, discarded)`, where `discarded` is the list of `items` whose `metadata.name` starts with `prefix` but is not in `matched` — computed only when `matched` is empty, mirroring the current inline logic in both `_list_pods` and `_shell`. Keep the signature independent of `_list_pods`'s and `_shell`'s specific `alias_config` shapes (both already carry `prefix` and optional `id_pattern`).

This step only adds the helper; `_list_pods` and `_shell` still contain their original inline logic until steps 02 and 03 switch them over, so behavior is unchanged after this step alone.

## Files to Change
- `python/kube/executor.py` — add the new static helper method near `_check_aws_credentials` (top of the class's private-helpers section).
