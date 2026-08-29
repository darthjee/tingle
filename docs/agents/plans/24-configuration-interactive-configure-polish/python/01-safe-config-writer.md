# Safe config writer

Add write support to the config layer: expose the raw (pre-default) dict for editing, and a `save()` path that re-validates the merged structure before ever touching the file on disk, using the same schema rules `KubeConfig._validate` already enforces for reads.

Reuse `KubeConfig._validate`/`_validate_pods` rather than duplicating schema rules — extract them to accept an arbitrary dict (they already do) so a draft dict can be checked before writing, independent of what was loaded at startup.

Write via a temp-file-plus-atomic-rename (`os.replace`) so a crash or interrupted write never leaves `config.json` half-written.

Suggested shape:
- `KubeConfig.raw` — the dict as read from disk (before defaults are applied), `{}` when the file doesn't exist yet. Needed so `configure` edits and re-saves only what the user actually set.
- `KubeConfig.validate(draft: dict) -> str | None` — expose the existing validation as a reusable entry point (thin wrapper around `_validate`).
- `KubeConfig.save(draft: dict) -> str | None` — validate `draft`, and on success write it to `self._path` (creating parent directories if absent) via a temp file + `os.replace`; returns an error message on validation failure (and does not touch the file), `None` on success.

## Files to Change

- `python/kube/config.py` — add `raw`, `validate()`, `save()` as described above; keep existing `data`/`pass_through`/`notice` behavior for readers unchanged.
