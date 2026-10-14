# Move the remaining contract into the image doc
`docs/agents/tingle-js-complexity-image.md` must stand on its own once the
specs are gone.

- Add a `### Merged JSON` subsection inside `## Contract` with the
  **Keys and types** table, its rules (`null` vs `[]`/`0`, all three `null` on
  a parse error, no version field, unknown extra keys ignored) and the
  **Per-file states** table from `specs/code_check/js_complexity/image.md §7`.
  Rewrite them as the current contract: `tool_versions.jscpd` is `"5.4.1"`,
  `tool_versions.escomplex` is `"0.1.0"`, `duplication` and `functions` are
  always filled as described, and the `duplication.md`/`details.md` links
  become in-doc links.
- Replace the link to `image.md §7` (around line 356) with a link to
  `#merged-json`.
- Remove the intro sentence that says the full specs still live under
  `specs/code_check/js_complexity/` (lines 16-23).
- The links to `duplication.md §2` (around line 190) and `details.md §2`
  (around line 257) give the *reasons* for the pinned options. Move any
  reason that is still normative into the doc in a sentence or two, then
  drop the link.
- In `### Single-file components`, drop "The full design and its grounding
  are in sfc.md while the specs exist; this section is the lasting contract".
- Diff the remaining spec files (`image.md`, `duplication.md`, `details.md`,
  `sfc.md`, `release.md`) against the doc and move any normative rule that
  is still missing. Do not move the grounding run (`image.md §10`), the
  release ordering rule (`release.md §1`) or anything that only describes
  which sub-issue did what.

## Files to Change
- `docs/agents/tingle-js-complexity-image.md` — new `### Merged JSON` subsection, spec links removed, missing normative content moved in.
