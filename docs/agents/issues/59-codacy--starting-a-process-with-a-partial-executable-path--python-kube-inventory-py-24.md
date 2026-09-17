# Codacy: Starting a process with a partial executable path (python/kube/inventory.py:24)

## Context

Codacy flagged `python/kube/inventory.py:24` with Bandit rule `B607`
("starting a process with a partial executable path"), category Security,
severity Warning. Codacy issue ID: `7c4dc0f61f8e2a4d92c4867d95f1b675`.

The finding is against a `subprocess.run` call in `python/kube/inventory.py`
that invoked `kubectl` by its bare name instead of a resolved absolute path,
which is the class of issue Bandit's B607 check flags.

## What needs to be done

- Verify whether `python/kube/inventory.py`'s `subprocess.run` call sites
  already resolve the `kubectl` executable to an absolute path (e.g. via a
  shared resolver helper) and carry the appropriate `# nosec` annotation for
  B607.
- If the finding is still present, resolve the executable path before
  invoking `subprocess.run`, consistent with how other `python/kube` call
  sites address the same Bandit rule.
- If the finding was already resolved by prior work in this codebase, close
  out the issue by confirming/documenting that the flagged line is already
  compliant, and add or update tests/comments only if needed for clarity.

## Acceptance criteria

- [ ] `python/kube/inventory.py:24` (or the current line for the flagged
      `subprocess.run` call) uses a resolved, non-partial path to the
      `kubectl` executable, with a `# nosec B607`-style annotation
      explaining why the remaining risk is acceptable.
- [ ] Existing tests in `python/tests/kube/test_inventory.py` continue to
      pass and reflect the current behavior.
