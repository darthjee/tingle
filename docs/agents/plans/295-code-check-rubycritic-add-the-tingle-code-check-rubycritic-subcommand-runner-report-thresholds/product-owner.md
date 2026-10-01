# Product-Owner Plan: code_check rubycritic: add the tingle code_check rubycritic subcommand

Main plan: [plan.md](plan.md)

## Shared contracts

What this agent relies on, produced by `python`:
- Package `python/code_check/rubycritic/` with these modules:
  - `constants.py`, `errors.py`, `flags.py` (import-light `FLAGS`), `image.py`
  - `selection.py`, `docker_runner.py`, `output_parser.py`, `reporter.py`
  - `executor.py` (`CheckRubycritic`, `PROG = "tingle code_check rubycritic"`)
  - Confirm the final names against the `python` agent's work.
- `SUBCOMMANDS["rubycritic"] = (CheckRubycritic, "Ruby code complexity via RubyCritic (Docker).")`.
- `SUBCOMMAND_NAMES = ("file_size", "rubycritic")`.
- `FileCollector` gains a keyword-only `binary_check=True`. rubycritic passes `False` and imports `FileCollector` from `file_size/` directly.
- The Docker run line and the default image, as in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Update docs/agents/architecture.md
**"Breaking a command down once it outgrows a single file"** (~lines 103-110)
- Add a sibling paragraph for `python/code_check/rubycritic/` that lists its modules and their roles.
- Summarise the Docker runner contract:
  - preflight: `which docker`, then `docker info` with a 30 s timeout;
  - `image inspect`, then a pull to stderr;
  - the `docker run` line with stdin paths;
  - the default image `darthjee/tingle_rubycritic:<version>`, with the version read from `shell/linux/VERSION` relative to the module path;
  - no Docker-in-Docker.
- Link to `specs/code_check/rubycritic/subcommand.md` §3–4 rather than copying it.
- Document the cross-subcommand reuse of `FileCollector` and its `binary_check` kwarg. State it as an intentional exception to the "move a helper up once a second consumer needs it" rule (~lines 133-135).

**"Subcommand dispatch"** (~line 121)
- Show both `SUBCOMMANDS` entries in the example.
- Note that `SUBCOMMAND_NAMES` must stay in sync with `SUBCOMMANDS` (a test enforces it).

**Completion bullet** (~lines 64-66)
- Note that each subcommand's completion is driven by its own `flags.FLAGS`.

**Test folder location** (~line 181), optional
- Add `python/tests/code_check/rubycritic/`.
- Note that `shutil.which` and `subprocess.run` are mocked, so Docker never runs in tests.

### Step 2 — Align the spec wording on the guide location
In `docs/agents/specs/code_check/rubycritic/file-selection.md` §7 and `config.md`:
- References to "the `rubycritic` section of `docs/guides/code_check.md`" should point at the new page `docs/guides/code_check/rubycritic.md`.
- This keeps #296 and #297 consistent with the page this issue creates.

## Files to Change
- `docs/agents/architecture.md`: rubycritic package, Docker runner summary, `FileCollector` reuse exception, dispatch example and completion note.
- `docs/agents/specs/code_check/rubycritic/file-selection.md`: guide location wording.
- `docs/agents/specs/code_check/rubycritic/config.md`: guide location wording.

## Notes
- `folder-structure.md`, `flow.md` and `specs.md` need no change. The `docker/rubycritic/` folder and the specs index are already covered.
- Run after the `python` agent, so the module names match the code.
