# Add interactive-exec and ambiguity-prompt helpers

Two standalone, reusable pieces `Kube._shell` will call into, following the module split already used by `scope.py`/`inventory.py`/`matching.py` (dumb wrappers, no alias resolution, no printing beyond what's documented, never raise):

- **Interactive exec** — a new function (e.g. `exec_shell(namespace, pod, shell)` in a new `kube/exec.py`) wrapping `kubectl exec -n <ns> -it <pod> -- <shell>` via `subprocess.run`, deliberately **without** `capture_output=True`/`text=True` capture of stdout/stderr, so the child process's stdio (and therefore the interactive TTY session) is inherited directly by the terminal. Returns just the process's exit code (or a `(success, error)` tuple consistent with the other wrappers — pick whichever this repo's reviewer prefers, `switch_context`'s shape is the closest precedent).
- **Ambiguity prompt** — a new function (e.g. `prompt_pod_choice(candidates)` in the same new module or `kube/matching.py`) that prints the list of candidate pod names (in the order they're given — callers pass `match_pods`'s already-deterministically-ordered list) and reads a selection from stdin (`input()`), returning the chosen pod dict. Invalid input handling (non-numeric, out-of-range) is this function's responsibility — reprompt or default to a clear error, whichever keeps the implementation simplest.

## Files to Change

- `python/kube/exec.py` (new) — `exec_shell` and `prompt_pod_choice` (or split across two functions/files if that reads cleaner — this is an implementation judgment call, not a hard requirement).
- `python/tests/kube/test_exec.py` (new) — cover `exec_shell` (asserts the exact `subprocess.run` call args, especially the absence of `capture_output`) and `prompt_pod_choice` (valid selection, invalid input handling), mocking `subprocess.run`/`input` as needed.
