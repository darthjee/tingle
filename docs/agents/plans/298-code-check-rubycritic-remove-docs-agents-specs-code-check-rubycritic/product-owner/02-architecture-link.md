# Drop the spec link from architecture.md

At `docs/agents/architecture.md` ~lines 138-140, the sentence "The Docker runner
contract, in short (the full rules are in [specs/code_check/rubycritic/subcommand.md](...), sections 3 and 4):"
loses its parenthetical spec link. Keep the short summary bullets that follow.
Optionally say the code and tests are the reference for the full rules, and link
`tingle-rubycritic-image.md#rubycritic-json-contract` where the JSON output is mentioned.

## Files to Change
- `docs/agents/architecture.md` — remove the link into the specs.
