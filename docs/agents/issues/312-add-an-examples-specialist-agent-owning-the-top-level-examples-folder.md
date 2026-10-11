# Issue: Add an `examples` specialist agent owning the top-level `examples/` folder

## Description

Add a new specialist agent, `examples`, that owns the new top-level
`examples/` folder introduced by #311.

`examples/` holds end-user walkthrough text files that ship in the release zip
and are printed by tingle commands at runtime (the first one being
`examples/kube/end_to_end.txt`, printed by `tingle kube example`).

## Problem

None of the existing agents fits `examples/`: `guide` owns `docs/guides/`
(repository-only, not shipped), `python`/`shell`/`node` own code rather than
prose, and `architect` is for coordination and root-level files. Without an
explicit owner, work on shipped examples has no clear delegation target.

## Solution

- Create `.claude/agents/examples.md`, following the shape of the existing
  agent files (e.g. `.claude/agents/guide.md`):
  - frontmatter `name: examples`, a one-line `description` ("Tingle examples
    owner. Use for any task involving examples/ content — shipped,
    terminal-printed walkthroughs, one folder per tingle command."), and
    `tools: Read, Edit, Write, Bash`;
  - **Scope:** owns `examples/`, organised as `examples/<command>/<name>.txt`.
    Does NOT touch `python/`, `shell/`, `node/`, `bin/`, `commands/`
    implementation (including the code that reads/prints the files),
    `docs/guides/` (`guide`), `docs/agents/` (`product-owner`) or root-level
    files (`architect`).
  - **Conventions:** plain ASCII, lines within ~80 columns; one linear,
    step-by-step walkthrough per file; clearly fictional identifiers only
    (e.g. AWS account `123456789012`), never values from a real environment
    and never secrets; keep each example in sync with the command's real
    behaviour (`long_help` in `commands/*.json` and `docs/guides/<command>.md`);
    files under `examples/` ship in the release, so they must stay free of
    anything that should not be distributed.
- Register the agent everywhere the roster is listed:
  - `AGENTS.md` (Tools list) and `CLAUDE.md`'s agent list;
  - `.claude/agents/architect.md` — the agent roster table, plus a delegation
    line next to the existing `guide` one ("Shipped examples (`examples/`)
    belong to `examples` — delegate to it likewise.");
  - `docs/agents/folder-structure.md` — a row for `examples/`, owned by the
    `examples` agent.
- Packaging `examples/` into the release zip and the code that prints the
  files are out of scope here (they belong to #311).

## Benefits

- Gives the new shipped `examples/` folder an explicit owner, so #311 and
  future examples (e.g. for `code_check`) have a clear delegation target.
