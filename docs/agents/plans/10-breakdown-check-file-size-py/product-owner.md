# product-owner Plan: Breakdown check_file_size.py

Main plan: [plan.md](plan.md)

## Shared contracts

Documents the `python/common/arg_parser.py` `ArgParser` API and the
`python/<command>/` package layout exactly as `python` implements them (see
`plan.md`'s "Shared contracts" and `python.md`) — this doc should describe
that shape, not invent a different one.

## Implementation Steps

### Step 1 — Document the command breakdown pattern

Extend `docs/agents/architecture.md`'s `### python/` section (or add a new
subsection right after it) with the general pattern for breaking a command
down once it outgrows a single file:

- Commands are registered in `commands/*.json`, pointing at their
  implementation entry point; `bin/tingle` remains the single hub that
  dispatches to it.
- A command's entry point stays a thin shell: parse args, instantiate the
  orchestrator class, call it.
- Reusable/common code (e.g. the generic `ArgParser`) lives in
  `python/common/`.
- Argument parsing goes through the shared `ArgParser`
  (`python/common/arg_parser.py`): it takes a list of flag definitions and
  returns a `dict` of parsed values; command-specific code only supplies
  its flag definitions instead of building its own `argparse` setup.
- Beyond arg parsing, a command breaks its own logic down by class/file as
  needed — package-style, one file per class, orchestrator class named
  after the command.
- Reference `python/check_file_size/` as the first example of this
  pattern in practice.

## Files to Change

- `docs/agents/architecture.md` — document the command breakdown pattern
  described above.

## Notes

- Keep this scoped to documenting the pattern and pointing at
  `check_file_size` as the example — no changes to code.
