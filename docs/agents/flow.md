# Flow

## Overview

_Describe the main runtime flow of the application here._

## kube AWS credential pre-check

`tingle kube switch`, `tingle kube list` (`namespace` and `pods`) and
`tingle kube shell` run an AWS credential pre-check before they touch the
cluster. `kube configure` does not. The executor (`python/kube/executor.py`)
runs the check through `python/kube/auth.py` (see
[architecture.md](architecture.md#kube-aws-credentials)):

1. **Detect the source.** `detect_credential_source()` checks
   `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` and returns `"env"`,
   `"partial"` or `"profile"`. `AWS_SESSION_TOKEN` is ignored here.
2. **Print a notice or warning** (nothing is printed for `"profile"`):
   - `"env"`:
     ```
     kube: using AWS credentials from environment (aws_profile ignored)
     ```
   - `"partial"`:
     ```
     kube: warning: incomplete AWS environment credentials (need both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY); falling back to profile '<aws_profile>'
     ```
3. **Run `aws sts get-caller-identity`:**
   - `"env"`: calls `check_aws_credentials(None)`, so the command runs
     without `--profile` and the AWS CLI reads the exported credentials.
   - `"partial"` / `"profile"`: calls `check_aws_credentials(aws_profile)`,
     so the command runs with `--profile <aws_profile>`. `aws_profile`
     comes from kube's config and defaults to `"default"`.
4. **Abort on failure.** If the check fails, the command prints an error
   that names the credential source, then stops:
   - env: `kube <cmd>: AWS credential check failed for environment credentials: <error>`
   - partial/profile: `kube <cmd>: AWS credential check failed for profile '<aws_profile>': <error>`

   `<cmd>` is the subcommand (`switch`, `list`, `shell`). On success the
   command goes on to its normal work (switch context, list resources, or
   exec into a pod).

### Caveat: kubeconfig exec plugins

The pre-check only covers kube's own `sts` call. The later `kubectl` calls
get their EKS tokens from the kubeconfig's exec plugin (usually
`aws eks get-token`). If that plugin's `args` contain `--profile <name>`, the
AWS CLI uses that profile, and the environment credentials are ignored for
the cluster calls, even when the pre-check used them. To use environment
credentials all the way through, remove `--profile` from the exec plugin
`args`.
