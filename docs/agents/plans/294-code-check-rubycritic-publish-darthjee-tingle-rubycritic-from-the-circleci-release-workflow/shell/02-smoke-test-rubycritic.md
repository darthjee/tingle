# Add smoke_test_rubycritic
Add `smoke_test_rubycritic <image> <platform>` to `scripts/release_image.sh`. It runs the fixture checks from [image.md section 6](../../../specs/code_check/rubycritic/image.md#6-smoke-test-fixture) against the local `<tag>-<arch>` image.

- **Run line:** `docker run --rm -i --platform <platform> --network none --user 501:20 -v "$PWD/docker/rubycritic/fixture:/src:ro" <image>` (match the canonical run line in [subcommand.md](../../../specs/code_check/rubycritic/subcommand.md) for working dir and mounts). Pipe in the fixture list, one path per line: `simple.rb complex.rb dup_a.rb dup_b.rb broken.rb empty.rb constants_only.rb`.
- **Checks**, done with `python3` on stdout:
  - exit status 0;
  - stdout is one JSON object;
  - `metadata.rubycritic.version == "5.0.0"`;
  - the `analysed_modules[].path` set is exactly the six non-broken files;
  - `parse_errors[].path == ["broken.rb"]`;
  - `0 <= score <= 100`;
  - per-file expectations:
    - `simple.rb`: complexity < 5, rating `A`;
    - `complex.rb`: complexity > 50;
    - `dup_a.rb`/`dup_b.rb`: duplication > 0;
    - `empty.rb`/`constants_only.rb`: complexity 0.0, methods_count 0.
- `command -v git` fails inside the image (`--entrypoint sh`).
- Empty stdin prints the empty object from image.md section 4 and exits 0.
- A failing check prints `<reason> on <platform>` on stderr and exits 1. Reuse `smoke_fail` if its wording fits.
- The python assertions read the JSON from stdin and the platform from argv. Keep them in one inline `python3 -c` (or heredoc) block, like the existing python snippets in the script.

## Files to Change
- `scripts/release_image.sh` — new `smoke_test_rubycritic` function, wired into `cmd_smoke_test` for the `rubycritic` selector.
