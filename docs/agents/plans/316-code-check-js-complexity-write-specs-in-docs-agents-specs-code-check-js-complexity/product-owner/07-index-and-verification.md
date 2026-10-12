# specs.md index and verification
1. In `docs/agents/specs.md`, replace "None currently." under **Current specs** with the row:

   | `code_check js_complexity` | [code_check/js_complexity/](specs/code_check/js_complexity/README.md) | #315 | #316 #317 #318 #319 #320 #321 #322 #323 #324 #325 #326 #327 |

   Keep the table header that is already there.
2. Make sure every feature spec links its sub-issue at the top.
3. Run the mechanical checks from the issue's **Verification** section:
   - every relative link resolves;
   - the sub-issue map matches the issue;
   - "Deviations from #315" is present;
   - the wording is normative;
   - `git diff --stat` shows only `docs/agents/specs/code_check/js_complexity/**` and `docs/agents/specs.md`.

## Files to Change
- `docs/agents/specs.md` — add the Current specs row.
