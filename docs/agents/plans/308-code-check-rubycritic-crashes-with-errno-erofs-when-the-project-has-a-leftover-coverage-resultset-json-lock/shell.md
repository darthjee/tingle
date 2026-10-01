# Shell Plan: code_check rubycritic: crashes with Errno::EROFS when the project has a leftover coverage/.resultset.json.lock

Main plan: [plan.md](plan.md)

## Shared contracts

- Ship `docker/rubycritic/coverage_path_patch.rb` in the image (a `COPY` in `docker/rubycritic/Dockerfile`, next to `entrypoint.rb`).
- `run_rubycritic` passes `--coverage-path /tmp/coverage` and runs with `RUBYOPT` including `-r<patch path>`.
- Fixture `docker/rubycritic/fixture/coverage/{.resultset.json,.resultset.json.lock}`, plus the new "no `coverage/` paths" smoke assertion. product-owner documents both in `docs/agents/tingle-rubycritic-image.md`.

## Implementation Steps

### Step 1 — Make the image ignore the project's coverage/

- Add `docker/rubycritic/coverage_path_patch.rb` with a short header comment. It explains that RubyCritic 5.0.0 parses `--coverage-path` but drops it in `Cli::Options::Argv#to_h`, so without the patch `analysers/coverage.rb` falls back to `/src/coverage` and locks `.resultset.json.lock` with `w+`, which fails on a read-only mount. Body (tested during exploration):
  ```ruby
  require "rubycritic/cli/options/argv"
  RubyCritic::Cli::Options::Argv.prepend(Module.new do
    def to_h = super.merge(coverage_path: @coverage_path)
  end)
  ```
  Only merge the key when `@coverage_path` is set, so the patch has no effect when the flag isn't passed.
- `docker/rubycritic/Dockerfile`: `COPY` the patch next to `entrypoint.rb`.
- `docker/rubycritic/entrypoint.rb`:
  - Add constants `COVERAGE_PATH = "/tmp/coverage"` and the patch path, resolved from the entrypoint's own directory.
  - Add `"--coverage-path", COVERAGE_PATH` to the command.
  - Call `system({"RUBYOPT" => [ENV["RUBYOPT"], "-r#{PATCH}"].compact.join(" ")}, *command, out: $stderr, err: $stderr)`.
  - Update the header contract comment to say the project's `coverage/` is ignored.
- `docker/rubycritic/DOCKERHUB_DESCRIPTION.md`: next to the "read-only `/src` ... only writes under `/tmp`" sentence, note that the project's `coverage/` (SimpleCov data) is ignored and coverage is not reported.

### Step 2 — Regression fixture and smoke-test assertions

- Add `docker/rubycritic/fixture/coverage/.resultset.json`: a small, valid SimpleCov resultset, for example `{"RSpec": {"coverage": {"/src/simple.rb": {"lines": [1, null, 1]}}, "timestamp": 1700000000}}`.
- Add an empty `docker/rubycritic/fixture/coverage/.resultset.json.lock`. Confirm `git add` picks up both dotfiles (they are not ignored).
- `scripts/release_image.sh` `smoke_test_rubycritic`: in the inline python assertion block, assert that no path in `analysed_modules` or `parse_errors` starts with `coverage/`. The existing run, mounted `:ro` with `-w /src`, now reproduces the crash before the fix (the run exits non-zero) and passes after it.

## Files to Change

- `docker/rubycritic/coverage_path_patch.rb` — new preload patch forwarding `--coverage-path`.
- `docker/rubycritic/Dockerfile` — `COPY` the patch.
- `docker/rubycritic/entrypoint.rb` — `--coverage-path /tmp/coverage` + `RUBYOPT` preload, plus the header comment.
- `docker/rubycritic/DOCKERHUB_DESCRIPTION.md` — note that the project's `coverage/` is ignored.
- `docker/rubycritic/fixture/coverage/.resultset.json`, `docker/rubycritic/fixture/coverage/.resultset.json.lock` — regression fixture.
- `scripts/release_image.sh` — the new assertion.

## CI Checks

- The image is only built and smoke-tested in the tag-only `release` workflow (`build-and-publish-rubycritic-image`), so verify locally:
  - `make rubycritic-image`
  - `docker tag tingle_rubycritic:dev darthjee/tingle_rubycritic:0.6.0-arm64`
  - `PLATFORMS=linux/arm64 scripts/release_image.sh smoke-test rubycritic`
  - Also confirm the smoke test fails against the old image or entrypoint, so it is a real regression test.
- `shellcheck scripts/release_image.sh`.
- Branch CI (`lint`, `tests` in `python/`) is unaffected. Run `pytest` and `ruff check .` in `python/` as a sanity check.

## Notes

- This differs from the issue's proposed Solution (the flag alone). The flag alone is a no-op in RubyCritic 5.0.0, which was verified in the `tingle_rubycritic:dev` image.
- Alternative (also tested): preload `require "simplecov"; SimpleCov.coverage_dir("/tmp/coverage")` with no CLI flag. The patch is preferred because it keeps the CLI flag meaningful and is easy to drop when RubyCritic fixes `Argv#to_h` upstream.
- Out of scope, worth a follow-up issue: because the working directory is `/src`, RubyCritic also reads the project's own `./.rubycritic.yml`, which can change the run.
