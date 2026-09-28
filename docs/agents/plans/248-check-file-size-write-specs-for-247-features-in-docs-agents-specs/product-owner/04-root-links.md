# Link specs from root docs and agent scopes
Root-level files belong to the **architect**, who makes these edits (not `product-owner`).

- `AGENTS.md`:
  - Add a row to the Documentation table: `| [Specs](docs/agents/specs.md) | Temporary feature specs for split issues, indexed by specs.md. |`
  - Add a short `### Specs (docs/agents/specs/)` subsection describing the `docs/agents/specs/<topic>/README.md` + per-feature files convention.
  - Extend the `product-owner` bullet in Tools to mention specs.
- `.claude/agents/product-owner.md`: add `specs.md` and `specs/` to "Your scope".
- `CLAUDE.md`: update the "Last updated" date (and the Documentation summary, if needed) to stay consistent with `AGENTS.md`. `.github/copilot-instructions.md` only if it mirrors the docs index.

## Files to Change
- `AGENTS.md` — Documentation table row, Specs subsection, product-owner scope.
- `.claude/agents/product-owner.md` — scope list.
- `CLAUDE.md` — Last updated / summary.
