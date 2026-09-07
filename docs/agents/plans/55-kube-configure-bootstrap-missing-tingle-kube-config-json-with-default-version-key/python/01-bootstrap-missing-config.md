# Add CURRENT_VERSION and bootstrap the missing-file case

Introduce a single source of truth for the default config schema version, and make `KubeConfig` create a valid config file (instead of falling back to pass-through) whenever `~/.tingle/kube/config.json` simply does not exist yet.

In `constants.py`, add `CURRENT_VERSION: ClassVar[int] = 1` alongside the other class-level constants (near `CONFIG_PATH`). This is the value written into a freshly bootstrapped config, and the one place a future schema bump would change.

In `config.py`'s `_read()`, replace the `if not self._path.exists(): self._fallback(...); return None` branch with a new `_bootstrap()` method that:
- Builds `raw = {"version": Constants.CURRENT_VERSION}`.
- Creates `self._path.parent` (`mkdir(parents=True, exist_ok=True)`) and writes `raw` to `self._path` as JSON — reuse the same atomic temp-file-plus-`os.replace` pattern already used in `save()` (factor it into a small shared helper, e.g. `_write(draft)`, called by both `_bootstrap()` and `save()`, rather than duplicating the temp-file dance).
- Sets `self.notice = f"kube: created new config at {self._path}"` (do **not** set `self.pass_through = True` — a bootstrapped config is valid, not a pass-through fallback).
- Returns `raw` so `_load()` continues into its normal `_validate`/`_apply_defaults` path (which will pass, since `version` is now present).

Leave every other `_read()` failure branch (`OSError` on read, invalid JSON, non-dict payload) exactly as-is — those still call `self._fallback(...)` and return `None`, keeping pass-through mode for genuinely broken files. `_validate()`'s existing structural checks (missing keys, wrong-typed object keys, malformed `pods` entries) are untouched; a bootstrapped `raw` always satisfies them.

## Files to Change

- `python/kube/constants.py` — add `CURRENT_VERSION: ClassVar[int] = 1`.
- `python/kube/config.py` — add `_bootstrap()` (and a shared `_write()` helper factored out of `save()`'s temp-file logic) invoked from `_read()` when the path does not exist; keep the other fallback branches unchanged.
