# Issue: kube: add `tingle kube example` subcommand with an end-to-end walkthrough

## Description

Add a new `example` subcommand to `tingle kube` that prints a single, end-to-end
example to the terminal, covering the whole workflow in order:

1. configuration (`tingle kube configure context|namespace|pod`, and the
   resulting `~/.tingle/kube/config.json`);
2. `tingle kube switch <context_alias>`;
3. `tingle kube list namespace` and `tingle kube list pods --namespace <alias>`;
4. finally `tingle kube shell <namespace_alias> <pod_alias>`.

The example text lives in a text file shipped with tingle and is printed as-is
by the subcommand.

## Problem

The relationship between context aliases, namespace aliases and pod aliases
(and the "active scope" rule that ties them to the current kubectl context) is
easy to get wrong. For example, a context alias whose real name does not match
`kubectl config current-context` silently makes every namespace alias resolve
"as-is", and typing `optional` at the `id_pattern` prompt makes a pod alias
match nothing. A single worked example, available straight from the terminal,
shows how the pieces fit together.

## Expected Behavior

### Scope

The output is a single, linear, step-by-step guide that takes the user from an
empty configuration all the way to an open shell in a pod. Nothing more.

In scope:

- A new `tingle kube example` subcommand, with no arguments, that prints the
  content of a text file to standard output.
- The guide uses one consistent fictional setup throughout (for example
  context `demo`, namespace `shop`, pod `api`) and walks through, in order:
  1. `tingle kube configure context`
  2. `tingle kube configure namespace`
  3. `tingle kube configure pod`
  4. `tingle kube switch <context_alias>`
  5. `tingle kube list namespace`
  6. `tingle kube list pods --namespace <namespace_alias>`
  7. `tingle kube shell <namespace_alias> <pod_alias>`
- Wiring the new subcommand into the parser, bash completion,
  `tingle --help kube`, and a mention in `docs/guides/kube.md`.

Out of scope:

- Troubleshooting / common-mistakes sections, alternative flows, or multiple
  examples — it is one step-by-step guide only.
- Running anything: `example` never calls `aws`, `kubectx` or `kubectl`, and
  never reads or writes `~/.tingle/kube/config.json`.
- Generating the guide from the user's own config.
- Any change to the behaviour of the existing kube subcommands.

### Example content

A single guide with numbered steps and one fictional setup used throughout:

| Item | Alias | Real value |
|---|---|---|
| AWS account ID | — | `123456789012` (AWS documentation placeholder) |
| Region | — | `us-east-1` |
| Context | `demo` | `arn:aws:eks:us-east-1:123456789012:cluster/demo-cluster` |
| Namespace | `shop` | `shop-backend` (under context `demo`) |
| Pod | `api` | prefix `shop-api-`, `id_pattern` `^[a-z0-9]{9,10}-[a-z0-9]{5}$`, namespace `shop` |
| Example pod names | — | `shop-api-5f7c9d8b6a-k3m8p`, `shop-api-5f7c9d8b6a-q7n2w` |
| AWS profile (mentioned only) | — | `default` |

`demo` is used instead of `prod` so nobody copying the example thinks they are
targeting production. The names must not reuse anything from a real setup
(e.g. the reporter's own context, namespace or pod names).

Steps:

0. **Before you start** — 2–3 lines: `aws`, `kubectx` and `kubectl` on the
   `PATH`; the EKS context already in the kubeconfig
   (`aws eks update-kubeconfig ...`); AWS credentials exported or an
   `aws_profile` set. No further AWS detail.
1. `tingle kube configure context` — create `demo`.
2. `tingle kube configure namespace` — pick context `demo`, create `shop`.
3. `tingle kube configure pod` — pick context `demo`, create `api` with an
   explicit `id_pattern`; then show
   the resulting `~/.tingle/kube/config.json` once.
4. `tingle kube switch demo`
5. `tingle kube list namespace`
6. `tingle kube list pods --namespace shop`
7. `tingle kube shell shop api`

For each step: a one-line purpose, the command, and a short excerpt of the
expected output. The three `configure` steps show the prompt answers inline.

Short inline hints (one line each, inside the steps — not a troubleshooting
section) where they matter, e.g.:

- the real context name/ARN must match `kubectl config current-context`
  exactly, otherwise namespace and pod aliases are not resolved;
- `id_pattern` is set explicitly to `^[a-z0-9]{9,10}-[a-z0-9]{5}$` because
  Deployment pod names (`<hash>-<5 chars>`) do not match the default
  `pod_id_pattern` (`^[a-z0-9]{10}$`); leaving it empty uses that default.

Format: plain ASCII, lines kept within ~80 columns.

Sketch (abridged):

```
tingle kube - end-to-end example
================================

Setup used in this example:
  context   demo -> arn:aws:eks:us-east-1:123456789012:cluster/demo-cluster
  namespace shop -> shop-backend      (belongs to context demo)
  pod       api  -> prefix "shop-api-"  (lives in namespace shop)

0. Before you start
   ...

1. Create the context alias
   $ tingle kube configure context
   Select an action: 1            (create)
   Alias: demo
   Real context name/ARN: arn:aws:eks:us-east-1:123456789012:cluster/demo-cluster
   -> must match `kubectl config current-context` exactly

...

6. List pods
   $ tingle kube list pods --namespace shop
   api:
     - shop-api-5f7c9d8b6a-k3m8p
     - shop-api-5f7c9d8b6a-q7n2w

7. Open a shell
   $ tingle kube shell shop api
```

### Edge cases

- **Config loaded before dispatch.** `Kube.run()` (`python/kube/executor.py`)
  builds `KubeConfig()` before dispatching any subcommand; that load creates
  `~/.tingle/kube/config.json` when it is missing and prints the
  `created new config` / invalid-config pass-through notices. `example` must be
  dispatched **before** the config is loaded, so it behaves identically (and
  prints nothing extra) whether the config is missing, invalid or valid, and
  never creates the file.
- **Extra arguments** (`tingle kube example foo`, `--json`): rejected by the
  argument parser with the usual usage error.
- **Closed pipe** (`tingle kube example | head`): exits quietly, without a
  `BrokenPipeError` traceback.
- **Missing text file** (packaging bug): covered by a test asserting the file
  ships and is printed; at runtime a plain error is acceptable, no fallback
  text.
- **Encoding:** the text file is plain ASCII and read as UTF-8, so output is
  identical regardless of terminal or locale.
- **Missing/invalid AWS credentials:** irrelevant — `example` never runs the
  credential check.

### Paging

No built-in pager: `example` just prints the guide to standard output. Users
who want to page through it can pipe it themselves
(`tingle kube example | less`); a closed pipe exits quietly (see Edge cases).

## Solution

### Approach and alternatives

Chosen: a `tingle kube example` subcommand that prints a bundled text file. It
is discoverable from the terminal next to the other kube subcommands, needs no
config, AWS credentials or cluster, keeps the walkthrough as plain editable
content, and is trivial to test. `docs/guides/kube.md` gets a short pointer to
it.

Considered and rejected:

- **A "Getting started" section in `docs/guides/kube.md` only** — requires
  leaving the terminal, and the guide is already long; the walkthrough would be
  buried among reference material.
- **A help flag (`tingle --help kube --example` / `tingle kube --example`)** —
  `--help` is meant as a short summary; a long walkthrough behind a flag mixes
  concerns and is less discoverable than a named subcommand.
- **An interactive setup wizard (`tingle kube setup`)** — duplicates
  `configure`, needs AWS and the cluster, and turns a documentation feature
  into new behaviour with a much larger testing surface.
- **Generating the example from the user's own config** — depends on a valid
  existing config; already out of scope.

### Text file location and packaging

- The guide lives at `examples/kube/end_to_end.txt`, under a new top-level
  `examples/` folder meant to hold future examples for other commands as well
  (e.g. `examples/code_check/...`).
- `docs/` stays repository-only documentation (agent docs and guides) and is
  not shipped; `examples/` holds runtime assets read by the CLI, so it gets its
  own top-level folder instead of `docs/examples/`.
- `examples` is added to `INCLUDES` in `scripts/release_cli.sh` so the folder
  ships in the release zip.
- At runtime the file is resolved relative to the tingle install folder (from
  the Python module's location), never relative to the current working
  directory.
- A test/release check asserts the example file is part of the files
  `release_cli.sh` packages, so a later change to `INCLUDES` cannot silently
  drop it.

### Folder ownership

The new top-level `examples/` folder is owned by a new `examples` specialist
agent, added by #312 (a sub-issue of this one, to be done first). That agent
writes `examples/kube/end_to_end.txt`; the `python` agent owns the code that
reads and prints it, and the other wiring stays with its usual owners
(`guide` for `docs/guides/`, `product-owner` for `docs/agents/`, `architect`
for `scripts/release_cli.sh`).

### Wiring

1. **Parser** (`python/kube/parser.py`): add an `example` subparser with no
   arguments; add it to the module docstring's usage list.
2. **Dispatch** (`python/kube/executor.py`): handle `example` in `Kube.run()`
   *before* `KubeConfig()` is constructed (see Edge cases).
3. **Completion** (`python/kube/completion.py`): add `example` to
   `SUBCOMMANDS`; after `example`, return no candidates and return **before**
   `KubeConfig()` is constructed — today `complete()` loads the config for
   every subcommand except `configure`, so a Tab after `tingle kube example`
   would otherwise create `~/.tingle/kube/config.json`.
4. **Help** (`commands/python.json`, `kube.long_help`): add
   `tingle kube example` to Usage and Examples, plus one sentence saying it
   prints a step-by-step guide from configuration to shell. Also fix the
   existing inaccuracy where Usage/Examples show `tingle kube list [--json]
   pods` without the required `--namespace <namespace_alias>`.
5. **User guide** (`docs/guides/kube.md`): add `tingle kube example` to the
   Usage block and a short "Step-by-step example" note near the top pointing
   to it.
6. **Agent docs** (`docs/agents/`, e.g. `architecture.md` / folder structure):
   document the new top-level `examples/` folder, that it ships in the
   release, and that it is resolved relative to the install folder.
7. **Release** (`scripts/release_cli.sh`): add `examples` to `INCLUDES` (see
   Text file location and packaging).

`README.md`'s one-line kube description does not need to change.

### Testing strategy

Tests are minimal and cover the command, not the guide's content (the text can
change freely without breaking tests):

- **Parser:** `example` is accepted with no arguments; extra arguments are
  rejected.
- **Executor:** `tingle kube example` prints exactly the content of the bundled
  text file (compared against the file itself, not hard-coded text).
- **No side effects:** `example` does not load or create
  `~/.tingle/kube/config.json` and does not run the AWS credential check or
  any `aws`/`kubectx`/`kubectl` command.
- **Completion:** `example` is offered among kube subcommands.

### Performance & security

- **Made-up identifiers only:** the guide must use clearly fictional values —
  account ID `123456789012`, cluster ARNs such as
  `arn:aws:eks:us-east-1:123456789012:cluster/demo-cluster`, and the generic
  names listed under Example content (`demo`, `shop`, `shop-backend`,
  `shop-api-...`). No real account IDs, cluster
  names, namespaces, pod names, profiles or credentials from any real
  environment.
- **No secrets in the example:** the "Before you start" step mentions
  exporting AWS credentials without showing any key values (e.g.
  `export AWS_ACCESS_KEY_ID=...`).
- **Performance:** not a concern — the command reads one small bundled file,
  with no network, `kubectl` or AWS calls.

### Backward compatibility

No breaking changes: `example` is a new subcommand, and the existing kube
subcommands, their output and `~/.tingle/kube/config.json` are untouched. The
only change to existing text is the `--namespace` fix in `tingle --help kube`.

## Benefits

- A complete, copy-able walkthrough from empty config to an open shell, available offline from the terminal.
- Makes the alias/scope model (context -> namespace -> pod, and the active-scope rule) concrete, reducing misconfigurations.
- Introduces a shipped top-level `examples/` folder that other commands can reuse for their own walkthroughs.
