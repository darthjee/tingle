# Split lint and tests jobs
Replace the single `test` job in `.circleci/config.yml` with two jobs, `lint` and `tests`, both using the same `cimg/python:3.11` image, `~/project/python` working directory, checkout, and dependency-install steps as today. `lint` runs `ruff check .`; `tests` runs `pytest`. Add both jobs to the `test` workflow so they run in parallel.

## Files to Change
- `.circleci/config.yml` — split the `test` job into `lint` and `tests` jobs, each with its own `Install dependencies` step, and list both under `workflows.test.jobs`.
