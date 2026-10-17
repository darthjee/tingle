# Add the --all flag to the parser

Add `--all` to the `pods` subparser in `KubeArgParser._build_list`, right
after `--namespace`: `action="store_true"`, help `Also list pods that match no
configured alias (within the given namespace)`. Update the usage docstrings to
`tingle kube list pods --namespace <alias> [--all]`.

## Files to Change

- `python/kube/parser.py` — add the `--all` argument to `pods_parser`; update
  the module docstring's usage line.
- `python/kube/executor.py` — update the module docstring's usage line.
- `python/tests/kube/test_parser.py` — `list pods --namespace web --all`
  parses to `all=True`; without the flag, `all=False`; `--all` placed before
  `--namespace` also parses.
