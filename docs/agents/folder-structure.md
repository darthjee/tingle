# Folder Structure

## Project Root

| Directory / File | Description |
|-----------------|-------------|
| `bin/`          | Callable entry points meant to be on `PATH`; each thin wrapper dispatches into the matching script under `shell/`, `python/`, or `node/`. |
| `shell/`        | Bash/Shell utility scripts. |
| `python/`       | Python utility scripts. |
| `node/`         | Node.js utility scripts. |
| `completions/`  | Holds the bash completion script(s) for `tingle` (`completions/tingle.bash`), sourced from `~/.bashrc` by `tingle install`. |
| `docs/agents/`  | Agent-facing documentation (architecture, flow, plans, issues). |
| `.github/`      | GitHub templates (PR and commit message templates, Copilot instructions). |
| `README.md`     | Project overview, name origin, and usage instructions. |
| `LICENSE`       | MIT license. |
