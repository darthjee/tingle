# Plan: kube: add `tingle kube example` subcommand with an end-to-end walkthrough

Issue: [311-kube-add-tingle-kube-example-subcommand-with-an-end-to-end-walkthrough.md](../../issues/311-kube-add-tingle-kube-example-subcommand-with-an-end-to-end-walkthrough.md)

## Overview

Add a `tingle kube example` subcommand that prints a bundled, plain-ASCII,
step-by-step walkthrough (configure context/namespace/pod -> switch -> list ->
shell) read from a new shipped top-level folder, `examples/`. The command and
its completion never load the kube config, run the AWS credential check, or
call `aws`/`kubectx`/`kubectl`. The walkthrough text is owned by the new
`examples` agent introduced by #312, which must be merged first.

## Agents involved

- [examples](examples.md) — writes `examples/kube/end_to_end.txt` (requires #312)
- [python](python.md) — parser, dispatch, completion, tests
- [cli](cli.md) — `kube.long_help` in `commands/python.json`
- [shell](shell.md) — add `examples` to `INCLUDES` in `scripts/release_cli.sh`
- [guide](guide.md) — `docs/guides/kube.md`
- [product-owner](product-owner.md) — `docs/agents/` (folder structure, release zip, architecture)

## Shared contracts

- **Subcommand:** `tingle kube example`, no positional arguments and no flags
  (argparse rejects extras with the usual usage error). Parsed as
  `{"subcommand": "example"}`.
- **Example file path (repo-relative):** `examples/kube/end_to_end.txt`.
- **Runtime resolution:** from `python/kube/<module>.py`, the file is
  `Path(__file__).resolve().parents[2] / "examples" / "kube" / "end_to_end.txt"`
  (i.e. relative to the tingle install root, never the cwd). In the release
  zip the layout is identical (`python/` and `examples/` are siblings).
- **Release:** `scripts/release_cli.sh` `INCLUDES` gains the token
  `examples`, so `git ls-files -- examples` is packaged.
- **File format:** plain ASCII, read as UTF-8, lines <= ~80 columns, printed
  verbatim to stdout (no pager, no header/footer added by the code).
- **Fictional setup used in the text** (docs and help examples may refer to
  it): context alias `demo` ->
  `arn:aws:eks:us-east-1:123456789012:cluster/demo-cluster`; namespace alias
  `shop` -> `shop-backend`; pod alias `api` with prefix `shop-api-`,
  `id_pattern` `^[a-z0-9]{9,10}-[a-z0-9]{5}$`, namespace `shop`; pod names
  `shop-api-5f7c9d8b6a-k3m8p`, `shop-api-5f7c9d8b6a-q7n2w`.

## Order

1. #312 (new `examples` agent) merged first.
2. `examples` writes the text file; `shell` updates `INCLUDES`.
3. `python` (its tests read the real file and `release_cli.sh`).
4. `cli`, `guide`, `product-owner` docs/help.
