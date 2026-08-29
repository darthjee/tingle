# Require --namespace on list pods

Make `--namespace` mandatory on `tingle kube list pods`, per the discussion outcome (no implicit default namespace — omitting it is a usage error). Currently `KubeArgParser._build_list` declares it with `default=None`, so argparse itself needs `required=True` (argparse allows `required=True` on an optional-style flag).

## Files to Change

- `python/kube/parser.py` — `_build_list`: add `required=True` to the `--namespace` argument on the `pods` subparser.
- `python/tests/kube/test_parser.py` — add a test asserting `kube list pods` (no `--namespace`) raises `SystemExit` (argparse's usage-error behavior), alongside the existing happy-path parse test(s).
