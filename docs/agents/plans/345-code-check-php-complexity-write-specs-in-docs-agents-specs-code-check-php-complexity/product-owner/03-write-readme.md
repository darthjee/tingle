# Write README.md (shared contracts)
Write `docs/agents/specs/code_check/php_complexity/README.md`, the normative source for everything more than one sub-issue relies on. It links the parent #344.

It has these sections:
1. **Overview:** what the check does, PDepend plus jscpd, and the image name. It also lists the spec files, each with the sub-issue that implements it.
2. **Sub-issues and merge order:**
   - #345–#353, each with its dependencies.
   - The image track (#346 → #347) and the Python track (#348 → #349 → #350) run in parallel.
   - #347 must be merged before the tingle tag that ships #348.
   - #351 and #352 change the image and Python in the same PR.
3. **CLI and flags:** the full flag table, with types, defaults and the sub-issue that adds each flag. The thresholds are on total CCN, with the calibrated defaults from step 02 and their table. There is no `--ext`.
4. **Extensions:** `.php` only, matched case-insensitively. `*.blade.php` is always skipped.
5. **Default excludes:** `file_size`'s `DEFAULT_EXCLUDES` plus `vendor`, `var`, `storage`, `bootstrap/cache` and `.phpunit.cache`.
6. **Filter order:** the same order as js_complexity's, with the Blade skip placed in it.
7. **Config keys:** the `php_complexity` section's keys and validators, the sub-issue that adds each key, and `ext` rejected as unknown.
8. **Exit codes and streams:** `0`, `1` and `2`, and what goes to stdout vs. stderr (including the `Pulling` message and warnings).
9. **Image contract summary:**
   - stdin is the file list; stdout is one JSON document; stderr carries diagnostics.
   - A **merged JSON summary**, with every key, its type and its nullability: `tool_versions`, and `files[]` with `path`, `parse_error`, the `pdepend` metrics, `functions` and `duplication`, plus `warnings`.
   - Which keys are `null` until #351 and #352 land.
10. **Pinned tools:** the base image (tag and digest), PDepend, Node and jscpd, from step 01.
11. **Deviations from #344:** numbered. Write "None" if there are none.

## Files to Change
- `docs/agents/specs/code_check/php_complexity/README.md`: new.
