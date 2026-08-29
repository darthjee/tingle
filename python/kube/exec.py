"""
exec.py — Interactive exec and ambiguity-prompt helpers for kube.

Standalone, reusable pieces for the `shell` command: launching an
interactive `kubectl exec` session (inheriting the terminal's stdio rather
than capturing it) and prompting the user to disambiguate between multiple
matching pods. Dumb wrappers only — no alias resolution or filtering here
(see `scope.py`/`inventory.py`/`matching.py`). Never raise — callers print
their own messages and decide how to proceed.
"""

from __future__ import annotations

import subprocess


def exec_shell(namespace: str, pod: str, shell: str) -> tuple[bool, str | None]:
    """Launch an interactive `kubectl exec -it` session in `pod`.

    Runs `kubectl exec -n <namespace> -it <pod> -- <shell>` without
    capturing stdout/stderr, so the child process's stdio (and therefore
    the interactive TTY session) is inherited directly by the calling
    terminal. Returns a `(success, error)` tuple, mirroring
    `scope.switch_context`'s shape: `error` is `None` on success, or a
    message derived from the exit code on failure.
    """
    result = subprocess.run(
        ["kubectl", "exec", "-n", namespace, "-it", pod, "--", shell],
        check=False,
    )
    if result.returncode != 0:
        return False, f"kubectl exec exited with status {result.returncode}"

    return True, None


def prompt_pod_choice(candidates: list[dict]) -> dict | None:
    """Prompt the user to pick one of `candidates` (ordered as given).

    Prints the candidate pod names as a numbered list and reads a
    selection from stdin. Reprompts on non-numeric or out-of-range input.
    Returns the chosen pod dict, or `None` if the user gives up (empty
    input).
    """
    for index, pod in enumerate(candidates, start=1):
        print(f"{index}) {pod['metadata']['name']}")

    while True:
        choice = input("Select a pod: ").strip()
        if not choice:
            return None

        if not choice.isdigit():
            print("Please enter a number.")
            continue

        selection = int(choice)
        if selection < 1 or selection > len(candidates):
            print(f"Please enter a number between 1 and {len(candidates)}.")
            continue

        return candidates[selection - 1]
