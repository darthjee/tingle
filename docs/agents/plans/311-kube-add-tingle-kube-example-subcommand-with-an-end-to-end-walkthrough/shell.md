# Shell Plan: kube: add `tingle kube example` subcommand with an end-to-end walkthrough

Main plan: [plan.md](plan.md)

## Shared contracts

- Add the token `examples` to `INCLUDES` in `scripts/release_cli.sh`; the
  python agent's test reads that line and asserts the token is present.

## Implementation Steps

### Step 1 — Ship examples/ in the release zip

Add `examples` to `INCLUDES` in `scripts/release_cli.sh`
(`INCLUDES="bin commands completions examples install shell python node
README.md LICENSE"`). Leave `PRUNE_PATTERN` unchanged. Check with
`git ls-files -- examples` (after the examples agent's file exists) that the
file is selected by `resolve_files`.

## Files to Change

- `scripts/release_cli.sh` — `INCLUDES` gains `examples`.

## Notes

- `scripts/` has no dedicated owner; the shell agent takes this one-line
  Bash change.
