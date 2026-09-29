# Product-owner Plan: install: add update mode to installer.sh

Main plan: [plan.md](plan.md)

## Shared contracts

Record in the specs exactly what [plan.md](plan.md#shared-contracts) lists:
the new `TINGLE_UPDATE_CLEANUP` env var (set by `tingle update`, unset when
the installer is run by hand), `TINGLE_UPDATE_TARGET` normalization,
`MANIFEST` being staged and swapped too, refusing a missing/malformed/empty
incoming `MANIFEST`, keeping file permissions when staging, and the
unsafe-path rule applying to every path.

## Implementation Steps

### Step 1 — Sync the update_command specs
- `installer-update-mode.md`: add `TINGLE_UPDATE_CLEANUP` and the
  normalization rule to §2's table; in §3.1 add the incoming-`MANIFEST`
  refusal; in §3.2 add permission keeping and staging `MANIFEST`; in §3.6
  and S3 (§4) make temp-dir removal conditional on `TINGLE_UPDATE_CLEANUP=1`;
  make the unsafe-path rule in §3.4 explicitly cover hashing, staging and
  swapping; add the new cases to §7 Testing and the new env var to §8.
- `README.md`: wherever the shared contracts list the update-mode env vars
  or the temp-dir ownership, add `TINGLE_UPDATE_CLEANUP`.
- `update-command.md`: `tingle update` sets `TINGLE_UPDATE_CLEANUP=1` (along
  with `TINGLE_UPDATE_TARGET`, `TINGLE_REPO`, `TINGLE_VERSION`) before
  `exec`ing the new installer.

## Files to Change
- `docs/agents/specs/update_command/installer-update-mode.md` — new rules above.
- `docs/agents/specs/update_command/README.md` — `TINGLE_UPDATE_CLEANUP` in the shared contracts.
- `docs/agents/specs/update_command/update-command.md` — `tingle update` sets `TINGLE_UPDATE_CLEANUP=1`.

## Notes
- `README.md` wins over feature specs, so keep all three files consistent.
