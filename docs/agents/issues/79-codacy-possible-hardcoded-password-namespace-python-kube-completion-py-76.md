# Issue: Codacy: Possible hardcoded password: '--namespace' (python/kube/completion.py:76)

## Description
Codacy's Bandit scan (rule `B105: hardcoded_password_string`) flags `python/kube/completion.py:76` as a possible hardcoded password:

```python
elif token == "--namespace":
```

This is a false positive: `"--namespace"` is a CLI flag name being matched during positional argv scanning in `_scan()`, not a credential. Bandit's B105 heuristic flags any string comparison against certain literal patterns regardless of whether the literal actually holds a secret.

## Problem
The finding shows up in Codacy as a High-severity Security issue, which is misleading — no credential is hardcoded here — and it inflates the repo's reported security issue count.

## Expected Behavior
Codacy should stop reporting this line as a security issue, while the underlying B105 detection rule remains active for genuine cases elsewhere in the codebase.

## Solution
Add an inline `# nosec B105` suppression comment on `python/kube/completion.py:76`, with a short rationale (e.g. "CLI flag name, not a credential"), following the same convention already used for the B603/B607 subprocess false positives in `python/kube/{scope,auth,exec,inventory}.py` (issue #57).

## Benefits
- Removes a misleading High-severity security finding from Codacy.
- Keeps the B105 check active for real hardcoded-secret cases.
- Consistent with the existing suppression convention already established in `python/kube/`.
