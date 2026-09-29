# Update the specs index
In `docs/agents/specs.md`, remove the `check_file_size` row from the "Current specs" table. No specs remain, so replace the table with a short line such as "No specs in progress." (drop the empty header row too). Keep the rest of the page as it is: intro, Layout and Conventions. The `specs/check_file_size` example paths in the prose use `<topic>` placeholders or the folder name as a convention example (`e.g. check_file_size`). That's fine to keep, since those aren't links. Change them to something neutral only if they read as links to the deleted folder.

## Files to Change
- `docs/agents/specs.md` — drop the `check_file_size` row and say no specs are in progress.
