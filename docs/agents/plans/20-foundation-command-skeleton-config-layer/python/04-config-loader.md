# Implement the config loader with pass-through fallback

Implement the config-reading layer: load `~/.tingle/kube/config.json` (path from `constants.py`), parse it as JSON, and validate its shape against the schema from Step 3. Apply defaults for `aws_profile`, `pod_id_pattern`, and `shell` when absent. On a missing file, invalid JSON, or a structurally invalid config (wrong types, missing required nested fields like a pod's `prefix`), do not raise — return/flag "pass-through mode" instead, with a clear notice printed to the user (per the parent epic's Section 6: "config.json missing or invalid -> full pass-through mode, with a notice that the config was not found"). This loader is consumed by `executor.py` in Step 5; it does not itself dispatch any subcommand behavior.

## Files to Change
- `python/kube/config.py` — new. A `KubeConfig` class (or similar) with a `load()` (or `__init__`) that reads the file, validates it, applies defaults, and exposes either a valid, defaulted config object/dict or a "pass-through" state plus the notice message to print. Imports schema/defaults from `constants.py`.
