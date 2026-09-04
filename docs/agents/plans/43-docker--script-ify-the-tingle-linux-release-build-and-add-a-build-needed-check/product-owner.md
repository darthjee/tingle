# product-owner Plan: Docker: script-ify the tingle-linux release build and add a build-needed check

Main plan: [plan.md](plan.md)

## Shared contracts

- Documents the same `darthjee/tingle:<tag>` / `shell/linux/VERSION`
  convention `architect` and `shell` implement — see [plan.md](plan.md)'s
  `## Shared contracts`. Do not introduce a third description of the tag
  convention; reuse the exact wording settled there.

## Implementation Steps

### Step 1 — Reconcile docs/agents/tingle-linux-image.md

Currently states (lines 4-5):

> **Tag strategy**: plain semver tags (e.g. `1.0.0`), published manually by
> pushing a matching `v*` git tag (e.g. `v1.0.0`) — no `latest`/automatic
> builds.

This is the actual source of the "three disagreeing conventions" drift
identified in the issue (docker tag says `1.0.0`, no `v`, while the git
tag and CI both use `v1.0.0`). Update to state a single consistent
convention: the published Docker tag is exactly the `v`-prefixed git tag
(e.g. pushing git tag `v1.0.0` publishes `darthjee/tingle:v1.0.0` — same
string, not two different formats), and name `shell/linux/VERSION` as the
pin file backing whatever is currently published. Also mention
`scripts/release_image.sh` as the script (not raw CI YAML) that performs
the build-needed check, build, smoke test, and publish.

### Step 2 — Add scripts/ to docs/agents/folder-structure.md

This issue introduces a new top-level `scripts/` directory (per the issue,
owned by `architect` — root-level, cross-cutting concern). Add a row for
it to the table in `docs/agents/folder-structure.md`, e.g.:

| Directory / File | Description |
|-----------------|-------------|
| `scripts/` | CI/release tooling scripts (not user-facing commands — see `bin/` for those). Currently holds `scripts/release_image.sh`, the `tingle-linux` Docker image build/publish/description script invoked by `.circleci/config.yml`. |

Keep the existing rows and ordering; just insert this one (logically near
`bin/`, since both are "callable script" entries, but ordering is a minor
judgment call).

## Files to Change
- `docs/agents/tingle-linux-image.md` — reconcile the tag-strategy wording
  and mention `shell/linux/VERSION` and `scripts/release_image.sh`.
- `docs/agents/folder-structure.md` — add the `scripts/` row.

## Notes
- Also worth a quick check of `docs/agents/architecture.md`'s own
  `.circleci/` section (it already correctly says architect owns CI, no
  change needed there) — only flagging so this isn't independently
  "discovered" as a gap later.
