# Project Instructions

Last updated: 2026-09-20

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
  whenever it is added or modified.
- **Must**: add a new script to the table in `README.md`.
- **Never**: place implementation code outside `shell/`, `python/`,
  `node/`, or `bin/`, or documentation outside `docs/agents/`.
- **Must**: update the relevant file(s) under `docs/agents/` whenever an
  architectural change is made.

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

## Documentation

All project documentation lives under [`docs/agents/`](docs/agents/):

| File | Contents |
|------|----------|
| [Folder Structure](docs/agents/folder-structure.md) | Top-level directory layout and the role of each folder. |
| [Architecture](docs/agents/architecture.md) | Source layout, modules, code style, and implementation guidelines. |
| [Flow](docs/agents/flow.md) | Main runtime flow of the application. |
| [Plans](docs/agents/plans/) | Implementation plans for ongoing or upcoming features. |
| [Issues](docs/agents/issues/) | Detailed specs for open issues. |
| [Contributing](docs/agents/contributing.md) | Commit guidelines, PR standards, code organization, and refactoring rules. |

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
