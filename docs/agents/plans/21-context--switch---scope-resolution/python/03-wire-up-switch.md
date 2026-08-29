# Wire up the real switch handler

Replace `Kube._switch`'s print stub with the real flow, composed from the `auth` and `scope` modules built in Steps 1-2:

1. Resolve `context_alias` against `config.data["contexts"]` via `scope`'s alias resolution — print the pass-through notice if it falls back to the literal value.
2. Run the AWS pre-check (`auth.check_aws_credentials`) using `config.data["aws_profile"]`. On failure, print a clear abort message (including the captured stderr) and return without calling `kubectx`.
3. Switch via `kubectx <real_name>` and validate via `kubectl config current-context`, using `scope`'s switch+validate function.
4. If the context doesn't exist (`kubectx`/validation fails), print the available contexts (via `scope`'s listing function) as a suggestion instead of a bare failure.

`_switch` stops being a `@staticmethod` taking only `parsed` if it needs the loaded `KubeConfig` — thread `config` through from `Kube.run()` the same way `pass_through`/`notice` already are, rather than reloading it inside `_switch`.

## Files to Change

- `python/kube/executor.py` — implement `_switch` using `auth.check_aws_credentials` and `scope`'s functions; pass the already-loaded `config` into it from `run()`.
- `python/tests/kube/test_executor.py` (new) — unit tests covering `_switch`'s full flow: alias resolved + successful switch, pass-through alias + successful switch, AWS pre-check failure (asserts `kubectx` is never called), and nonexistent context (asserts the suggestion list is printed). Mock `auth`/`scope` at the boundary rather than `subprocess` directly, since those modules already have their own unit tests.
