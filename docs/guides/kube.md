# `tingle kube`

Kubernetes (EKS) subcommand with a scoped alias layer.

## What it does

Working with an EKS cluster by hand usually means typing long context ARNs,
namespace names and generated pod names over and over: `kubectx` to pick a
cluster, `kubectl get pods -n ... | grep ...` to find a pod, then
`kubectl exec -n ... -it ... -- bash` to get into it.

`tingle kube` replaces those long names with short aliases that you define
once in a config file:

- **context aliases** stand for a real context name or ARN (for example
  `prod` for `arn:aws:eks:us-east-1:123456789012:cluster/prod`);
- **namespace aliases** stand for a real namespace, and belong to one
  context alias;
- **pod aliases** describe how to recognise a pod by its name (a fixed
  prefix plus a generated ID), and also belong to one context alias.

With the aliases in place you can switch clusters, list namespaces and pods,
and open a shell in a pod with short commands such as
`tingle kube shell web api`. Before touching the cluster, kube checks that
your AWS credentials work, so you get a clear message instead of a confusing
`kubectl` error.

## Prerequisites

These tools must be installed and on your `PATH`:

- the `aws` CLI (used to check your AWS credentials);
- `kubectx` (used to switch contexts);
- `kubectl` (used to read the current context, list namespaces and pods,
  and open shells).

Your kubeconfig must already contain the EKS contexts you want to use (for
example, added with `aws eks update-kubeconfig`). kube does not create
contexts; it only switches between them.

## Usage

```
tingle kube switch <context_alias>
tingle kube list [--json] namespace
tingle kube list [--json] pods --namespace <namespace_alias>
tingle kube shell <namespace_alias> <pod_alias>
tingle kube configure context
tingle kube configure namespace
tingle kube configure pod
```

Note the argument order for `list`: `--json` goes right after `list`, before
`namespace` or `pods`, and `pods` always needs `--namespace <alias>`.

Examples:

```
tingle kube switch prod
tingle kube list namespace
tingle kube list --json namespace
tingle kube list pods --namespace web
tingle kube list --json pods --namespace web
tingle kube shell web api
tingle kube configure context
```

If you enabled bash completion with `tingle install`, pressing Tab completes
subcommands, `list`/`configure` targets and your configured aliases.

## The config file

kube stores its aliases in:

```
~/.tingle/kube/config.json
```

You can edit it by hand or let `tingle kube configure` manage it for you
(see [`tingle kube configure`](#tingle-kube-configure)). A complete example:

```
{
  "version": 1,
  "aws_profile": "work",
  "pod_id_pattern": "^[a-z0-9]{10}$",
  "shell": "bash",
  "contexts": {
    "prod": "arn:aws:eks:us-east-1:123456789012:cluster/prod",
    "stg": "arn:aws:eks:us-east-1:123456789012:cluster/staging"
  },
  "namespaces": {
    "prod": {
      "web": "web-frontend",
      "jobs": "background-jobs"
    }
  },
  "pods": {
    "prod": {
      "api": {
        "prefix": "api-server-",
        "id_pattern": "^[a-z0-9]{9,10}-[a-z0-9]{5}$",
        "namespace": "web"
      },
      "worker": {
        "prefix": "worker-"
      }
    }
  }
}
```

### Top-level keys

| Key              | Required | Default          | Meaning                                                  |
|------------------|----------|------------------|----------------------------------------------------------|
| `version`        | yes      | —                | Config schema version. A new config is written with `1`. |
| `aws_profile`    | no       | `default`        | AWS CLI profile used for the credential check.           |
| `pod_id_pattern` | no       | `^[a-z0-9]{10}$` | Default regex for the generated part of pod names.       |
| `shell`          | no       | `bash`           | Program run by `tingle kube shell` inside the pod.       |
| `contexts`       | no       | `{}`             | Context aliases.                                         |
| `namespaces`     | no       | `{}`             | Namespace aliases, grouped by context alias.             |
| `pods`           | no       | `{}`             | Pod aliases, grouped by context alias.                   |

Defaults are applied in memory only: kube never writes them into your file.

### The alias blocks

- `contexts` maps an alias to a real context name or ARN, exactly as it
  appears in `kubectl config get-contexts`.
- `namespaces` maps a **context alias** to an object that maps namespace
  aliases to real namespace names.
- `pods` maps a **context alias** to an object that maps pod aliases to a
  pod rule. Each rule is an object with:
  - `prefix` (required): the fixed start of the pod name, for example
    `api-server-`;
  - `id_pattern` (optional): a regex for the rest of the name; when absent,
    the top-level `pod_id_pattern` is used;
  - `namespace` (optional): the **namespace alias** this pod lives in. It is
    used to filter `list pods` and to warn you in `shell` when you ask for
    the pod in a different namespace.

### Active scope

Namespace and pod aliases only apply to the cluster you are currently on.
kube finds this "active scope" by running `kubectl config current-context`
and looking for the context alias whose real name matches it. If no context
alias matches (for example, you switched with plain `kubectx` to a context
you never aliased), there is no active scope and namespace and pod aliases
are not resolved.

### How pod aliases match pods

Pods created by Deployments get generated names such as
`api-server-7d9f8c6b5d-x2k4q`. A pod alias matches a pod when:

1. the pod name starts with the alias's `prefix`, and
2. the rest of the name (after the prefix) fully matches the alias's
   `id_pattern`, or `pod_id_pattern` if the alias has none.

Matching pods are ordered by creation time, oldest first. With the example
config above, `api` matches `api-server-7d9f8c6b5d-x2k4q`, while `worker`
matches names like `worker-a1b2c3d4e5` (ten lowercase letters or digits after
the prefix).

## When the config is missing or invalid

- **Missing file:** the first time you run a kube subcommand, kube creates
  `~/.tingle/kube/config.json` (and its folders) containing just
  `{"version": 1}`, and prints:

  ```
  kube: created new config at /home/you/.tingle/kube/config.json
  ```

- **Unreadable, invalid JSON, or wrong shape** (for example, no `version`
  key, `contexts` not being an object, or a pod rule without `prefix`):
  kube prints a notice such as

  ```
  kube: invalid JSON in config at /home/you/.tingle/kube/config.json: <details> — falling back to pass-through mode.
  ```

  and carries on in **pass-through mode**: no aliases are loaded, every
  name you type is used as-is (a real context, namespace or pod name), and
  the defaults (`aws_profile: default`, `shell: bash`, and so on) are used.

In pass-through mode `tingle kube configure` cannot save anything, because
the broken file is never overwritten. Fix the file by hand, or delete it so
kube creates a fresh one, then run `configure` again.

## AWS credentials

Before `switch`, `list` and `shell` touch the cluster, kube runs
`aws sts get-caller-identity` to make sure your AWS credentials work.
`configure` never contacts AWS or the cluster, so it skips this check.

kube picks the credential source from your environment:

- **Profile mode (default).** When neither `AWS_ACCESS_KEY_ID` nor
  `AWS_SECRET_ACCESS_KEY` is set, kube checks the profile named by
  `aws_profile` in the config (`default` if absent), using
  `aws sts get-caller-identity --profile <aws_profile>`.

- **Environment mode.** When both `AWS_ACCESS_KEY_ID` and
  `AWS_SECRET_ACCESS_KEY` are exported (and not empty), the AWS CLI uses
  them directly and `aws_profile` is ignored. kube prints:

  ```
  kube: using AWS credentials from environment (aws_profile ignored)
  ```

  `AWS_SESSION_TOKEN`, if you use temporary credentials, is passed along to
  the AWS CLI as usual, but it does not affect which mode is chosen.

- **Partial credentials.** When only one of the two variables is set, kube
  warns and falls back to profile mode:

  ```
  kube: warning: incomplete AWS environment credentials (need both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY); falling back to profile '<aws_profile>'
  ```

If the check fails, kube stops before running any `kubectx` or `kubectl`
command and prints the AWS CLI's error:

```
kube switch: AWS credential check failed for profile 'work': <aws error>
kube list: AWS credential check failed for environment credentials: <aws error>
```

## `tingle kube switch`

```
tingle kube switch <context_alias>
```

Switches your current Kubernetes context:

1. Looks up `<context_alias>` in `contexts`. If it is not there, kube
   prints a notice and uses the name as a real context name:

   ```
   kube: 'my-ctx' not found in configured contexts — using it as-is.
   ```

2. Runs the AWS credential check.
3. Runs `kubectx <real name>`, then confirms with
   `kubectl config current-context` that the switch took effect.

On success it prints:

```
kube switch: now using context 'prod' (arn:aws:eks:us-east-1:123456789012:cluster/prod)
```

On failure it prints the reason followed by the contexts you can use: your
configured context aliases, or, if you have none, the context names from
`kubectl config get-contexts -o name`:

```
kube switch: failed to switch to 'prdo': <kubectx error>
kube switch: available contexts:
  - prod
  - stg
```

## `tingle kube list`

### Listing namespaces

```
tingle kube list [--json] namespace
```

Lists every namespace in the current cluster (`kubectl get namespaces`).
Namespaces that have an alias in the active scope are shown as
`alias -> name`; the rest are shown by name only:

```
default
jobs -> background-jobs
kube-system
web -> web-frontend
```

With `--json`, the output is a JSON array; `alias` is `null` for namespaces
without an alias:

```
[
  {
    "alias": null,
    "name": "default"
  },
  {
    "alias": "web",
    "name": "web-frontend"
  }
]
```

### Listing pods

```
tingle kube list [--json] pods --namespace <namespace_alias>
```

Resolves `<namespace_alias>` in the active scope (if it is not configured,
kube prints a `not found in configured namespaces — using it as-is.` notice
and uses it as a real namespace name), lists the pods in that namespace, and
groups them under your pod aliases.

Only the pod aliases of the active scope are shown, and only those whose
`namespace` is either unset or equal to the `<namespace_alias>` you passed.
Pods that match no alias are not listed. If the active scope has no pod
aliases, nothing is printed.

```
api:
  - api-server-7d9f8c6b5d-x2k4q
  - api-server-7d9f8c6b5d-p9m3z
worker:
  kube list: candidates discarded by id_pattern for 'worker':
    - worker-debug
```

When an alias matches nothing but some pods start with its `prefix`, those
pods are listed as "candidates discarded by id_pattern", which helps you
fix a pattern that is too strict.

With `--json`, the output is a JSON array with one entry per alias (the
discarded candidates are not included):

```
[
  {
    "alias": "api",
    "pods": [
      "api-server-7d9f8c6b5d-x2k4q",
      "api-server-7d9f8c6b5d-p9m3z"
    ]
  },
  {
    "alias": "worker",
    "pods": []
  }
]
```

## `tingle kube shell`

```
tingle kube shell <namespace_alias> <pod_alias>
```

Opens an interactive shell inside a pod:

1. Runs the AWS credential check.
2. Resolves `<namespace_alias>` in the active scope (unknown aliases are
   used as-is, with a notice).
3. Resolves `<pod_alias>`:
   - If it is not a pod alias in the active scope, kube prints
     `kube: 'my-pod' not found in configured pods — using it as-is.` and
     treats it as the exact pod name.
   - If the alias has a `namespace` that differs from the
     `<namespace_alias>` you passed, kube warns but continues with the
     namespace you passed.
   - kube lists the pods in the namespace and applies the alias's matching
     rule. One match is used directly. Several matches show a numbered
     list, oldest first:

     ```
     1) api-server-7d9f8c6b5d-x2k4q
     2) api-server-7d9f8c6b5d-p9m3z
     Select a pod:
     ```

     Type a number and press Enter. Pressing Enter on an empty line cancels
     with `kube shell: no pod selected`.
   - No matches print `kube shell: no pods matched alias '<alias>' in
     '<namespace>'`, followed by any candidates discarded by the
     `id_pattern`.
4. If the pod is not in the `Running` phase, kube warns
   (`kube shell: warning — pod '<name>' is not in Running phase`) but still
   tries to connect.
5. Runs `kubectl exec -n <namespace> -it <pod> -- <shell>`, where `<shell>`
   is the config's `shell` value (`bash` by default). Your terminal is
   attached to the session; type `exit` to leave.

If your containers do not have `bash`, set `"shell": "sh"` in the config.

## `tingle kube configure`

```
tingle kube configure context
tingle kube configure namespace
tingle kube configure pod
```

Interactive prompts to create, edit or remove aliases. `configure` only
edits the config file: it never runs `aws`, `kubectx` or `kubectl`.

### The action menu

Each flow shows what is already configured and then asks:

```
What would you like to do?
1) create
2) edit
3) remove
Select an action:
```

At any menu or required prompt, pressing Enter on an empty line aborts
without saving:

```
kube configure: aborted, nothing saved.
```

Menus reprompt when you type something that is not a valid number.

### Configuring contexts

`tingle kube configure context` lists your context aliases, then:

- **create** asks for `Alias` and `Real context name/ARN`.
- **edit** lets you pick an existing alias by number, then asks for the
  same two values with the current ones shown in brackets; press Enter to
  keep a value.
- **remove** lets you pick an alias by number. If that context has
  namespace or pod aliases, kube lists what will be dropped along with it
  and asks for confirmation:

  ```
  Removing context alias 'prod' will also drop:
    - namespaces.prod (2 entrie(s))
    - pods.prod (2 entrie(s))
  Confirm removal? [y/N]:
  ```

  Only `y` or `yes` confirms; anything else aborts.

### Configuring namespaces and pods

Namespace and pod aliases live inside a context alias, so
`tingle kube configure namespace` and `tingle kube configure pod` first ask
you to pick the context alias (the scope) they belong to. If you have no
context aliases yet, they tell you to run `kube configure context` first.

After picking the scope, the flow shows that scope's aliases and the same
create/edit/remove menu.

- **Namespace create/edit** asks for `Alias` and `Real namespace name`.
- **Pod create/edit** asks for:
  - `Alias`;
  - `prefix` (required);
  - `id_pattern (optional, regex)`: leave empty to use `pod_id_pattern`;
    an invalid regex is rejected and asked again;
  - `namespace alias (optional)`: the namespace aliases of the scope are
    listed as a reminder; leave empty for none.
- **Remove** lets you pick an alias by number and removes just that alias.

### Saving

Every change is validated against the config schema before it is written.
If validation fails, the file is left untouched:

```
kube configure: config missing required key(s): version — nothing saved.
```

Writes are atomic (a temporary file replaces the config in one step), so an
interrupted session never leaves a half-written file. On success kube
prints a confirmation such as
`kube configure: context alias 'prod' saved.` or
`kube configure: pod alias 'api' saved under 'prod'.`

When editing, typing a **different** alias name creates a new alias with
that name; the original alias is kept. To rename an alias, create the new
one and then remove the old one.

## From kubectx/kubectl to kube

If you already work with `kubectx` and `kubectl`, here is how each manual
step maps to kube. The one-time setup is running `tingle kube configure`
for your contexts, namespaces and pods.

1. **Export your AWS credentials.** Nothing changes here:

   ```
   export AWS_ACCESS_KEY_ID=...
   export AWS_SECRET_ACCESS_KEY=...
   ```

   kube detects them, ignores `aws_profile`, and verifies them before every
   `switch`, `list` and `shell`. Without them, kube uses `aws_profile`.

2. **`kubectx` (list contexts).** Run `tingle kube configure context` once
   to give the contexts you use short aliases; the flow lists the aliases
   you already have. `tingle kube switch` also lists the available contexts
   when a switch fails.

3. **`kubectx <ctx>` (switch context):**

   ```
   tingle kube switch prod
   ```

4. **`kubectl get ns`:**

   ```
   tingle kube list namespace
   ```

   Namespaces you aliased are shown as `alias -> name`.

5. **`kubectl get pods -n $NAMESPACE | grep <name>`:**

   ```
   tingle kube list pods --namespace web
   ```

   The pod alias's prefix and ID pattern do the filtering that `grep` did.

6. **`kubectl exec -n $NAMESPACE -it $POD -- bash`:**

   ```
   tingle kube shell web api
   ```

   No need to copy the generated pod name: kube finds it, and asks you to
   pick one if there are several.

## Errors

- Missing or unknown arguments are reported by the argument parser, which
  prints a usage line and an error to standard error, for example:

  ```
  usage: kube list pods [-h] --namespace NAMESPACE
  kube list pods: error: the following arguments are required: --namespace
  ```

  Putting `--json` after `pods` or `namespace` gives:

  ```
  kube: error: unrecognized arguments: --json
  ```

- A failed AWS credential check stops the command:

  ```
  kube <command>: AWS credential check failed for profile '<aws_profile>': <aws error>
  ```

- A namespace or pod name that is not a valid Kubernetes name (lowercase
  letters, digits and `-`) is rejected before `kubectl` runs:

  ```
  invalid namespace: 'Web_Frontend'
  ```

- A `kubectl` failure (for example, a namespace or pod that does not exist)
  prints the error from `kubectl` itself.

- If the shell session cannot be opened or ends with an error:

  ```
  kubectl exec exited with status <code>
  ```

## Quick help

For a short summary of the command, run:

```
tingle --help kube
```
