# Define the config schema and defaults

Define the `~/.tingle/kube/config.json` schema and its default values as plain constants, following the `check_file_size/constants.py` precedent (a `Constants` class holding class-level defaults). This is data/constants only — no file I/O here, that's Step 4.

Schema fields (per the parent epic, issue #19's Section 4): `version`, `aws_profile` (default `"default"`), `pod_id_pattern` (default `"^[a-z0-9]{10}$"`), `shell` (default `"bash"`), `contexts` (object, alias → real context name), `namespaces` (object, keyed by context alias), `pods` (object, keyed by context alias, each pod entry has `prefix` required, `id_pattern` and `namespace` optional).

## Files to Change
- `python/kube/constants.py` — new. A `Constants` class (or module-level constants) with `DEFAULT_AWS_PROFILE = "default"`, `DEFAULT_POD_ID_PATTERN = r"^[a-z0-9]{10}$"`, `DEFAULT_SHELL = "bash"`, plus the config file's path (`Path.home() / ".tingle" / "kube" / "config.json"`) and the set of required/optional top-level schema keys, in a shape `config.py` (Step 4) can import and use for validation.
