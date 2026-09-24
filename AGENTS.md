# Project Instructions

Last updated: 2026-09-24

You are an assistant helping maintain Tingle, a personal collection of small,
independent utility scripts.

Tingle is a personal repository of everyday utility scripts — a code "Swiss Army
knife". It has no single theme; each script is a small, independent tool for a
recurring task such as file scraping, bulk renaming, or copying files between
git branches.

## Stack

- **Shell** (Bash) — `shell/`
- **Python** — `python/`
- **Node.js** — `node/`

## Conventions

- **Should**: Scripts are independent and runnable on their own — avoid
  introducing cross-script dependencies unless truly shared.
- **Should**: Each script document its own usage and dependencies in a
  header comment.
- **Should**: New scripts be added to the table in `README.md`.

## Boundaries

- **Never**: introduce cross-script dependencies unless truly shared.
- **Must**: document a script's usage and dependencies in a header comment
  whenever it is added or modified, unless the change does not affect its
  usage or dependencies (e.g. typo fixes, formatting, internal refactors).
- **Must**: add a new script to the table in `README.md`, unless it is an
  internal helper not meant to be invoked directly.
- **Never**: place implementation code outside `shell/`, `python/`,
  `node/`, or `bin/`, except for build, release, install and CI tooling and
  config (e.g. `Makefile`, `scripts/`, `install/`, `completions/`,
  `commands/`, `docker-compose.yml`, `.circleci/`, `.github/`).
- **Never**: place documentation anywhere other than `docs/guides/`
  (user-facing guides) or `docs/agents/` (agent-facing docs), except for
  root-level files required by tooling or convention (`README.md`,
  `AGENTS.md`, `CLAUDE.md`, `DOCKERHUB_DESCRIPTION.md`, and
  templates/instructions under `.github/`).
- **Must**: update the relevant file(s) under `docs/agents/` whenever an
  architectural change is made; if no existing file covers the area, add
  one and list it in the Documentation table.
- **Must**: update the matching guide in `docs/guides/` whenever a
  command's user-visible behaviour changes; if the command has no guide
  yet, note that in the PR description.

## Tools

Specialist agents are defined under `.claude/agents/`, which holds their
full descriptions. Delegate work to the agent that owns the area:

- `architect` — cross-cutting tasks, multi-agent coordination, root-level
  files.
- `cli` — entry points under `bin/` (arg parsing, `--help`, exit codes,
  dispatch into the language folders).
- `node` — Node.js scripts under `node/`.
- `python` — Python scripts under `python/`.
- `shell` — Bash/Shell scripts under `shell/`.
- `product-owner` — content under `docs/agents/` (architecture, flow, folder
  structure, contributing, issues, plans).
- `guide` — content under `docs/guides/` (end-user guides, one per `tingle`
  command, and the guides index).

## Documentation

Agent-facing project documentation lives under
[`docs/agents/`](docs/agents/); end-user guides live under
[`docs/guides/`](docs/guides/README.md):

| File | Contents |
|------|----------|
| [Folder Structure](docs/agents/folder-structure.md) | Top-level directory layout and the role of each folder. |
| [Architecture](docs/agents/architecture.md) | Source layout, modules, code style, and implementation guidelines. |
| [Flow](docs/agents/flow.md) | Main runtime flow of the application. |
| [Plans](docs/agents/plans/) | Implementation plans for ongoing or upcoming features. |
| [Issues](docs/agents/issues/) | Detailed specs for open issues. |
| [Contributing](docs/agents/contributing.md) | Commit guidelines, PR standards, code organization, and refactoring rules. |
| [User Guides](docs/guides/README.md) | End-user guides, one per `tingle` command. |

### Issues (`docs/agents/issues/`)

Each file documents an issue in detail. Naming convention:

```
docs/agents/issues/<issue_id>_<issue_name>.md
```

Example: `docs/agents/issues/5_release_docker_image.md` for issue #5.

### Plans (`docs/agents/plans/`)

Each plan is a directory named after the issue ID and topic, containing one or more related files:

```
docs/agents/plans/<issue_id>_<topic>/<related_files>.md
```

Example: `docs/agents/plans/12_add-auth/plan.md` for issue #12.
