# Rewire .circleci/config.yml to call the script

Replace the inline `run:` command bodies in `build-and-publish-linux-image`
and `update-description` with thin calls into
`scripts/release_image.sh <subcommand>` (written in step 01). Do **not**
change the workflow structure — job names, `requires:
[build-and-publish-linux-image]` on `update-description`, or the
`filters: { tags: { only: /v.*/ }, branches: { ignore: /.*/ } }` blocks on
both jobs all stay exactly as they are today.

Target shape for `build-and-publish-linux-image`'s steps (replacing the
current "Build image" / "Smoke test - GNU sed" / "Smoke test - non-root
user" / "Publish image" `run:` blocks):

```yaml
  build-and-publish-linux-image:
    machine: true
    steps:
      - checkout
      - run:
          name: Build image
          command: scripts/release_image.sh build
      - run:
          name: Smoke test
          command: scripts/release_image.sh smoke-test
      - run:
          name: Publish image
          command: scripts/release_image.sh publish
```

Target shape for `update-description`:

```yaml
  update-description:
    machine: true
    steps:
      - checkout
      - run:
          name: Update Docker Hub description
          command: scripts/release_image.sh update-description
```

(Exact step names/grouping above are a starting point — adjust to whatever
reads cleanest once `release_image.sh`'s actual subcommand names are
finalized in step 01, as long as no bash logic beyond a single script
invocation remains inline.)

## Files to Change
- `.circleci/config.yml` — replace both jobs' `run:` bodies with calls into
  `scripts/release_image.sh`, as described above.
