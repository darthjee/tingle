# Verify the image

Run the checks from spec sections 6 and 7 by hand. Report the commands and
their results in the PR description. The scripted `smoke_test_rubycritic`
belongs to #294, so do not add one here.

1. `docker buildx build --platform linux/amd64 docker/rubycritic` and
   `docker buildx build --platform linux/arm64 docker/rubycritic` both
   succeed.
2. `make rubycritic-image`.
3. From `docker/rubycritic/fixture`, run:

   ```
   ls *.rb | docker run --rm -i --pull never --network none \
     --security-opt no-new-privileges --user 501:20 \
     -v "$PWD":/src:ro -w /src tingle_rubycritic:dev
   ```

   Then check, for example with `python3 -c` or `jq`, that:
   - the exit status is 0 and stdout is one JSON object;
   - `metadata.rubycritic.version == "5.0.0"`;
   - the `analysed_modules[].path` set is exactly the six non-broken files;
   - `parse_errors[].path == ["broken.rb"]`;
   - `score` is in [0, 100];
   - the per-file expectations from step 04 hold.
4. `docker run --rm --entrypoint sh tingle_rubycritic:dev -c 'command -v git'`
   exits non-zero.
5. `printf '' | docker run --rm -i ... tingle_rubycritic:dev` prints the empty
   object from spec section 4 and exits 0.
6. Optional: pass a missing path, and check it lands in `parse_errors` without
   failing the run.

## Files to Change
- None. This step is verification only.
