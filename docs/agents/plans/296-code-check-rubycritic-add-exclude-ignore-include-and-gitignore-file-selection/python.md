# Python Plan: code_check rubycritic: add --exclude/--ignore/--include and .gitignore file selection

Main plan: [plan.md](plan.md)

## Shared contracts

Produces the five flags exactly as listed in [plan.md](plan.md#shared-contracts)
(names, argparse types/actions, defaults and help texts), and the behaviour
(filter order, gitignore, symlink confinement, single-file rules) described
there. The cli and guide agents document these.

## Steps

- [01 — Add outside_symlinks to FileCollector](python/01-file-collector-outside-symlinks.md)
- [02 — Share the excludes helper](python/02-shared-excludes-helper.md)
- [03 — Add the rubycritic flags](python/03-rubycritic-flags.md)
- [04 — Wire selection and executor](python/04-selection-and-executor.md)
- [05 — Tests](python/05-tests.md)

## CI Checks

- `python/`: `ruff check .` (CI job: `lint`)
- `python/`: `pytest` (or `docker-compose run --rm tingle_tests pytest` from the repo root; CI job: `tests`, coverage must stay >= 75%)

## Notes

- Turning `.gitignore` on by default makes `GitIgnore.ignored_paths` call the
  global `subprocess.run`, which the rubycritic executor tests patch for Docker.
  Add an autouse fixture that stubs `GitIgnore.ignored_paths` (returns `None`)
  in `python/tests/code_check/rubycritic/test_executor.py`, or make the fakes
  ignore `git` calls.
- `completion.py` must not import `file_collector`, `selection` or executors
  (`test_completion_imports_no_heavy_module`); keep the excludes helper out of
  `flags.py`.
- `file_size`'s existing collector and executor tests must pass unchanged.
- Out of scope: `rubycritic` config section and `--no-config` (#297), spec removal (#298).
