# Add the example subcommand

Add `tingle kube example` end to end in the Python package, without loading
the config.

- `python/kube/example.py` (new): a small module exposing the example file
  path (`EXAMPLE_PATH = Path(__file__).resolve().parents[2] / "examples" /
  "kube" / "end_to_end.txt"`) and a `print_example()` function that reads it
  as UTF-8 and writes it to stdout unchanged. Handle a closed pipe
  (`BrokenPipeError`, e.g. `tingle kube example | head`) by exiting quietly
  (redirect stdout to devnull before exit, as Python's docs recommend) — no
  traceback.
- `python/kube/parser.py`: add `_build_example` registering an `example`
  subparser with no arguments; call it from `build()`; add
  `tingle kube example` to the module docstring usage.
- `python/kube/executor.py`: in `Kube.run()`, after parsing and **before**
  `KubeConfig()` is constructed, return early with `print_example()` when
  `parsed["subcommand"] == "example"`. Update the class/module docstrings that
  list subcommands.

Tests:

- `python/tests/kube/test_parser.py`: `example` parses to
  `{"subcommand": "example"}`; `example foo` and `example --json` raise
  `SystemExit` (usage error).
- `python/tests/kube/test_example.py` (new): `print_example()` /
  `Kube().run(["example"])` prints exactly `EXAMPLE_PATH.read_text("utf-8")`
  (compare to the file, not literal text); `EXAMPLE_PATH` exists; the file is
  ASCII-only.
- `python/tests/kube/test_executor_dispatch.py`: with `kube.executor.KubeConfig`
  and `kube.executor.check_aws_credentials` patched, `run(["example"])` never
  calls either (no config load/creation, no AWS check); a `BrokenPipeError`
  on write exits without a traceback.

## Files to Change

- `python/kube/example.py` — new: path constant and printer.
- `python/kube/parser.py` — `example` subparser + docstring.
- `python/kube/executor.py` — early dispatch before `KubeConfig()`.
- `python/tests/kube/test_parser.py` — parser cases.
- `python/tests/kube/test_example.py` — new: output and file checks.
- `python/tests/kube/test_executor_dispatch.py` — no-side-effect dispatch.
