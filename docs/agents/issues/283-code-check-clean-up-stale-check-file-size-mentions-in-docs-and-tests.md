# Issue: code_check: clean up stale check_file_size mentions in docs and tests

## Description
Part of #279. Depends on #280, #281 and #282, which are all merged. This is the last check for places that still call `check_file_size` the current command, or that describe the alias as it was before #281 and #282.

The targets listed in the parent issue (`docs/agents/specs.md`, `.claude/agents/guide.md`, the `python/kube/parser.py` docstring and the fake `argv[0]` in `python/tests/common/test_arg_parser.py`) were already fixed in #280. The stale mentions below are the ones that are left.

## Problem
- `docs/agents/architecture.md` (around line 139) says the `python/check_file_size/` shim forwards to `code_check/file_size` "with unchanged behaviour and no deprecation warning". Since #281, the shim prints a deprecation warning on stderr.
- `python/tests/code_check/test_config.py` uses `"check_file_size"` as the example section name in the generic `load_section` tests. That section is now the legacy key, and the current name is `file_size`.
- `python/tests/code_check/test_executor.py`: `test_subcommands_maps_file_size_to_check_file_size` names the test after the old command. It is really checking the `CheckFileSize` class.

## Expected Behaviour
- The only remaining mentions of `check_file_size` refer to the deprecated alias (`python/check_file_size/`, its `commands/python.json` entry, its tests and guide), the legacy config key (`LEGACY_CONFIG_SECTION`, its tests and docs), or the migration notes in the guides.
- The `CheckFileSize` class name stays as it is. The #279 decisions keep it.

## Solution
- `product-owner` agent:
  - `docs/agents/architecture.md`: say that the shim prints a deprecation warning on stderr and keeps stdout and exit codes unchanged. Check the rest of that section, and the completion note around line 56, against #281 and #282.
  - Run the grep from Verification and fix anything else that is stale in `docs/agents/`, `AGENTS.md` and `README.md`.
- `python` agent:
  - `python/tests/code_check/test_config.py`: use `"file_size"` as the section name in the generic `load_section` tests.
  - `python/tests/code_check/test_executor.py`: rename the test to `test_subcommands_maps_file_size_to_executor` (or something similar).

## Verification
- `grep -rn check_file_size --exclude-dir=.git --exclude-dir=issues --exclude-dir=plans .` shows only alias, legacy-key and migration mentions.
- `cd python && ruff check . && pytest`.

## Benefits
The docs and tests stay consistent, so agents and contributors are pointed at the right place.
