# Write README.md (shared contracts)
Create `docs/agents/specs/code_check/rubycritic/README.md`. It is the overview and the single source of truth for everything more than one sub-issue relies on.

It must contain:
- **Overview:** what `tingle code_check rubycritic <path>` does, and a link to the parent #290.
- **Sub-issue table:** one row per sub-issue, #292–#298, giving its title, spec file (#292 and #298 have none), owning agent(s) and dependencies. It also states the merge order:
  - #292 comes first.
  - After that, two tracks run in parallel: #293 → #294 and #295 → #296 → #297.
  - #298 comes last.
  - #294 must be merged before the tingle release tag that ships #295.
- **CLI and flags:** the full flag list, with types and defaults, and which sub-issue adds each flag.
- **Exit codes:** 0, 1 and 2, and what triggers each.
- **Config keys:** the list, with a pointer to `config.md`.
- **Default excludes:** the full list (`file_size`'s `DEFAULT_EXCLUDES` + `tmp`, `log`, `.bundle`).
- **Filter order:** default excludes → `--exclude` → `.gitignore` → `--ignore` → `--include`/`.rb`.
- **Image contract summary:**
  - the image name and tag rule
  - the `docker run` line
  - stdin: one relative path per line
  - stdout: the RubyCritic JSON
  - stderr: everything else
  - pointers to `image.md` and `subcommand.md`
- **Ownership:** the new top-level `docker/` folder is owned by the `shell` agent, and #293 records it in `.claude/agents/shell.md` and `docs/agents/folder-structure.md`.
- **Contradictions:** if step 01 found any contradiction with #290, list it here with the chosen resolution.

## Files to Change
- `docs/agents/specs/code_check/rubycritic/README.md`: new.
