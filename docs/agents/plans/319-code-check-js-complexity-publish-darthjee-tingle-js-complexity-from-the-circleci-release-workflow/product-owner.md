# Product-owner Plan: code_check js_complexity: publish darthjee/tingle_js_complexity from the CircleCI release workflow

Main plan: [plan.md](plan.md)

## Shared contracts

- Document the `js_complexity` selector, settings, CircleCI job names and smoke-test checks exactly as listed in [plan.md](plan.md#shared-contracts), and as shell implements them in `scripts/release_image.sh` and `.circleci/config.yml`.

## Implementation Steps

### Step 1 — Write docs/agents/tingle-js-complexity-image.md
Write the doc in the style of `docs/agents/tingle-rubycritic-image.md`, with the sections from release.md §6:
1. Header bullets: image name; tag strategy (same semver as tingle, every tag published, no `latest`, `v` tags ignored, one amd64/arm64 manifest); source (`docker/js_complexity/`, build context, FTA/npm/final stages); pins (base digest, Rust stage, `package-lock.json`, versions table).
2. Contract: canonical run line, stdin, refused lines, staged tree, merged JSON on stdout, stderr and exit status.
3. Runtime user and hardening.
4. Release pipeline: selector, steps, smoke-test checks, CircleCI jobs and dependencies, the "no change detection" rule.
5. Docker Hub description.
6. Local build: `make js-complexity-image` and `--image tingle_js_complexity:dev`.
7. Bumping versions (from image.md §13).

Take the facts from `docs/agents/specs/code_check/js_complexity/image.md`, `release.md` and the actual `docker/js_complexity/` files. Do not invent details.

### Step 2 — Update the cross-references
- `docs/agents/tingle-linux-image.md` and `docs/agents/tingle-rubycritic-image.md`: add a one-line pointer to the new doc. Extend the "a git tag `X.Y.Z` triggers the image jobs" note to list the js_complexity jobs, and note that the CLI release requires all three image jobs.
- `docs/agents/folder-structure.md`: in the `scripts/` row, mention the `js_complexity` selector (`darthjee/tingle_js_complexity`). In the `docker/` row, point `docker/js_complexity/` at `tingle-js-complexity-image.md` instead of the spec.

## Files to Change
- `docs/agents/tingle-js-complexity-image.md` — new.
- `docs/agents/tingle-linux-image.md` — pointer and release note.
- `docs/agents/tingle-rubycritic-image.md` — pointer and release note.
- `docs/agents/folder-structure.md` — `scripts/` and `docker/` rows.

## Notes
- Do not remove `docs/agents/specs/code_check/js_complexity/`; that is #327.
