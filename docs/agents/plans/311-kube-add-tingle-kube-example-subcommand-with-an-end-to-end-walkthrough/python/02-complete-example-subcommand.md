# Complete the example subcommand

Offer `example` in bash completion without touching the config.

- `python/kube/completion.py`: add `"example"` to `SUBCOMMANDS`. In
  `complete()`, next to the existing `configure` early return and **before**
  `KubeConfig()` is constructed, return `[]` when `subcommand == "example"`
  (it takes no arguments). Mention `example` in the module docstring where
  config-free subcommands are described.

Tests (`python/tests/kube/test_completion.py`):

- `complete([""])` includes `example`.
- `complete(["example", ""])` returns `[]` and does not construct
  `KubeConfig` (patch `kube.completion.KubeConfig` and assert not called) nor
  call `scope.detect_active_scope`.

## Files to Change

- `python/kube/completion.py` — `SUBCOMMANDS` + config-free early return.
- `python/tests/kube/test_completion.py` — completion cases.
