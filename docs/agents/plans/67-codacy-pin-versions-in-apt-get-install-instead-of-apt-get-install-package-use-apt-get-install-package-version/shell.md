# Shell Plan: Codacy: Pin versions in apt get install. Instead of `apt-get install <package>` use `apt-get install <package>=<version>`

Main plan: [plan.md](plan.md)

## Implementation Steps

### Step 1 — Pin package versions in `shell/linux/Dockerfile`
Update the `apt-get install` line to pin each package to its current `ubuntu:24.04` candidate version, in Hadolint's `<package>=<version>` form:

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

Versions verified via `apt-cache policy <pkg>` inside a fresh `ubuntu:24.04` container on 2026-09-18 — re-verify before landing, since a pinned version can already be gone from the Ubuntu archive by the time this ships. If a pinned version 404s, replace only that package's pin with the then-current candidate version, keeping the rest unchanged.

### Step 2 — Verify the image still builds and passes the existing smoke test
Run the same commands CI runs (see `## CI Checks` below) locally to confirm the pinned versions resolve and the image still behaves as expected.

## Files to Change
- `shell/linux/Dockerfile` — pin `coreutils`, `findutils`, `grep`, `sed`, `gawk`, `tar`, `diffutils` to explicit versions in the `apt-get install` line.

## CI Checks
- `shell/linux`: `scripts/release_image.sh build && scripts/release_image.sh smoke-test` (CI job: `build-and-publish-linux-image`)

## Notes
- Package versions in the Ubuntu archive can be superseded or pruned; if a pinned version is unavailable at implementation time, look up the then-current candidate via `apt-cache policy <pkg>` in a fresh `ubuntu:24.04` container and pin that instead.
