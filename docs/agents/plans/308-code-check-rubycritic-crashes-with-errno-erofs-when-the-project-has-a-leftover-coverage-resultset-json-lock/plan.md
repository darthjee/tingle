# Plan: code_check rubycritic: crashes with Errno::EROFS when the project has a leftover coverage/.resultset.json.lock

Issue: [308-code-check-rubycritic-crashes-with-errno-erofs-when-the-project-has-a-leftover-coverage-resultset-json-lock.md](../../issues/308-code-check-rubycritic-crashes-with-errno-erofs-when-the-project-has-a-leftover-coverage-resultset-json-lock.md)

## Overview

Make the `tingle_rubycritic` image ignore the analysed project's `coverage/` folder so RubyCritic never opens `/src/coverage/.resultset.json.lock` on the read-only mount. Exploration showed that RubyCritic 5.0.0 parses `--coverage-path` but drops it (`Cli::Options::Argv#to_h` has no `coverage_path:` key), so the flag alone, as the issue proposed, does nothing. The image therefore ships a small preload patch that forwards `--coverage-path` into RubyCritic's config, loaded via `RUBYOPT`, and the entrypoint passes `--coverage-path /tmp/coverage`. A fixture with a leftover lock file in the smoke test guards against regressions.

## Agents involved

- [shell](shell.md)
- [product-owner](product-owner.md)

## Shared contracts

- New image file: `docker/rubycritic/coverage_path_patch.rb`, copied in the Dockerfile next to `entrypoint.rb`, to the same directory as the entrypoint.
- The entrypoint runs `bundle exec rubycritic --format json --no-browser -p /tmp/out --coverage-path /tmp/coverage <paths>` with `RUBYOPT` containing `-r<absolute path of coverage_path_patch.rb>` (added to any existing `RUBYOPT`).
- `/tmp/coverage` is never created. Coverage in the report is always empty. Nothing is written under `/src`.
- New fixture: `docker/rubycritic/fixture/coverage/.resultset.json` (a small, valid SimpleCov resultset) and `docker/rubycritic/fixture/coverage/.resultset.json.lock` (empty).
- New smoke-test assertion: no `analysed_modules` or `parse_errors` path starts with `coverage/`. The run still exits 0 and the existing assertions still pass.
