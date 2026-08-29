# Wire configure dispatch and --json list output

Two independent, small changes to the executor/parser:

## Replace the `configure` stub

`Kube._configure` in `executor.py` currently just prints "not yet implemented". Dispatch to the new `configure.py` functions (Steps 2–3) by `configure_target`:

```python
@staticmethod
def _configure(parsed: dict) -> None:
    config = KubeConfig()
    {
        "context": configure_context,
        "namespace": configure_namespace,
        "pod": configure_pod,
    }[parsed["configure_target"]](config)
```

Note `_configure` currently receives only `parsed` (no `config`) in `_handlers`' mapping — it needs its own fresh `KubeConfig()` load here (not the one loaded for read-only commands in `run()`), since `configure` intentionally edits `config.raw`, not the defaults-applied `config.data` used everywhere else.

## `--json` on `list namespace` / `list pods`

Add a `--json` flag to the `list` subparser in `parser.py` (applies to both `list namespace` and `list pods` — add it once on the parent `list_parser`, not duplicated on each subcommand). In `executor.py`, `_list_namespace`/`_list_pods` branch on `parsed["json"]`:
- **Text mode (unchanged)**: existing `alias -> name` / grouped-by-alias printing.
- **JSON mode**: build a list of `{"alias": <alias or None>, "name": <real_name>}` for namespaces, and `{"alias": <alias>, "pods": [<name>, ...]}` per configured pod alias for `list pods`; print with `json.dumps(..., indent=2)`.

## Files to Change

- `python/kube/parser.py` — add `--json` flag to `_build_list`'s `list_parser`.
- `python/kube/executor.py` — replace `_configure` stub with real dispatch; branch `_list_namespace`/`_list_pods` on `--json`.
