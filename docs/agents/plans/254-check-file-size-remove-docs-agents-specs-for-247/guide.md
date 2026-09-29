# Guide Plan: check_file_size: remove docs/agents/specs/ for #247

Main plan: [plan.md](plan.md)

## Shared contracts

- Runs before the specs are deleted. Use `docs/agents/specs/check_file_size/*.md` as the checklist.
- The guide must cover every feature, config key and contract listed in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Check the guide against the specs
Go through every spec file and every user-visible rule in it: flags, defaults, config keys, precedence, filter order, the `--min-level` interaction with `--top` / the summary / `--fail-on`, the `Config:` header line, error messages and exit codes. For each one, confirm `docs/guides/check_file_size.md` describes it. The guide already has a section per feature (`--exclude`, `--no-default-excludes`, `.gitignore and --no-gitignore`, `--ignore and --include`, `--min-level`, `Configuration file` with `Keys`, `How the config and the command line combine`, `--no-config`, `Config errors`, `Exit status and errors`), so expect gaps to be small or absent. Only user-facing behaviour matters here. Internal details such as function names or module layout stay out of the guide.

### Step 2 — Fill any gaps
Add whatever is missing to the right existing section of the guide, in its current style. If there are no gaps, make no change and say so in the commit or PR summary.

## Files to Change
- `docs/guides/check_file_size.md` — only if Step 1 finds a gap.

## CI Checks
- Docs: the `lint` job in `.circleci/config.yml`. Run its local equivalent if it covers Markdown.

## Notes
- Don't restructure the guide. This is a coverage check, not a rewrite.
