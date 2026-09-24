# Plan: Codacy: Possible hardcoded secret key (secret) (python/kube/auth.py:26)

Issue: [192-codacy-possible-hardcoded-secret-key-secret-python-kube-auth-py-26.md](../../issues/192-codacy-possible-hardcoded-secret-key-secret-python-kube-auth-py-26.md)

## Overview
Silence the false-positive Prospector/dodgy (#192) and Bandit B105 (#193) findings on `python/kube/auth.py:26` with a single justified inline suppression comment. No behavioural change.

See [python.md](python.md) for the full plan.
