# Extend cli agent's own scope to commands/

Update `.claude/agents/cli.md` so the `cli` specialist's documented scope explicitly includes the new root-level `commands/` directory, since it's introduced by and tightly coupled to `bin/tingle`'s dispatch logic (per the issue's Ownership decision).

Add a line under "Your scope" alongside the existing `bin/` bullet, e.g.:

```markdown
- `commands/` — per-language mapping files (`commands/<lang>.sh`) that `bin/tingle` sources to resolve command names to script paths.
```

## Files to Change

- `.claude/agents/cli.md` — extend "Your scope" to include `commands/`.
