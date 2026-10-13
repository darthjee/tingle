# Product-owner Plan: code_check js_complexity: add the tingle code_check js_complexity subcommand

Main plan: [plan.md](plan.md)

## Shared contracts

You rely on the values in [plan.md](plan.md#shared-contracts) (the name, the one-line description and the module layout produced by `python`).

## Implementation Steps

### Step 1 — Document the package in `docs/agents/architecture.md`
- After the `python/code_check/rubycritic/` section, add `python/code_check/js_complexity/` "follows the same layout, built on `docker_check`", listing each module:
  - `executor.py`: `CheckJsComplexity`, with the `_load_config` and selection overrides until #321/#322;
  - `constants.py`, `errors.py`, `flags.py`;
  - `image.py`, `docker_runner.py`, `selection.py`: thin wrappers, with the declaration-file `skip` predicate;
  - `output_parser.py`: the merged-JSON contract, validated in full;
  - `reporter.py`.
- Add `code_check.js_complexity.flags` to the completion paragraph (around line 68) next to the file_size and rubycritic flags modules.

### Step 2 — Update the `README.md` command table
In the `code_check` row, add `[`js_complexity`](docs/guides/code_check/js_complexity.md), JavaScript/TypeScript code complexity via FTA (Docker)` after rubycritic. Also check the line around `README.md:44`, which names the commands that need Docker, and add `tingle code_check js_complexity` there.

## Files to Change
- `docs/agents/architecture.md`: the js_complexity package section and the completion paragraph.
- `README.md`: the `code_check` row and the Docker-requirements sentence.

## Notes
- The `docs/agents/specs/code_check/js_complexity/` folder stays until #327 removes it. Do not delete or edit it here, apart from fixing a factual mismatch found during implementation.
