## Description
Sub-issue of #45 (`Add tingle web install (curl | bash)`), sequenced **first** —
before #46 (release zip) and #47 (bootstrap/installer), both of which build on
whatever the release tag format is.

The repo's release/CI tooling currently expects **`v`-prefixed** tags
(`v1.9.0`). The maintainer's actual release convention across projects is
**plain semver** (`1.9.0`); the `v`-prefix was introduced during #43/#44 when
three conflicting tag conventions were reconciled — onto the wrong one. This
issue flips tingle to plain `X.Y.Z`.

## Problem
- `.circleci/config.yml`'s `release` workflow gates both jobs on
  `filters: tags: only: /v.*/` — a `1.9.0` tag push would not trigger a release
  at all.
- `shell/linux/VERSION` holds `v0.0.1`; `scripts/release_image.sh`'s
  `verify_version_pin` hard-fails CI unless it matches `$CIRCLE_TAG` exactly, so
  the pin file and the pushed tag must use the same format.
- `docs/agents/tingle-linux-image.md` and `DOCKERHUB_DESCRIPTION.md` both
  document the `v`-prefix as the convention.
- No git tags and no published Docker image exist yet, so there is **no
  migration cost** — this is the last cheap moment to change it.

## Expected Behavior
- Pushing a plain semver tag (`1.9.0`, optionally `1.9.0-rc1`) triggers the
  `release` workflow; a `v`-prefixed tag does **not**.
- `shell/linux/VERSION` contains `0.0.1` (no `v`).
- `shell/linux/docker_run.sh` resolves the image ref as `darthjee/tingle:0.0.1`
  — it already just reads `VERSION`, so only the file content changes.
- `scripts/release_image.sh` behaviour is unchanged; only its header/comment
  references to `v*` / `v`-prefixed tags are updated to `X.Y.Z`.
- `docs/agents/tingle-linux-image.md` and `DOCKERHUB_DESCRIPTION.md` describe the
  plain-semver convention consistently.
- Manual verification: push a throwaway `0.0.0-rc1` tag on a branch/fork,
  confirm the `release` workflow starts; confirm a `v0.0.0-rc1` tag does not.

### Edge cases
- **CircleCI tag regex** — `filters.tags.only` is a Java regex, matched against
  the whole tag string (`Pattern.matches()` semantics — full match, not a
  search). Final: `/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/` (semver core
  plus an optional pre-release suffix). The suffix is wanted: it is used by the
  throwaway `0.0.0-rcN` test tags in #46/#47 and by #46's `prerelease` rule.
  Precision decisions:
  - **`^…$` kept though redundant** — CircleCI already full-matches; the
    explicit anchors keep the pattern self-documenting where #46/#47 copy it
    verbatim into their own filters.
  - **Left unquoted in YAML**, matching the current `only: /v.*/`. An unquoted
    scalar treats `\.` literally; double-quoting would make `\.` a YAML escape
    error.
  - **Build metadata (`+…`) rejected on purpose**, not an oversight: Docker
    tags cannot contain `+` (`docker build -t tingle:1.9.0+x` fails), so a `+`
    tag must never trigger the workflow.
  - **Pre-release class is `[0-9A-Za-z.]` — no `-`**, deliberately kept tight.
    Real usage is only `-rcN` / `-rc.N`; `1.9.0-x-y` failing is acceptable.
  - **No script-side format validation** — `release_image.sh` only
    string-compares `shell/linux/VERSION` to `$CIRCLE_TAG`; the CI filter is
    the sole format gate (a malformed tag never triggers the workflow; a
    `VERSION`/tag mismatch hard-fails `verify_version_pin`). A planner should
    **not** add a redundant regex check to the script.
- **`previous_tag()` in `release_image.sh`** — `git tag --sort=-creatordate` is
  format-agnostic; no change.
- **Any other `v0.`/`v1.` literal introduced by #43/#44** — the sweep surface
  is fully enumerated below (`### Sweep — complete hit list`); it is 4 files /
  8 lines, nothing hidden in `README.md`, `Makefile`, `completions/`, `bin/`,
  or language dirs.
- **Someone later pushes a `v*` tag out of habit** — it silently does nothing
  (no workflow triggered). Acceptable; documented in two spots (see
  `### "v*" does nothing` note below), **not** in `DOCKERHUB_DESCRIPTION.md`
  (its audience pulls the image, never pushes release tags).

## Solution
- `.circleci/config.yml` — change both `only: /v.*/` filters to the plain-semver
  regex above (#46's new job then uses the same pattern).
- `shell/linux/VERSION` — `v0.0.1` -> `0.0.1`.
- `scripts/release_image.sh` — update header/comment references to `v*` /
  `v`-prefixed; no code change (string compare + `git tag` sort are
  format-agnostic).
- `docs/agents/tingle-linux-image.md`, `DOCKERHUB_DESCRIPTION.md` — replace the
  `v`-prefixed wording/examples with plain `X.Y.Z`.
- No open-ended tree sweep needed — the complete hit list is fixed (below).

### Sweep — complete hit list

Exactly 4 files, 8 lines (issue/plan files excluded):

| File:line | Current | Change |
| --- | --- | --- |
| `.circleci/config.yml:14` | `only: /v.*/` | plain-semver regex |
| `.circleci/config.yml:22` | `only: /v.*/` | plain-semver regex + `# plain semver only …` comment above the filter |
| `shell/linux/VERSION:1` | `v0.0.1` | `0.0.1` |
| `scripts/release_image.sh:17` | `# … since the previous v* tag` | `X.Y.Z` wording (comment only; header lines 12-14 and `previous_tag()` at :36 carry no `v` literal — untouched) |
| `DOCKERHUB_DESCRIPTION.md:15` | ``Tags are `v`-prefixed semver (e.g. `v1.0.0`) … on `v*` `` | plain `X.Y.Z` wording; **no** `v*`-does-nothing note here |
| `docs/agents/tingle-linux-image.md:4-5` | ``Tag strategy: `v`-prefixed … publishes `darthjee/tingle:v1.0.0` `` | plain `X.Y.Z` + the "a `v`-prefixed tag triggers no release" clause |
| `docs/agents/tingle-linux-image.md:12` | ``(e.g. `v1.0.0`)`` | `1.0.0` |
| `docs/agents/tingle-linux-image.md:17` | ``since the previous `v*` tag`` | `X.Y.Z` wording |

Confirmed with no hits: `README.md`, `AGENTS.md` (only an unrelated
`issues/5_release_docker_image.md` path example), `docs/agents/folder-structure.md`,
`Makefile`, `completions/`, `bin/`, `node/`, `python/`; no `docs/agents/plans/`
dir and no CHANGELOG yet.

**Verification gate** — after the change,
`grep -rnI -E 'v[0-9]+\.[0-9]+|/v\.\*/|v-prefix' . --exclude-dir=.git` must
return only intentional matches: the CI comment's `(v1.9.0)` example, the
`tingle-linux-image.md` "triggers no release" clause, and the issue/plan files.

### "v*" does nothing — note placement

The "a `v`-prefixed tag triggers no release" fact is recorded in exactly two
places, chosen to land in front of whoever might push such a tag:

- **`.circleci/config.yml`** — a one-line comment directly above the filter
  regex, so anyone debugging "why didn't my release trigger?" sees it first,
  e.g.:

  ```yaml
  tags:
    # plain semver only — a v-prefixed tag (v1.9.0) is silently ignored
    only: /^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/
  ```

- **`docs/agents/tingle-linux-image.md`** — one clause folded into the existing
  *Tag strategy* bullet, e.g. "…pushing git tag `1.0.0` publishes
  `darthjee/tingle:1.0.0`; a `v`-prefixed tag triggers no release (silently
  ignored by the CircleCI tag filter)."

Deliberately **not** in `DOCKERHUB_DESCRIPTION.md`: its readers pull the image
and never push release tags, so tag-filter mechanics are noise there — that
file only gets the `v` → plain `X.Y.Z` wording rewrite.

### Scope
- `.circleci/config.yml`, `shell/linux/VERSION`, `scripts/release_image.sh`
  (comments only), `docs/agents/tingle-linux-image.md`,
  `DOCKERHUB_DESCRIPTION.md`.

### Out of scope
- The release-zip job / `scripts/release_cli.sh` — #46 (it adopts the regex this
  issue lands).
- The bootstrap / installer — #47.
- Introducing a shared `tingle.version` file — still a deferred follow-up.
- Actually cutting the first real release tag — a manual operational step.

### Dependencies
- None. **Blocks #46 and #47**, which both assume the settled tag format.

### Responsible agent(s)
- `architect` — `.circleci/config.yml`, `shell/linux/VERSION` (a data file, not
  a script; its content is coupled to the CI regex and `verify_version_pin`, so
  it stays with the rest of the release-format flip), root `scripts/` comments,
  root file `DOCKERHUB_DESCRIPTION.md`.
- `product-owner` — `docs/agents/tingle-linux-image.md`.

## Benefits
- Aligns tingle with the maintainer's actual release convention before any tag
  is ever cut, so the first release is `1.0.0`, not `v1.0.0`.
- #46 / #47 consume `X.Y.Z` directly with no later churn.
- Removes the last remnant of the pre-#43 tag-convention confusion.
