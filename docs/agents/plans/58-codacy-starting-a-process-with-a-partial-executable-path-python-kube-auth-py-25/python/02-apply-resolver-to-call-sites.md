# Use the resolver at every subprocess.run call site

Replace the bare `"aws"`/`"kubectl"`/`"kubectx"` first element of every `subprocess.run` argument list in the four flagged files with `binaries.resolve("aws")` / `binaries.resolve("kubectl")` / `binaries.resolve("kubectx")`, and update each site's `# nosec` comment from `B603` to `B603, B607` (both are now genuinely addressed: B603 by the fixed, list-form, no-shell call; B607 by resolving the absolute path).

## Files to Change
- `python/kube/auth.py` — import `binaries`; in `check_aws_credentials`, replace `"aws"` with `binaries.resolve("aws")` in the `subprocess.run` args list; update the `# nosec` comment to `B603, B607`.
- `python/kube/exec.py` — import `binaries`; in `exec_shell`, replace `"kubectl"` with `binaries.resolve("kubectl")`; update the `# nosec` comment.
- `python/kube/inventory.py` — import `binaries`; in `list_namespaces`, `get_pod`, and `list_pods`, replace each `"kubectl"` with `binaries.resolve("kubectl")`; update each `# nosec` comment.
- `python/kube/scope.py` — import `binaries`; in `switch_context` (both the `kubectx` call and the `kubectl config current-context` call), `list_available_contexts`, and `detect_active_scope`, replace `"kubectx"`/`"kubectl"` with `binaries.resolve("kubectx")`/`binaries.resolve("kubectl")`; update each `# nosec` comment.
