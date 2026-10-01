# Issue: code_check rubycritic: crashes with Errno::EROFS when the project has a leftover coverage/.resultset.json.lock

## Description

`tingle code_check rubycritic source` aborts inside the RubyCritic container with:

```
Read-only file system @ rb_sysopen - /src/coverage/.resultset.json.lock (Errno::EROFS)
```

### Steps to reproduce

1. In a Ruby project that has a SimpleCov `coverage/.resultset.json` (e.g. after running the specs), run:
   ```
   tingle code_check rubycritic source
   ```

### Actual

RubyCritic crashes and no report is produced.

<details>
<summary>Full backtrace</summary>

```
bundler: failed to load command: rubycritic (/usr/local/bundle/bin/rubycritic)
/usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers/coverage.rb:102:in `initialize': Read-only file system @ rb_sysopen - /src/coverage/.resultset.json.lock (Errno::EROFS)
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers/coverage.rb:102:in `open'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers/coverage.rb:102:in `with_lock'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers/coverage.rb:97:in `synchronize_resultset'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers/coverage.rb:78:in `stored_data'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers/coverage.rb:64:in `resultset'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers/coverage.rb:116:in `results'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers/coverage.rb:16:in `initialize'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers_runner.rb:30:in `new'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers_runner.rb:30:in `block in run'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers_runner.rb:29:in `each'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/analysers_runner.rb:29:in `run'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/commands/default.rb:24:in `critique'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/commands/default.rb:19:in `execute'
        from /usr/local/bundle/gems/rubycritic-5.0.0/lib/rubycritic/cli/application.rb:21:in `execute'
        from /usr/local/bundle/gems/rubycritic-5.0.0/bin/rubycritic:10:in `<top (required)>'
        from /usr/local/bundle/bin/rubycritic:25:in `load'
        from /usr/local/bundle/bin/rubycritic:25:in `<top (required)>'
        from /usr/local/lib/ruby/3.3.0/bundler/cli/exec.rb:58:in `load'
        from /usr/local/lib/ruby/3.3.0/bundler/cli/exec.rb:58:in `kernel_load'
        from /usr/local/lib/ruby/3.3.0/bundler/cli/exec.rb:23:in `run'
        from /usr/local/lib/ruby/3.3.0/bundler/cli.rb:455:in `exec'
        from /usr/local/lib/ruby/3.3.0/bundler/vendor/thor/lib/thor/command.rb:28:in `run'
        from /usr/local/lib/ruby/3.3.0/bundler/vendor/thor/lib/thor/invocation.rb:127:in `invoke_command'
        from /usr/local/lib/ruby/3.3.0/bundler/vendor/thor/lib/thor.rb:527:in `dispatch'
        from /usr/local/lib/ruby/3.3.0/bundler/cli.rb:35:in `dispatch'
        from /usr/local/lib/ruby/3.3.0/bundler/vendor/thor/lib/thor/base.rb:584:in `start'
        from /usr/local/lib/ruby/3.3.0/bundler/cli.rb:29:in `start'
        from /usr/local/lib/ruby/gems/3.3.0/gems/bundler-2.5.22/exe/bundle:28:in `block in <top (required)>'
        from /usr/local/lib/ruby/3.3.0/bundler/friendly_errors.rb:117:in `with_friendly_errors'
        from /usr/local/lib/ruby/gems/3.3.0/gems/bundler-2.5.22/exe/bundle:20:in `<top (required)>'
        from /usr/local/bin/bundle:25:in `load'
        from /usr/local/bin/bundle:25:in `<main>'
```

</details>

## Problem

`DockerRunner.run_args` (`python/code_check/rubycritic/docker_runner.py`) mounts the project read-only (`-v {root}:/src:ro`), and the image contract (`docker/rubycritic/DOCKERHUB_DESCRIPTION.md`) promises it "works with a read-only `/src`" and "only writes under `/tmp`".

RubyCritic 5.0's coverage analyser always reads SimpleCov results from `--coverage-path` (default `./coverage`, i.e. `/src/coverage`). In `analysers/coverage.rb`, `synchronize_resultset` takes a lock **only when `coverage/.resultset.json.lock` already exists**; `with_lock` then opens that file with `File.open(..., 'w+')`, which fails on the read-only mount with `Errno::EROFS`.

So the crash happens when the analysed project has a leftover SimpleCov lock file (`coverage/.resultset.json.lock`), not merely a resultset. The entrypoint (`docker/rubycritic/entrypoint.rb`, `run_rubycritic`) never passes `--coverage-path`, so RubyCritic always looks at the project's `coverage/`.

tingle does not use RubyCritic's coverage data anywhere (`python/code_check/rubycritic/` never reads it).

## Expected Behavior

`tingle code_check rubycritic` produces its report whether or not the project has a `coverage/` folder (with or without a leftover `.resultset.json.lock`). The project's `coverage/` is ignored, and nothing is written under `/src`.

## Solution

Fix it inside the image: in `docker/rubycritic/entrypoint.rb` (`run_rubycritic`), pass `--coverage-path` pointing at a path under `/tmp` that holds no SimpleCov data (e.g. `/tmp/coverage`, not created). RubyCritic then never reads or locks anything under `/src/coverage`, so the read-only mount and the image contract ("only writes under `/tmp`") stay intact.

- Coverage in the report is always empty. That is fine: tingle never reads RubyCritic's coverage data.
- No change to `DockerRunner` or the `:ro` mount.

### Alternatives considered (rejected)

- **Copy the project's resultset into `/tmp/coverage`** — keeps coverage data, but adds code for data tingle doesn't show.
- **`--tmpfs /src/coverage` in `DockerRunner`** — only covers a `coverage/` at the mount root, and leaves the image broken for direct `docker run` users.
- **Rescue `Errno::EROFS` and retry without coverage** — brittle; depends on parsing error output.
- **Drop `:ro` from the project mount** — weakens the isolation tingle relies on.

### Testing strategy

Regression coverage lives in the image smoke test (`smoke_test_rubycritic`, `scripts/release_image.sh`), since the fix is image-only:

- Add `docker/rubycritic/fixture/coverage/` with a small SimpleCov `.resultset.json` and an empty `.resultset.json.lock` (the path is not gitignored). The smoke test already mounts the fixture `:ro`, so it reproduces the crash before the fix and passes after.
- Assert the run still exits 0 with one JSON object, and that nothing under `coverage/` appears in `analysed_modules` or `parse_errors`.
- Update the fixture table and assertion list in `docs/agents/tingle-rubycritic-image.md` ("Smoke test").
- No Python tests: no Python code changes.

### Scope

**In scope**

- `docker/rubycritic/entrypoint.rb`: pass `--coverage-path` under `/tmp` to `rubycritic`.
- `docker/rubycritic/fixture/coverage/` and the smoke-test assertions.
- Docs: `docs/agents/tingle-rubycritic-image.md` (contract/smoke test) and `docker/rubycritic/DOCKERHUB_DESCRIPTION.md` if the contract wording changes (e.g. note that a project's `coverage/` is ignored).

**Out of scope**

- Any change to `DockerRunner` or to the `:ro` project mount.
- Surfacing RubyCritic coverage in tingle's report.

### Backward compatibility

- No change to the image's stdin/stdout contract or to tingle's output: coverage was never consumed.
- tingle `X.Y.Z` pins `darthjee/tingle_rubycritic:X.Y.Z`, so the fix reaches users only with the next release (CLI + image published together). Earlier tingle versions keep the bug; the workaround there is to delete `coverage/.resultset.json.lock` before running.

## Benefits

- `tingle code_check rubycritic` works on any Ruby project that has run its specs with SimpleCov, without manual cleanup.
- The image honours its own contract again: a read-only `/src`, and writes only under `/tmp`.
- The project mount stays read-only, so tingle's isolation guarantees are untouched.
