# Plan: docs: add user guide for tingle install (docs/guides/install.md)

Issue: [175-docs-add-user-guide-for-tingle-install-docs-guides-install-md.md](../../issues/175-docs-add-user-guide-for-tingle-install-docs-guides-install-md.md)

## Overview
Add the end-user guide `docs/guides/install.md` and link it from the guides
index. The `guide` agent owns this work. One small root-file edit (linking
the `install` row in the root `README.md` Scripts table) belongs to the
`architect`, because the `guide` agent must not touch root files.

See [guide.md](guide.md) for the full plan.

## Architect follow-up (root file)
- `README.md` — in the Scripts table, change the `install` cell to
  ``[`install`](docs/guides/install.md)``. Leave the rest of the row as it is.
