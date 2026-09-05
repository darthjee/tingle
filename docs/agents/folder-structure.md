# Folder Structure

## Project Root

| Directory / File | Description |
|-----------------|-------------|
| `bin/`          | Callable entry points meant to be on `PATH`; each thin wrapper dispatches into the matching script under `shell/`, `python/`, or `node/`. |
| `scripts/`      | CI/release tooling scripts (not user-facing commands — see `bin/` for those). Currently holds `scripts/release_image.sh`, the `tingle-linux` Docker image build/publish/description script invoked by `.circleci/config.yml`. |
| `shell/`        | Bash/Shell utility scripts. |
| `python/`       | Python utility scripts. |
| `node/`         | Node.js utility scripts. |
| `completions/`  | Holds the bash completion scripts for `tingle`: `completions/tingle.bash` (central hub, sourced from `~/.bashrc` by `tingle install`), `completions/bash/tingle.sh` (level-one: command names), and `completions/bash/commands.sh` (level-two: command-specific args, delegating to a command's `completion.<ext>` via `tingle resolve <cmd>`, or falling back to native file/folder completion). |
| `docs/agents/`  | Agent-facing documentation (architecture, flow, plans, issues). |
| `.github/`      | GitHub templates (PR and commit message templates, Copilot instructions). |
| `README.md`     | Project overview, name origin, and usage instructions. |
| `LICENSE`       | MIT license. |
