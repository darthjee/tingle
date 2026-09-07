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
  - Add a `Constants.CURRENT_VERSION = 1` constant (`python/kube/constants.py`)
    as the single source of truth for the default/current config schema
    version, instead of hardcoding `1` at the bootstrap call site.
  - Fix the bootstrap at the source: `KubeConfig._read()` / `_fallback()`
    (`python/kube/config.py`) should initialize `self.raw = {"version":
    Constants.CURRENT_VERSION}` when the config file is simply absent
    (distinct from an existing-but-malformed/invalid file), instead of
    leaving `self.raw = {}`. This benefits every kube command that reads
    config, not just `configure` — `configure_context` /
    `_configure_context_upsert` then work unmodified against a `raw` that
    already satisfies `Constants.REQUIRED_KEYS`.
  - When this bootstrap creates `~/.tingle/kube/` and writes the new
    `config.json` for the first time, print a one-line notice, e.g.:
    `kube configure: created new config at ~/.tingle/kube/config.json`.
  - Ensure `config.save(draft)` no longer rejects the first save due to a
    missing `version` key once the file has been bootstrapped.
- Tests (`python/tests/kube/test_config.py` and `test_configure.py`):
  - Add coverage for the "file doesn't exist yet" path end-to-end in both
    `KubeConfig` directly and through the `configure context` command. All
    existing tests pre-seed `{"version": 1, ...}`, so none currently exercise
    first-run bootstrap behavior.
  - Verify that running `tingle kube configure context` (or the equivalent
    Python entry point) against a missing `~/.tingle/kube/config.json`
    creates the directory and file with `Constants.CURRENT_VERSION`, prints
    the creation notice, and successfully saves the new alias.

## Acceptance criteria

- [ ] `Constants.CURRENT_VERSION` exists and is used as the default `version`
      value wherever a fresh config is bootstrapped.
- [ ] `KubeConfig` bootstraps `~/.tingle/kube/config.json` (creating the
      `~/.tingle/kube/` directory too) with `{"version":
      Constants.CURRENT_VERSION}` whenever the file is absent, regardless of
      which kube command triggered the read.
- [ ] The bootstrap prints a one-line notice naming the created file path.
- [ ] Running `tingle kube configure context` (or `configure
      namespace`/`configure pod`) when `~/.tingle/kube/config.json` does not
      exist creates the file and successfully saves the requested alias, with
      no "config missing required key(s): version" error.
- [ ] Subsequent runs continue to work as before against the now-existing
      config file (no regression to the pre-seeded-config test path).
- [ ] `python/tests/kube/test_config.py` and `test_configure.py` include
      tests that exercise the missing-config-file bootstrap path end-to-end,
      including the printed notice.
