# kube configure: bootstrap missing ~/.tingle/kube/config.json with default version key

## Context

`tingle kube configure context` (and, by extension, `configure namespace` and
`configure pod`) fails the very first time a user runs it, before
`~/.tingle/kube/config.json` exists.

When the config file is absent, `KubeConfig._read()`
(`python/kube/config.py`) falls back to pass-through mode and leaves
`self.raw = {}` — no `version` key is ever injected. `Constants.REQUIRED_KEYS`
(`python/kube/constants.py:31`) requires `version`, but
`Constants.DEFAULTS` has no default value for it, and nothing in
`python/kube/configure.py`'s upsert flows (`configure_context` /
`_configure_context_upsert`) stamps a `version` before calling
`config.save(draft)`.

As a result, `config.save()` validates the draft, finds `version` missing,
and refuses to write, printing:

```
kube configure: config missing required key(s): version — nothing saved.
```

This blocks every first-time user from creating any alias, since there is no
way to seed the config file without manually creating
`~/.tingle/kube/config.json` with `{"version": 1}` beforehand.

## What needs to be done

- Python (`python/kube/`):
  - When `~/.tingle/kube/config.json` does not exist yet, `tingle kube
    configure` (covering `configure context`, `configure namespace`, and
    `configure pod`) should bootstrap it before proceeding with the alias
    creation — equivalent to creating the `~/.tingle/kube/` directory and
    writing a default `{"version": 1}` config.json.
  - This bootstrap should happen transparently as part of the
    `configure_context` / `_configure_context_upsert` upsert flow (or
    wherever the config is first loaded/saved), rather than requiring the
    user to create the file manually.
  - Ensure `config.save(draft)` no longer rejects the first save due to a
    missing `version` key once the file has been bootstrapped.
- Tests (`python/tests/kube/test_configure.py`):
  - Add coverage for the "file doesn't exist yet" path end-to-end. All
    existing tests pre-seed `{"version": 1, ...}`, so none currently exercise
    first-run bootstrap behavior.
  - Verify that running `tingle kube configure context` (or the equivalent
    Python entry point) against a missing `~/.tingle/kube/config.json`
    creates the directory and file with the default `version` key and
    successfully saves the new alias.

## Acceptance criteria

- [ ] Running `tingle kube configure context` (or `configure
      namespace`/`configure pod`) when `~/.tingle/kube/config.json` does not
      exist creates `~/.tingle/kube/` and a `config.json` seeded with
      `{"version": 1}` instead of failing.
- [ ] The alias requested in that first run is saved successfully, with no
      "config missing required key(s): version" error.
- [ ] Subsequent runs continue to work as before against the now-existing
      config file (no regression to the pre-seeded-config test path).
- [ ] `python/tests/kube/test_configure.py` includes a test that exercises
      the missing-config-file bootstrap path end-to-end.
