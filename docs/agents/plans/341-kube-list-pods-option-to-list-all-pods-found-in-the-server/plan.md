# Plan: kube list pods: option to list all pods found in the server

Issue: [341-kube-list-pods-option-to-list-all-pods-found-in-the-server.md](../../issues/341-kube-list-pods-option-to-list-all-pods-found-in-the-server.md)

## Overview

Add an opt-in `--all` flag to `tingle kube list pods` that, besides today's
per-alias blocks, prints a final `(unmatched)` group (JSON: an entry with
`"alias": null`) holding every pod returned by the server that no displayed
alias matched. Output without the flag is unchanged. The python agent
implements the flag, the output and completion; the guide and examples agents
document it.

## Agents involved

- [python](python.md)
- [guide](guide.md)
- [examples](examples.md)

## Shared contracts

- **Flag**: `--all` (long form only, `store_true`), defined on the `pods`
  subparser of `list`, next to `--namespace`. Parsed key: `parsed["all"]`.
  Usage: `tingle kube list [--json] pods --namespace <namespace_alias> [--all]`.
- **Help text**: `Also list pods that match no configured alias (within the
  given namespace)`.
- **Text output with `--all`**: today's alias blocks (`<alias>:` followed
  by `  - <pod>` lines), then a final block whose header is the literal
  `(unmatched):` followed by `  - <pod>` lines. The `(unmatched):` header
  is always printed, even with no pods under it. The "candidates discarded by
  id_pattern" hint is never printed with `--all`.
- **JSON output with `--all`**: today's `[{"alias": <str>, "pods":
  [<str>...]}]` list plus one final entry `{"alias": null, "pods": [...]}`,
  always present (`"pods": []` when empty).
- **Unmatched set**: pods returned by kubectl for the resolved namespace that
  none of the *displayed* aliases (active scope + namespace filter) matched,
  ordered by `creationTimestamp` ascending. A pod matched by several aliases
  is listed under each of them, as today.
- **Example sample** (namespace `shop`, as in `examples/kube/end_to_end.txt`):

  ```
  $ tingle kube list pods --namespace shop --all
  api:
    - shop-api-5f7c9d8b6a-k3m8p
    - shop-api-5f7c9d8b6a-q7n2w
  (unmatched):
    - shop-redis-0
    - shop-migrate-28391740-x8k2l
  ```
