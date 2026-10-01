# Fixture, Makefile target and agent scope

Create the smoke-test fixture under `docker/rubycritic/fixture/`, as listed in
spec section 6:

| File | Content |
|------|---------|
| `simple.rb` | A class with one trivial method. Expected complexity below 5, rating `"A"`. |
| `complex.rb` | One method with nested conditionals, loops and a `case`. Expected Flog about 72, and at least above 50. |
| `dup_a.rb`, `dup_b.rb` | Two classes with the same method body. Both need `duplication` above 0. |
| `broken.rb` | A method with an unclosed parameter list. |
| `empty.rb` | An empty file. |
| `constants_only.rb` | A module with two constants and no method. |

Add a `rubycritic-image` target to the root `Makefile` (and to `.PHONY`). Its
recipe is a single tab-indented line,
`docker build -t tingle_rubycritic:dev docker/rubycritic`.

Extend `.claude/agents/shell.md`:

- add `docker/` to "Your scope", using the shared description;
- note the build context and the spec for bumps.

Keep the existing "Do NOT touch" list.

## Files to Change
- `docker/rubycritic/fixture/*.rb`: seven new files.
- `Makefile`: `rubycritic-image` target.
- `.claude/agents/shell.md`: scope now includes `docker/`.
