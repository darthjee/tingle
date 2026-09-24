# Plan: docs: add user guide for tingle linux (docs/guides/linux.md)

Issue: [176-docs-add-user-guide-for-tingle-linux-docs-guides-linux-md.md](../../issues/176-docs-add-user-guide-for-tingle-linux-docs-guides-linux-md.md)

## Overview
Add the end-user guide `docs/guides/linux.md` for `tingle linux`, link it
from the guides index, and link the `linux` row of the root `README.md`
Scripts table to it. This follows the same pattern as #175 (`install`
guide).

See [guide.md](guide.md) for the full plan of the guide work.

## Architect step — link the root README row
After the `guide` agent's work is done, the `architect` changes the
`linux` row of the Scripts table in the root `README.md` from
`| \`linux\` | Shell | ... |` to
`| [\`linux\`](docs/guides/linux.md) | Shell | ... |`, the same way the
`install` row is linked. `README.md` is a root file, so `guide` must not
edit it.

- `README.md` — link the `linux` row to `docs/guides/linux.md`.
