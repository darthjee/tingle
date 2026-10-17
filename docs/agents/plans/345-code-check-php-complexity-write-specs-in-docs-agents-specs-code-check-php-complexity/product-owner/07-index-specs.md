# Index the specs in docs/agents/specs.md
Add this row to the **Current specs** table and remove the "None currently." line:

```markdown
| `code_check/php_complexity` | [specs](specs/code_check/php_complexity/README.md) | #344 | #345–#353 |
```

Then check that every relative link in the new spec files resolves, and that each spec file links its sub-issue and `README.md`.

## Files to Change
- `docs/agents/specs.md`: add the php_complexity entry.
