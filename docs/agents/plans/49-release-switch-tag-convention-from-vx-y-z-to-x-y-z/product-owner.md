# Product Owner Plan: Release: switch tag convention from vX.Y.Z to X.Y.Z

Main plan: [plan.md](plan.md)

## Shared contracts

- Describe the tag format exactly as architect lands it: plain semver `X.Y.Z`
  (optional pre-release suffix), no `v` prefix. The published Docker tag equals
  the git tag string.
- Add the "`v`-prefixed tag triggers no release" fact — this doc is one of the
  two agreed homes for it (the other is the CircleCI config comment). Keep the
  wording parallel to that comment.

## Implementation Steps

### Step 1 — Rewrite the v-prefix wording in tingle-linux-image.md

`docs/agents/tingle-linux-image.md` documents the `v`-prefix as the convention
in three spots:

- **Tag strategy bullet (lines ~4–5)**: "the published Docker tag is exactly the
  `v`-prefixed git tag — pushing git tag `v1.0.0` publishes
  `darthjee/tingle:v1.0.0`…". Rewrite to plain semver — "pushing git tag
  `1.0.0` publishes `darthjee/tingle:1.0.0`" — and append the shared-contract
  clause: "a `v`-prefixed tag triggers no release (silently ignored by the
  CircleCI tag filter)".
- **Version pin bullet (line ~12)**: "(e.g. `v1.0.0`)" → "(e.g. `1.0.0`)".
- **Release script bullet (line ~17)**: "since the previous `v*` tag" →
  "since the previous release tag" (or "`X.Y.Z` tag").

Keep everything else in the file unchanged.

## Files to Change

- `docs/agents/tingle-linux-image.md` — replace all three `v`-prefixed
  wordings/examples with plain `X.Y.Z`, and add the "a `v`-prefixed tag triggers
  no release" clause to the Tag strategy bullet.

## Notes

- No CI job covers `docs/` — no automated check.
- Wording must stay consistent with `DOCKERHUB_DESCRIPTION.md` (architect) and
  the CircleCI comment: same format, same "`v*` does nothing" fact.
