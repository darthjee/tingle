# Register the specs in docs/agents/specs.md
Update the permanent specs index.

- Under **Current specs**, replace "No specs in progress." with the table from the conventions:

  | Topic | Specs | Parent issue | Sub-issues |
  |---|---|---|---|
  | `code_check rubycritic` | [code_check/rubycritic/](specs/code_check/rubycritic/README.md) | #290 | #292 #293 #294 #295 #296 #297 #298 |

- Under **Conventions** (and **Layout** if needed), allow a topic to be a nested `<command>/<subcommand>/` folder, e.g. `code_check/rubycritic/`.
- Check that every link in the new specs resolves: the relative links between spec files, and the links to repo files.

## Files to Change
- `docs/agents/specs.md`: add the index row and the nested-folder convention.
