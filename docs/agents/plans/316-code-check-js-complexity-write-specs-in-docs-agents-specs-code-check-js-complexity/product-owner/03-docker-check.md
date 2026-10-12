# docker-check.md
Write `docs/agents/specs/code_check/js_complexity/docker-check.md`, the spec for #317. It covers:
- **What moves to `python/code_check/docker_check/`:**
  - the `docker_runner.py` functions (preflight, `ensure_image`/pull, `run`, `run_args`, `check_outcome`, `decode`, `write_stderr`);
  - `resolve_image`;
  - the `selection.py` functions (`Selection`, `unsendable_reason`, `build_selection`, `select_files`);
  - the executor scaffolding: config load and merge, `_resolve_target`, the header, display selection, the gate and exit codes.

  For each one, list its new parameters: image repository, extensions, an extra skip predicate, and the error class or prefix.
- **What stays in `rubycritic/`.**
- **Backward-compatibility invariants**, as stated in the issue:
  - byte-for-byte identical behaviour;
  - existing tests change only import paths;
  - no shared message wording that alters rubycritic's output;
  - the rubycritic image is untouched;
  - `file_size` is untouched, and new parameters default to today's behaviour.
- **The test layout:** `python/tests/code_check/docker_check/`.

Base every name on the real code in `python/code_check/rubycritic/`.

## Files to Change
- `docs/agents/specs/code_check/js_complexity/docker-check.md` — new.
