# Python Plan: code_check rubycritic: per-method complexity drill-down (--details)

Main plan: [plan.md](plan.md)

## Shared contracts

- Consumes the image's `methods` key ([plan.md → Image stdout](plan.md#image-stdout-new-top-level-methods-key)).
- Provides `--details [N]` and the `details` config key ([plan.md → CLI flag and config key](plan.md#cli-flag-and-config-key)).
- Missing-key error and detail-line layout: [plan.md](plan.md#missing-methods-key).

## Steps

- [01 — Parse the `methods` key](python/01-parse-methods.md)
- [02 — Add the `--details` flag](python/02-details-flag.md)
- [03 — Print the detail lines](python/03-report-details.md)
- [04 — Add the `details` config key](python/04-config-key.md)

## CI Checks
- `python/`: `ruff check .` (CI job: `lint`), `pytest` (CI job: `tests`), run from `python/`. Coverage stays at or above 75%.

## Notes
- `code_check.completion` reads `FLAGS`. With `nargs='?'` it treats `--details` as value-taking with free-form choices, which is fine. Add a completion test if one exists per flag.
- The `--fail-on` gate and the summary don't change.
