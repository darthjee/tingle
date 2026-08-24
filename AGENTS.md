# Project Instructions

Tingle is a personal repository of everyday utility scripts — a code "Swiss Army
knife". It has no single theme; each script is a small, independent tool for a
recurring task such as file scraping, bulk renaming, or copying files between
git branches.

## Stack

- **Shell** (Bash) — `shell/`
- **Python** — `python/`
- **Node.js** — `node/`

## Conventions

- Scripts are independent and runnable on their own — avoid introducing
  cross-script dependencies unless truly shared.
- Each script should document its own usage and dependencies in a header
  comment.
- New scripts should be added to the table in `README.md`.

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
