# Shell Plan: code_check rubycritic: per-method complexity drill-down (--details)

Main plan: [plan.md](plan.md)

## Shared contracts

The image must produce the `methods` key exactly as described in
[plan.md → Image stdout](plan.md#image-stdout-new-top-level-methods-key).
Python relies on `path` matching the stdin line, `line` being an int and
`score` being a number with 2 decimals.

## Implementation Steps

### Step 1 — Add per-method Flog scores to the entrypoint
In `docker/rubycritic/entrypoint.rb`, after `run_rubycritic(survivors)` and `read_report`, score the surviving paths with the Flog API. Flog 4.9.4 is already in the locked bundle as a RubyCritic dependency, so the Gemfile doesn't change.

- `require "flog"`, then build `Flog.new(all: true, methods: true, quiet: true)` and call `flog.flog(*survivors)`. Read the scores (`totals` or `each_by_score`) and their locations (`method_locations`, values like `"complex.rb:2-14"`). Check the exact API against the installed gem (`bundle exec gem contents flog`). Flog must not print to stdout; output already goes to stderr through `$stdout = $stderr`.
- Skip names ending in `#none`. Split the location into `path` and the first line number.
- Round scores to 2 decimals and sort them (score descending, path, name). Set `report["methods"]`.
- In the no-survivors branch, emit `"methods" => []`.
- If Flog itself raises, let the existing top-level rescue fail the run (exit 1), as for any other entrypoint failure.
- Update the header comment (Output section).

### Step 2 — Smoke test and image contract doc
- `scripts/release_image.sh` `smoke_test_rubycritic`:
  - Fixture run: `methods` is a list. It holds an entry `{"path": "complex.rb", "name": "Complex#run"}` with `score` > 50 and an int `line`. No entry has a `path` of `broken.rb`, `empty.rb` or `constants_only.rb`, and no `name` ends in `#none`.
  - Empty-stdin run: the expected object gains `"methods": []`.
- `docs/agents/tingle-rubycritic-image.md` "Contract" section: document the `methods` key, its fields and order, the empty-list case and how Flog is invoked.

## Files to Change
- `docker/rubycritic/entrypoint.rb`: run Flog, emit `methods`.
- `scripts/release_image.sh`: smoke-test checks for `methods`.
- `docs/agents/tingle-rubycritic-image.md`: contract update.

## CI Checks
- Image smoke test (local build): `scripts/release_image.sh build rubycritic && scripts/release_image.sh smoke-test rubycritic`. In CI it runs only on release tags (`build-and-publish-rubycritic-image`), so run it locally before opening the PR.

## Notes
- Flog keys methods by `Class#method`, so the same method name in a class reopened in two files gets merged into one entry, with only one location. This is acceptable: the entry is attributed to the file Flog reports.
- Release rule from #290 still applies: the image tag is the tingle version, so the image with `methods` ships together with the CLI that reads it.
