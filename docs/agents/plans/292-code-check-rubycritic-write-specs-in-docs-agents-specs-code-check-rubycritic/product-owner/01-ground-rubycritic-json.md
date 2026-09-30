# Ground the contract in a real RubyCritic run
Before writing any spec that depends on RubyCritic's output, run it for real and capture the facts. Work in a scratch directory outside the repo, or in a temporary folder that is never committed.

1. Choose the pins:
   - the latest `ruby:3.3.N-slim` patch tag on Docker Hub
   - the latest stable `rubycritic` gem version (`gem search -r ^rubycritic$` or rubygems.org)
2. In `ruby:3.3.N-slim`, **without installing git**, `gem install rubycritic -v <version>`.
3. Create a small set of sample files:
   - `simple.rb`: one trivial method
   - `complex.rb`: nested conditionals and loops, so Flog scores high
   - `dup_a.rb` + `dup_b.rb`: duplicated code, for Flay
   - `broken.rb`: a syntax error
   - `empty.rb`
   - `constants_only.rb`: a module with constants and no methods
4. Run it the way the image will:
   ```
   docker run --rm -i --network none --user <uid>:<gid> -v <fixture>:/src:ro -w /src <image-with-gem> \
     rubycritic --format json --no-browser -p /tmp/out <files>
   ```
   Then `cat /tmp/out/report.json`. For the first run, use a throwaway image built with the gem installed. If `--network none` or a foreign uid breaks the gem's runtime (HOME, tmp), record the environment the entrypoint needs, e.g. `HOME=/tmp`.
5. Record:
   - the exact JSON paths for the overall score, and for each file its path, complexity, rating, smells (count or list), duplication, and methods count (if present)
   - how paths are written (relative, `./`-prefixed or absolute `/src/...`)
   - how `broken.rb` shows up (missing, present with an error field, a stderr warning) and a reliable way for tingle to detect it
   - whether `empty.rb` and `constants_only.rb` are present
   - any git-related warnings when git is absent
   - whether `-p /tmp/out` works with a read-only `/src` and a foreign uid
   - the exit status in each case
6. Keep a trimmed sample of the real `report.json` for `subcommand.md`.

## Files to Change
- None in the repo. The findings feed steps 03 and 05.
