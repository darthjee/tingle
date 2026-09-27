# Verify by hand
There is no shell test framework. Put a `docker` stub on `PATH` that prints its arguments, and that answers `docker info` with `Docker Desktop` or something else depending on an env var. Then check:
- present and missing `~/.gitconfig`, `~/.config/git`, `~/.ssh/known_hosts`, `~/.ssh/config`, `~/.aws`, kubeconfig (use a temporary `HOME`);
- set, unset and empty `AWS_*` variables, and that no value ever appears in the arguments;
- `KUBECONFIG=/missing:/present:/other` mounts `/present` only;
- Docker Desktop detected vs not; `SSH_AUTH_SOCK` unset, set to a regular file, and set to a socket; Linux vs macOS (`uname`);
- `--isolated` and `TINGLE_LINUX_ISOLATED=1`: no `docker info` call, only the base arguments, and the banner ends with `(isolated)`;
- an unknown option exits 1;
- a `HOME` and working directory containing spaces;
- the banner goes to stderr for `shell` only (`tingle linux sed` output is byte-identical);
- `main.sh complete shell ''` prints `--isolated`.

End to end, with the rebuilt `0.0.3` image: `git clone` over ssh (agent) and over https (no `osxkeychain` errors), `kubectl config use-context` persists to the host, and `aws sts get-caller-identity` works with env credentials and with a profile or SSO.

## Files to Change
- None (verification only).
