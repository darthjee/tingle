# Write details.md and duplication.md
**`docs/agents/specs/code_check/php_complexity/details.md` (#351):**
- `--details [N]` parsing: alone it means `5`, and `0` means all.
- The line format, e.g. `ccn 19  InvoiceService::reconcile   (L210)`, and the alignment.
- Ordering and tie-breaks: by CCN descending, then line.
- Anonymous functions and closures: whether and how they are named, based on what step 01 showed.
- It is never shown under `PARSE` rows, and it respects `--top`/`--min-level`.
- The `details` config key (`nullable_non_negative_int`).
- Whether #351 needs an image change: only if README §9 keeps `functions` `null` in #346.
- The test cases.

**`docs/agents/specs/code_check/php_complexity/duplication.md` (#352):**
- Adding Node and the pinned jscpd to the image: the stage layout and the lock file.
- The exact jscpd command and options, run on the same staged files.
- Mapping clones back to `<n>`. The `Dup` value is the number of the file's lines in any clone, counting each line once.
- The `duplication` JSON and `tool_versions.jscpd`.
- The `Dup` column's format, with `-` when there is no data.
- Degraded mode: jscpd fails → one stderr warning naming jscpd; the exit code is unaffected.
- Only the selection is considered.
- The test and smoke cases.

## Files to Change
- `docs/agents/specs/code_check/php_complexity/details.md`: new.
- `docs/agents/specs/code_check/php_complexity/duplication.md`: new.
