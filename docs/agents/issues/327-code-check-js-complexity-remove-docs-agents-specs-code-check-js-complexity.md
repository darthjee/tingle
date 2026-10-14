# Issue: code_check js_complexity: remove docs/agents/specs/code_check/js_complexity/

## Description
Final cleanup sub-issue of #315. All other sub-issues (#316–#326) are closed. This issue removes the temporary specs for `tingle code_check js_complexity` under `docs/agents/specs/code_check/js_complexity/`, following the cleanup rule in `docs/agents/specs.md`. It mirrors #298, which did the same for rubycritic.

## Problem
Permanent files still point into the specs:

- `docs/agents/tingle-js-complexity-image.md`: the intro ("The full specs still live under ..."), the jscpd and escomplex sections (links to `duplication.md §2` and `details.md §2`), the stdout contract (link to `image.md §7` for key types and per-file states) and the *Single-file components* section (link to `sfc.md`).
- `.claude/agents/shell.md`: the bump procedure links to `image.md#13-bumping-versions`.
- `docker/js_complexity/Dockerfile`, `entrypoint.js`, `lib/staging.js`, `lib/jscpd.js`, `lib/escomplex.js` and `lib/sfc.js`: "Contract:" comments.
- `scripts/release_image.sh`: the comments above the js_complexity smoke-test checks.
- `python/tests/code_check/js_complexity/sample_output.py`: the module docstring (`image.md §7`).
- `docs/agents/specs.md`: the Current specs row.

The image doc already covers most of the image contract, but the **key/type table and the per-file states table** of the merged JSON (`image.md §7`) exist only in the spec. Deleting the folder as-is would leave broken links and lose that content.

`docs/agents/architecture.md` has no link into the specs and already documents the `docker_check` package.

## Expected Behavior
- `docs/agents/specs/code_check/js_complexity/` is deleted, and `docs/agents/specs/code_check/` too (it becomes empty).
- The `code_check js_complexity` row is removed from the Current specs table in `docs/agents/specs.md`, and "No specs in progress." is restored.
- No file in the repo (docs, agent definitions, code comments, tests) references `docs/agents/specs/code_check/js_complexity/`. Only historical `docs/agents/issues`/`plans` files may still match.
- `docs/agents/tingle-js-complexity-image.md` is self-sufficient:
  - the merged-JSON **keys and types** table and the **per-file states** table move into its *Contract* section, rewritten as the current contract (no "from #324" / "null before #325" history);
  - the intro no longer mentions the specs;
  - jscpd, escomplex and SFC details that are still normative and only in the specs move in too.
- Code comments and the shell agent point to the matching section of the image doc (by heading, not spec section number).
- Historical and process content (merge order, the grounding run in `image.md §10`, the release ordering rule in `release.md §1`) is dropped, not moved.
- The outdated line in `docs/agents/architecture.md` saying `python/code_check/js_complexity/` "has no `config.py` yet (the config section arrives with #322)" is corrected: `config.py` exists now.
- No behaviour change: only docs, comments and the test docstring change.

## Solution
1. Diff each spec file against the permanent docs (`docs/agents/tingle-js-complexity-image.md`, `docs/agents/architecture.md`, `docs/guides/code_check/js_complexity.md`) and move what is still normative and missing (at least `image.md §7` *Keys and types* and *Per-file states*).
2. Fix the outdated `config.py` line in `docs/agents/architecture.md`.
3. Repoint every reference listed under Problem to the matching permanent section.
4. Delete the specs folder (and the now-empty `code_check/` folder) and the `specs.md` row.
5. Verify with `grep -rn 'specs/code_check/js_complexity' . --exclude-dir=.git`, ignoring `docs/agents/issues` and `docs/agents/plans`.

### Agents
- `product-owner`: `docs/agents/` changes (image doc, `architecture.md`, `specs.md`, deleting the specs).
- `shell`: comments in `docker/js_complexity/` and `scripts/release_image.sh`.
- `python`: the docstring in `python/tests/code_check/js_complexity/sample_output.py`.
- `architect`: `.claude/agents/shell.md`.

## Benefits
- Closes out #315 with no broken links and without losing the contracts that the code and future version bumps rely on.
