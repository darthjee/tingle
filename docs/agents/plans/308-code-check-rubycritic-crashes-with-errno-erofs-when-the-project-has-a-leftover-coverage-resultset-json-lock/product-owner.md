# Product-owner Plan: code_check rubycritic: crashes with Errno::EROFS when the project has a leftover coverage/.resultset.json.lock

Main plan: [plan.md](plan.md)

## Shared contracts

- The image now ships `coverage_path_patch.rb` (preloaded via `RUBYOPT`) and runs RubyCritic with `--coverage-path /tmp/coverage`. The project's `coverage/` is ignored, coverage is always empty, and nothing is written under `/src`.
- New fixture files `fixture/coverage/.resultset.json` and `fixture/coverage/.resultset.json.lock` (empty). New smoke assertion: no `analysed_modules`/`parse_errors` path starts with `coverage/`.

## Implementation Steps

### Step 1 — Update the rubycritic image doc

In `docs/agents/tingle-rubycritic-image.md`:
- In the image layout and file table, add `coverage_path_patch.rb` and explain why it exists: RubyCritic 5.0.0 drops `--coverage-path` from `Argv#to_h`, and a leftover `coverage/.resultset.json.lock` makes it crash with `Errno::EROFS` on the read-only `/src`.
- In the contract/entrypoint section, add `--coverage-path /tmp/coverage` and the `RUBYOPT` preload to the rubycritic command description.
- In "Smoke test", add the `coverage/` fixture files to the fixture table (around lines 384-391) and the new assertion to the "It asserts that:" list (around lines 393-406).

## Files to Change

- `docs/agents/tingle-rubycritic-image.md` — contract, file table and smoke-test docs.

## Notes

- Doc-only. Keep the wording consistent with what shell actually implements, and check its final diff.
