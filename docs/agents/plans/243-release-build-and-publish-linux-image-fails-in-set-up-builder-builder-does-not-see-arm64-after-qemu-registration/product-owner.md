# Product-owner Plan: release: build-and-publish-linux-image fails in "Set up builder" — builder does not see arm64 after QEMU registration

Main plan: [plan.md](plan.md)

## Shared contracts

Document the `setup-builder` steps exactly as written in [plan.md](plan.md#shared-contracts), matching what `shell` implements in `scripts/release_image.sh`. The builder is never "selected"; `build`/`publish` pass `--builder tingle-builder`.

## Implementation Steps

### Step 1 — Correct the `setup-builder` description
In `docs/agents/tingle-linux-image.md` (item 1 of the release-job list, lines 111-115), replace the current text. It says QEMU is registered first and the builder is then created and "selected". In the code, the builder is created and started first and never selected.

Describe the real steps briefly: create `tingle-builder` if it's missing and start it → if every platform in `$PLATFORMS` is listed, skip QEMU (Docker Desktop, re-runs) → otherwise register QEMU through the pinned `tonistiigi/binfmt` image → stop the builder so BuildKit checks platforms again → recreate it once as a fallback (the only path that loses the cache) → fail if a platform is still missing.

Also mention that the `test` workflow's `setup-builder` job runs this step on every PR on the same `ubuntu-2404` machine image, so failures show up before release. Keep the paragraph's existing wrapping and style.

## Files to Change
- `docs/agents/tingle-linux-image.md` — item 1 (`setup-builder`) of the release-job description, plus a mention of the new `test`-workflow job.

## Notes
- Only touch that item (and, if it reads better, one sentence near it about the new CI job). Don't document #244 or the 0.2.0 recovery here.
