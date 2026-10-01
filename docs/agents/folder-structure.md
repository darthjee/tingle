# Folder Structure

## Project Root

| Directory / File | Description |
|-----------------|-------------|
| `bin/`          | Callable entry points meant to be on `PATH`; each thin wrapper dispatches into the matching script under `shell/`, `python/`, or `node/`. |
| `scripts/`      | CI/release tooling scripts (not user-facing commands — see `bin/` for those). Holds `scripts/release_image.sh`, the Docker image build/publish/description script for `darthjee/tingle` and, with the `rubycritic` selector, `darthjee/tingle_rubycritic` — see [tingle-linux-image.md](tingle-linux-image.md) and [tingle-rubycritic-image.md](tingle-rubycritic-image.md) — and `scripts/release_cli.sh`, the `tingle` release-zip build/publish script — see [tingle-release-zip.md](tingle-release-zip.md) — both invoked by `.circleci/config.yml`. |
| `dist/`         | Git-ignored build-output directory for `scripts/release_cli.sh` (`tingle-<tag>.zip` + `.sha256` sidecar). Not committed, not packaged into the release zip. |
| `docker/`       | Docker images for `tingle code_check` checks, one sub-folder per image (`docker/rubycritic/` builds `tingle_rubycritic`, see [tingle-rubycritic-image.md](tingle-rubycritic-image.md)). Owned by the `shell` agent. |
| `shell/`        | Bash/Shell utility scripts. |
| `python/`       | Python utility scripts. |
| `node/`         | Node.js utility scripts. |
| `completions/`  | Holds the bash completion scripts for `tingle`: `completions/tingle.bash` (central hub, sourced from `~/.bashrc` by `tingle install`), `completions/bash/tingle.sh` (level-one: command names), and `completions/bash/commands.sh` (level-two: command-specific args, delegating to a command's `completion.<ext>` via `tingle resolve <cmd>`, or falling back to native file/folder completion — also used when a handler prints exactly the sentinel `__tingle_files__`). |
| `docs/agents/`  | Agent-facing documentation only (architecture, flow, plans, issues, and the specs index `specs.md` with temporary feature specs under `specs/`); not end-user guides. |
| `docs/guides/`  | End-user guides, one per `tingle` command, indexed by `docs/guides/README.md`. Owned by the `guide` agent. |
| `.github/`      | GitHub templates (PR and commit message templates, Copilot instructions). |
| `README.md`     | Project overview, name origin, and usage instructions. |
| `LICENSE`       | MIT license. |
