# Product-owner Plan: code_check: extract a shared docker_check module from rubycritic (no behaviour change)

Main plan: [plan.md](plan.md)

## Shared contracts

Document the layout in [plan.md](plan.md#shared-contracts) as the `python` agent ships it. If a name differs in the final code, the code wins: check `python/code_check/docker_check/` before writing.

## Implementation Steps

### Step 1 — Describe `docker_check` in the architecture doc
In `docs/agents/architecture.md` (around the "`python/code_check/rubycritic/` follows the same layout" section):

- Add a `python/code_check/docker_check/` subsection that lists each module (`constants.py`, `errors.py`, `docker_runner.py`, `image.py`, `selection.py`, `executor.py`) with a one-line role. Present it as the base for Docker-backed checks: a new check supplies a parser, a reporter, a config schema, flags, an image repository and an error subclass.
- Explain the parameterisation: `error_class`, `command`/`tool` (only the two tool-specific messages), `repo` with `version_file` passed at call time, `extensions` and `skip`, and the `DockerCheck` class attributes and hooks. Note that display filtering stays in each reporter.
- Rewrite the rubycritic layout list: `errors.py` now subclasses `DockerCheckError`, and `image.py`, `selection.py` and `docker_runner.py` are thin wrappers that keep the old signatures. Move the "Docker runner contract" bullets under `docker_check`. They are unchanged: they now describe the shared runner, and rubycritic's default image stays `darthjee/tingle_rubycritic:<version>`.
- Update the "`FileCollector` reuse" paragraph: `docker_check.selection` is now the consumer that imports `FileCollector` from `code_check.file_size.file_collector` with `binary_check=False` and `outside_symlinks=False`, and every Docker-backed check reaches it through `docker_check`.
- In the tests paragraph, mention `python/tests/code_check/docker_check/` next to the rubycritic tests (Docker is mocked the same way).

### Step 2 — Folder structure, if needed
Check `docs/agents/folder-structure.md`. It lists only top-level folders, so it most likely needs no change. Edit it only if it names `code_check` sub-packages.

## Files to Change
- `docs/agents/architecture.md` — add the `docker_check` section and update the rubycritic, `FileCollector` and tests paragraphs.
- `docs/agents/folder-structure.md` — only if it lists `code_check` sub-packages.

## CI Checks
- Markdown lint per `.markdownlint.json` (if run in CI).

## Notes
- User guides (`docs/guides/`) do not change: user-facing behaviour is identical.
- Run this after the `python` work, so the doc matches the final names.
