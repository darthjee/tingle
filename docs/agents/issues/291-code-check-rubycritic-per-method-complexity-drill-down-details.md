# Issue: code_check rubycritic: per-method complexity drill-down (--details)

## Description
Follow-up to #290. `tingle code_check rubycritic` shows one row per file with the file's total Flog complexity. This issue adds a `--details [N]` option that lists the most complex methods under each reported file.

Depends on #295 (the subcommand, merged) and on the image from #293/#294.

## Problem
A file-level Flog total says a file is complex, but not **which methods** make it complex. Users have to run Flog themselves to find them.

RubyCritic's JSON can't fill this gap on its own. It only lists a method when Flog flags it as a `HighComplexity`/`VeryHighComplexity` smell, which happens above roughly 25 Flog points. Every method below that is missing.

## Expected Behavior
- `tingle code_check rubycritic <path> --details` prints, under each file row the report already shows, that file's 5 highest-scoring methods. Each one is an indented line, sorted by score from highest to lowest:

  ```
  🔴 ERROR             212.40  F            3            0  app/models/order.rb
      72.00  Order#total            (app/models/order.rb:12)
      55.31  Order#apply_discounts  (app/models/order.rb:40)
  ```

  (The exact column alignment is decided in the plan, to match the existing table.)
- `--details N` shows up to N methods per file. `--details 0` shows all of them. `--details` with no value means 5. Without the flag, the report is unchanged.
- Details only appear for rows that are already shown, after `--top` and `--min-level` are applied. `PARSE` rows and files with no methods get no detail lines.
- Methods show only their score. They have no level, no colour by level and no gate: levels, `--fail-on` and the exit codes stay file-based.
- New config key `details` (int ≥ 0, or `null`) in the `rubycritic` section. The CLI wins over the config, following the existing precedence rules.

## Solution
### Image (`docker/rubycritic/`, `shell` agent)
- The entrypoint also runs Flog over every path that survives the pre-parse, scoring all methods. The Flog API in Ruby is preferred over parsing Flog's text output (for example `Flog.new(all: true, methods: true)`, then `each_by_score` and `method_locations`).
- It adds a top-level `methods` key to the JSON on stdout: a list of `{"path": <relative path as received>, "name": "Class#method", "line": <int>, "score": <number, 2 decimals>}`. Flog's non-method bucket (`#none`) is left out. When RubyCritic is not run (no surviving paths), the list is empty: `"methods": []`.
- Update the image spec/contract docs and the smoke test fixture checks. For example, `complex.rb` must have a `Complex#run` entry with a score above 50.
- The default image tag is the tingle version, so the new contract ships with the next tingle release, as before. The image publish must happen before the release tag is pushed.

### Subcommand (`python/code_check/rubycritic/`, `python` + `cli` agents)
- `--details [N]` (argparse `nargs='?'`, `const=5`, int ≥ 0; a negative value is a usage error, exit 1). It defaults to `None` in `FLAGS`, like the other single-value flags. Add it to the help text.
- Parse `methods` and group the entries by path, using the same path mapping as `analysed_modules`.
- If `--details` is set and the JSON has no `methods` key (for example an older image passed with `--image`), the run fails with exit 1 and an error saying the image doesn't provide per-method data. Without `--details`, a missing `methods` key is ignored, so older images keep working.
- Config: add `details` to the allowed keys and to validation.
- Tests: parsing, grouping, top-N per file, 0 = all, interaction with `--top`/`--min-level`, the missing-key error, and config.

### Docs (`guide` agent)
- Document `--details` and the `details` config key in the `code_check rubycritic` user guide.

## Benefits
- Users can go straight to the methods to refactor.
- The data is complete: every method is scored, not just the ones that RubyCritic flags as smells.
- Users don't need a local Ruby/Flog install.
