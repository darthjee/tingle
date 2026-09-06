# Architect Plan: Release: switch tag convention from vX.Y.Z to X.Y.Z

Main plan: [plan.md](plan.md)

## Shared contracts

- Accepted tag format: plain semver `X.Y.Z` + optional pre-release suffix; no
  `v` prefix, no `+build` metadata.
- CircleCI filter regex (this agent lands it):
  `/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/` — anchored, left unquoted in
  YAML, pre-release class `[0-9A-Za-z.]` (no `-`).
- `shell/linux/VERSION` content: `0.0.1`.
- The "`v*` does nothing" note goes in the CircleCI config as a one-line comment
  above the filter; product-owner adds the parallel clause in
  `tingle-linux-image.md`. It does **not** go in `DOCKERHUB_DESCRIPTION.md`.

## Implementation Steps

### Step 1 — Behavioral change: tag filters + VERSION pin

`.circleci/config.yml` — the `release` workflow has two jobs
(`build-and-publish-linux-image` at ~line 14, `update-description` at ~line 22),
each with `filters: tags: only: /v.*/`. Replace **both** occurrences with:

```yaml
tags:
  # plain semver only — a v-prefixed tag (v1.9.0) is silently ignored
  only: /^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/
```

Keep the sibling `branches: ignore: /.*/` lines unchanged. Leave the regex
unquoted (an unquoted YAML scalar keeps `\.` literal; quoting breaks it). Adding
the comment above both filters is fine; once is enough if preferred.

`shell/linux/VERSION` — single line, change `v0.0.1` to `0.0.1` (keep the
trailing newline). No change to `shell/linux/docker_run.sh`: it already does
`darthjee/tingle:$(cat "$(dirname "${BASH_SOURCE[0]}")/VERSION")` and will
resolve `darthjee/tingle:0.0.1` on its own.

### Step 2 — Wording-only updates (no behavior change)

`scripts/release_image.sh` — the header comment at ~line 17 reads
"…hasn't changed since the previous v* tag…". Change `v*` to `X.Y.Z` (or
"the previous release tag"). Do **not** touch `resolve_tag`, `previous_tag`
(`git tag --sort=-creatordate` is format-agnostic), or `verify_version_pin`
(a plain string compare) — no code change anywhere in this file.

`DOCKERHUB_DESCRIPTION.md` — line ~15: "Tags are `v`-prefixed semver
(e.g. `v1.0.0`), published manually on `v*` git tag pushes…". Rewrite to plain
semver, e.g. "Tags are plain semver (e.g. `1.0.0`), published manually on
`X.Y.Z` git tag pushes…". Do **not** add the "`v*` does nothing" note here.

## Files to Change

- `.circleci/config.yml` — both `only: /v.*/` → the plain-semver regex, plus a
  one-line explanatory comment above the filter(s).
- `shell/linux/VERSION` — `v0.0.1` → `0.0.1`.
- `scripts/release_image.sh` — comment wording `v*` → `X.Y.Z` (line ~17); no
  code change.
- `DOCKERHUB_DESCRIPTION.md` — `v`-prefixed wording/example → plain `X.Y.Z`
  (line ~15).

## CI Checks

- None gate these files on a PR (`lint`/`tests` are `python/`-only; the
  `release` workflow is tag-triggered). Manual post-merge check: push a
  throwaway `0.0.0-rc1` tag and confirm the `release` workflow starts; a
  `v0.0.0-rc1` tag must not.
- If `circleci` CLI is available, run `circleci config validate` after the edit
  to confirm the unquoted regex still parses.

## Notes

- The regex is copied verbatim by #46 / #47 — do not "simplify" the anchors
  away.
- `shell/linux/VERSION` is a data file, not a script; it is assigned to
  `architect` (not `shell`) because its content is coupled to the CI regex and
  `verify_version_pin`, so it changes atomically with the rest of the flip.
