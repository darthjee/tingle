# TODO

Outstanding setup items to fill in once the repo has real scripts and tooling
in place.

## Lint/check commands per agent

No linter config exists yet. Once scripts are added, set these up and wire
each into a `.claude/scripts/check_<agent-name>.sh`:

- `shell` — `shellcheck shell/**/*.sh`
- `python` — `ruff check python/`
- `node` — `npx eslint node/`
- `cli` — check command for `bin/` entry points (TBD once conventions are set)
