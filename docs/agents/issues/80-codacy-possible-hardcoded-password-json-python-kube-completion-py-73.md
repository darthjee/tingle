# Issue: Codacy: Possible hardcoded password: '--json' (python/kube/completion.py:73)

## Description
Codacy's Bandit scanner flags line 73 of `python/kube/completion.py` as `B105` ("Possible hardcoded password") because the code compares a token against the string literal `--json`. Bandit's B105 check pattern-matches string-equality comparisons against literals that look password-like; `--json` is a CLI flag name being recognized during bash-completion scanning, not a credential.

This is the same false-positive pattern already suppressed for the `--namespace` comparison on line 76 (fixed under issue #79 / PR #91), which was merged without also covering the `--json` comparison a few lines above it.

## Problem
In `_scan()` (`python/kube/completion.py`), the line `if token == "--json":` (line 73) is flagged by Codacy/Bandit as pattern `Bandit_B105`, severity High. There is no authentication or credential handling in this function — it only classifies completion tokens — so the finding is a false positive, but it still surfaces as one of the repository's worst code-quality findings in Codacy.

## Expected Behavior
Codacy should no longer report a B105 finding for this line, while the completion logic's behavior is unchanged.

## Solution
Add a `# nosec B105 - CLI flag literal, not a credential` suppression comment to the `if token == "--json":` line (73), mirroring the comment already present on the `--namespace` branch (line 76).

## Benefits
Clears a High-severity false positive from Codacy's findings, consistent with the precedent already established for the sibling `--namespace` check.
