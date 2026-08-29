# python Plan: Context: switch + scope resolution

Main plan: [plan.md](plan.md)

## Overview

`python/kube/executor.py`'s `_switch` handler is currently a print stub. This plan implements it for real: resolve `context_alias` against `contexts` in the loaded config (or pass through the literal value with a notice), run an AWS credential pre-check, invoke `kubectx` to switch, and validate the result via `kubectl config current-context`. On an unresolvable context, list the available ones as a suggestion instead of a bare failure.

Two pieces are built as standalone, reusable functions rather than inlined into `_switch`, since later children (#22 Discovery, #23 Execution) are expected to call them too:

- **AWS pre-check** (`python/kube/auth.py`) — `aws sts get-caller-identity --profile <aws_profile>`.
- **Active-scope detection** (`python/kube/scope.py`) — `kubectl config current-context` → reverse lookup in `contexts` → alias.

Per the decision made when discussing this issue, neither is wired into `Kube.run()` globally — both are called only from `_switch` in this issue. `list`/`shell`/`configure` stay no-op stubs, unaffected.

## Context

- `python/kube/config.py`'s `KubeConfig` already loads, validates, and defaults `~/.tingle/kube/config.json`, exposing `.data` (with `contexts: dict[str, str]`, alias → real context name/ARN), `.pass_through`, and `.notice`.
- `python/kube/parser.py` already parses `switch <context_alias>` into `{"subcommand": "switch", "context_alias": <str>}` — no parser changes needed.
- `python/kube/executor.py`'s `Kube._switch` is currently:
  ```python
  @staticmethod
  def _switch(parsed: dict) -> None:
      """Stub handler for `kube switch <context_alias>` (real logic: issue #21)."""
      print(f"kube switch: not yet implemented (context_alias={parsed['context_alias']})")
  ```
- No `subprocess` calls exist anywhere in `python/` yet — this is the first command to shell out to an external CLI (`aws`, `kubectx`, `kubectl`). Use `subprocess.run(..., capture_output=True, text=True, check=False)` and inspect `returncode`/`stdout`/`stderr` directly; no existing wrapper to reuse.
- `python/pyproject.toml`'s `[tool.coverage.run]` only lists `source = ["check_file_size", "common"]` — `kube` isn't in the coverage source list yet (a gap from #20, unrelated to this issue's own tests, but this issue is the first to add real branching logic worth measuring).

## Steps

- [01 — Add the AWS pre-check module](python/01-add-aws-precheck.md)
- [02 — Add the scope/alias module](python/02-add-scope-module.md)
- [03 — Wire up the real switch handler](python/03-wire-up-switch.md)
- [04 — Add kube to the coverage source list](python/04-add-coverage-source.md)

## CI Checks

- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes

- `kubectx`'s own behavior on an unknown context name is the source of truth for detecting "nonexistent context" — confirm its exit code/stderr shape while implementing Step 3, and fall back to parsing `kubectl config get-contexts` output for the suggestion list if `kubectx` doesn't expose one cleanly.
- The config schema documented in the parent epic (#19) stores EKS contexts as ARNs (e.g. `arn:aws:eks:us-east-1:...:cluster/qa-cluster`); `kubectx <real_name>` is expected to work against those ARNs directly, since that's what `aws eks update-kubeconfig` registers as the context name.
