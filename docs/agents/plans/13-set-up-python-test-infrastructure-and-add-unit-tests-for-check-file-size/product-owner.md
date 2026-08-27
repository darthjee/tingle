# product-owner Plan: Set up Python test infrastructure and add unit tests for check_file_size

Main plan: [plan.md](plan.md)

## Shared contracts

- Records exactly what `python` and `architect` decided, verbatim: test
  folder is `python/tests/` (mirroring `python/`'s package layout, not a
  top-level `tests/`), and the new `.circleci/` root folder is owned by
  `architect`.

## Implementation Steps

### Step 1 — Record the test folder location decision

In `docs/agents/architecture.md`, under the existing `### python/` section
(or immediately after it), add a short note establishing `python/tests/` as
the test folder convention for `python/` — mirroring the package layout
(`python/tests/check_file_size/`, `python/tests/common/`) rather than a
top-level `tests/` — so future Python commands under this repo follow the
same pattern issue #13 established.

### Step 2 — Record `.circleci/` folder ownership

In `docs/agents/architecture.md`'s "Source Code Layout" section, add a
`.circleci/` entry (alongside the existing `python/`, `shell/`, `node/`,
`bin/`, `completions/` entries) noting it holds the CI pipeline config and
is owned by `architect`, since it's cross-cutting rather than
language-specific.

## Files to Change

- `docs/agents/architecture.md` — add the two decisions above.
