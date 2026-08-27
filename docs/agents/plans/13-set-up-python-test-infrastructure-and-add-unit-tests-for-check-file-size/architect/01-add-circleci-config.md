# Add CircleCI config

Create `.circleci/config.yml` (new top-level folder — owned by `architect`,
see this issue's dialogue). A single job runs lint + tests directly on a
stock CircleCI image, no custom/published base image and no multi-arch
build (scoped down from the `darthjee/majora` pattern — see issue and
`plan.md` for rationale).

Job shape:

```yaml
version: 2.1

workflows:
  version: 2
  test:
    jobs:
      - test

jobs:
  test:
    docker:
      - image: cimg/python:3.11
    working_directory: ~/project/python
    steps:
      - checkout:
          path: ~/project
      - run:
          name: Install dependencies
          command: pip install -r requirements-dev.txt
      - run:
          name: Lint
          command: ruff check .
      - run:
          name: Tests
          command: pytest
```

`cimg/python:3.11` already runs as a non-root `circleci` user by default, so
no extra user setup is needed here (unlike `python/Dockerfile`, see
`python.md`).

## Files to Change

- `.circleci/config.yml` — new file, single `test` job (lint + pytest) as
  shown above.
