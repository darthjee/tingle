# Issue: Codacy: Pin versions in apt get install. Instead of `apt-get install <package>` use `apt-get install <package>=<version>`

## Description
Codacy's Hadolint check (`DL3008`, BestPractice, Warning) flags `shell/linux/Dockerfile:11`: the `apt-get install` call installs `coreutils`, `findutils`, `grep`, `sed`, `gawk`, `tar`, and `diffutils` without pinning versions, which makes image builds non-reproducible — a rebuild on a different day can silently pull a newer (or, after an Ubuntu archive prune, unavailable) package version.

- **Codacy issue ID**: `9b6732e2147e29b7c3647a5761d55a87`

## Problem
`shell/linux/Dockerfile` builds `FROM ubuntu:24.04` and installs its GNU toolbox packages unpinned:

```
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        coreutils \
        findutils \
        grep \
        sed \
        gawk \
        tar \
        diffutils \
    && rm -rf /var/lib/apt/lists/*
```

Without version pins, two builds of the same Dockerfile can produce images with different package versions, which is both a reproducibility gap and the specific pattern Codacy/Hadolint flags.

## Expected Behavior
The `apt-get install` line pins an explicit version for every package it installs, in the `<package>=<version>` form Hadolint's `DL3008` expects, so the Codacy finding clears and rebuilds are reproducible.

## Solution
Pin each package to its current `ubuntu:24.04` candidate version (verified via `apt-cache policy` against the `ubuntu:24.04` image on 2026-09-18):

| Package | Version |
|---|---|
| coreutils | 9.4-3ubuntu6.3 |
| findutils | 4.9.0-5build1 |
| grep | 3.11-4build1 |
| sed | 4.9-2ubuntu0.24.04.1 |
| gawk | 1:5.2.1-2ubuntu0.1 |
| tar | 1.35+dfsg-3ubuntu0.4 |
| diffutils | 1:3.10-1ubuntu0.1 |

Update `shell/linux/Dockerfile` to:

```
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        coreutils=9.4-3ubuntu6.3 \
        findutils=4.9.0-5build1 \
        grep=3.11-4build1 \
        sed=4.9-2ubuntu0.24.04.1 \
        gawk=1:5.2.1-2ubuntu0.1 \
        tar=1.35+dfsg-3ubuntu0.4 \
        diffutils=1:3.10-1ubuntu0.1 \
    && rm -rf /var/lib/apt/lists/*
```

Verify the build still succeeds (`docker build -f shell/linux/Dockerfile shell/linux`) after pinning, since a pinned version can already be gone from the archive by the time this lands.

## Benefits
- Reproducible image builds — the same Dockerfile always installs the same package versions.
- Clears the Codacy/Hadolint `DL3008` finding.
- Removes a class of "it worked yesterday" build-drift surprises.
