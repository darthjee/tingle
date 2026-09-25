# CircleCI job and Docker Hub description

Wire the new flow into CI, and state the supported platforms on Docker Hub.

- In `.circleci/config.yml`, job `build-and-publish-linux-image`:
  - replace `machine: true` with a pinned machine image, so a recent Docker with buildx is guaranteed:

    ```yaml
    machine:
      image: ubuntu-2404:current
    ```

    If Codacy or CircleCI prefer a dated tag, use the current dated `ubuntu-2404:<YYYY.MM.N>`;
  - add a first run step, `Set up builder`: `scripts/release_image.sh setup-builder`, before `Build image`. The other steps (`build`, `smoke-test`, `publish`) stay in the same job, so the builder cache is shared.
- In `DOCKERHUB_DESCRIPTION.md`, add a short "Supported platforms: `linux/amd64`, `linux/arm64`" line near the image description. Keep all links absolute. This is a root-level file that the shell agent has edited before (#182), and it is pushed by the `update-description` job on release.

## Files to Change
- `.circleci/config.yml` — pinned machine image and the `Set up builder` step.
- `DOCKERHUB_DESCRIPTION.md` — supported platforms line.
