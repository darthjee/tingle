## Overview

Configuration slice of `tingle kube`, plus final polish. Lets the user manage `~/.tingle/kube/config.json` entirely through prompts instead of hand-editing JSON, and closes out the remaining edge cases and output polish from the parent spec.

Part of the `tingle kube` epic (see parent issue). Depends on children #1-#4 — all commands and the full config schema must exist before configuration/polish can close them out. Last in the strictly serial sequence.

## Scope

- `tingle kube configure context|namespace|pod` — interactive Python mode (prompts only, does not invoke `kubectl`/`kubectx`/`aws`):
  - `configure context` has no outer scope (it defines scope) — prompts go straight to alias → real name/ARN, skipping any scope-selection step.
  - `configure namespace` and `configure pod` cascade: scope (context) → alias → real value, since both live inside a context block.
  - For `pod`: prefix + optional `id_pattern` + optional namespace alias (same scope).
  - Support create/edit/remove of aliases at each level.
  - Removing a context alias cascades: its `namespaces[alias]` and `pods[alias]` blocks are deleted along with it, so `config.json` never holds orphaned scope data.
- Safe `config.json` writing: validate the JSON structure against the schema (owned by child #1) before saving, so a bad interactive session never corrupts the file on disk.
- Polish pass across all commands built in children #1-#4:
  - Structured `--json` output on `list` commands.
  - Rich error messages with suggestions (nonexistent context/namespace, alias out of scope, no pod match, pod not Running — per parent issue Section 6).
  - Sweep the edge cases table in Section 6 of the parent issue and confirm each is handled consistently across commands.

## Out of scope

- Changing the config schema's shape — this issue only adds validated read/write access to the existing schema (owned by child #1); schema changes should go back to child #1 if truly needed.
- New cluster-facing commands — no new `kubectl`/`kubectx`/`aws` invocations are introduced here.

## Shared contracts closed by this issue

- **`~/.tingle/kube/config.json` schema** — child #1 opened it; this issue is the last consumer/writer and should treat the schema as closed once this lands (no silent schema drift going forward).

## Acceptance Criteria

- `tingle kube configure context|namespace|pod` supports create/edit/remove for aliases at each level via cascading prompts (`context`: alias → value; `namespace`/`pod`: scope → alias → value).
- Removing a context alias cascades to delete its `namespaces`/`pods` blocks, leaving no orphaned scope data.
- Config writes are validated before saving; an invalid interactive edit never corrupts `config.json`.
- `list namespace` / `list pods` support `--json` output.
- All Section 6 edge cases (invalid AWS credentials, nonexistent context, nonexistent namespace, alias out of scope, no pod match, pod not Running, missing/invalid config) produce the documented behavior consistently across every command.
- Definition of Done from the parent issue is fully satisfied by this point: `tingle kube` responds for all commands, aliases resolve correctly and independently per scope, no unsafe pod exec happens silently, and everything is configurable without hand-editing JSON.

## Suggested agent(s)

python (+ cli + architect for final cross-command consistency review)
