# Python Plan: kube: add `tingle kube example` subcommand with an end-to-end walkthrough

Main plan: [plan.md](plan.md)

## Shared contracts

- Subcommand `example` with no arguments; parsed dict
  `{"subcommand": "example"}`.
- Read `Path(__file__).resolve().parents[2] / "examples" / "kube" /
  "end_to_end.txt"` as UTF-8 and write it verbatim to stdout.
- Never construct `KubeConfig()`, never run the AWS check, never call
  `aws`/`kubectx`/`kubectl` — in `run` or in `complete`.
- Relies on `examples/kube/end_to_end.txt` (examples agent) and the
  `examples` token in `scripts/release_cli.sh` `INCLUDES` (shell agent).

## Steps

- [01 — Add the example subcommand](python/01-add-example-subcommand.md)
- [02 — Complete the example subcommand](python/02-complete-example-subcommand.md)
- [03 — Guard that the example ships](python/03-guard-example-ships.md)

## CI Checks

- `python`: `cd python && ruff check . && pytest` (CI jobs: lint, tests)

## Notes

- Tests compare output against the file itself, never hard-coded guide text,
  so the walkthrough can be edited freely.
