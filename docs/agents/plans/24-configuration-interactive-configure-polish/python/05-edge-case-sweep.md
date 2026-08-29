# Section 6 edge-case sweep

Walk the parent issue's Section 6 table against the current behavior of `switch`/`list`/`shell` and close the gaps found. Most cases are already handled by earlier children (#20–#23); this step confirms and patches the remainder:

| Edge case | Current state | Action |
| --- | --- | --- |
| Invalid AWS credentials | Handled — `_check_aws_credentials`/`switch`'s pre-check aborts before `kubectl` | none |
| Nonexistent context | Handled — `_switch` lists available contexts on `switch_context` failure | none |
| Nonexistent namespace | Partially handled — `resolve_namespace_alias` only covers the alias-not-found case; a real-but-wrong namespace name reaching `kubectl get pods -n <ns>` surfaces `inventory.list_pods`'s raw `stderr`, which is already a "clear error" per `list_pods`/`get_pod`'s existing contract | verify the raw `kubectl` stderr text is not empty/cryptic for a missing namespace; if it already reads clearly (kubectl's own `NotFound` message), no change — else prefix it with `kube: ` for consistency with other messages |
| Alias out of scope | Handled — `resolve_context_alias`/`resolve_namespace_alias` pass through with a notice | none |
| No pod matches the alias | Handled in `shell` (`_shell` prints discarded-by-`id_pattern` candidates); **not** handled in `list pods` — an alias with zero matches just prints its own empty header | add the same "candidates discarded by id_pattern" suggestion to `_list_pods` when a configured alias matches nothing, reusing the same discard-by-prefix computation `_shell` already does |
| Pod not Running | Handled — `_shell` warns before exec | none |
| `config.json` missing or invalid | Handled — `KubeConfig._fallback` sets `pass_through`/`notice`, printed in `run()` | none |

## Files to Change

- `python/kube/executor.py` — extend `_list_pods` to print discarded-by-`id_pattern` candidates when an alias matches zero pods, mirroring `_shell`'s existing block; prefix any bare `kubectl` stderr surfaced for a nonexistent namespace with `kube: ` if it isn't already clear.
