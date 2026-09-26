# Fetch stage: verified kubectl and AWS CLI

Add a `fetch` builder stage before the final stage. It downloads and verifies the upstream tools, so `gnupg`, `unzip`, the zips and the extracted installer never reach the final image.

## `fetch` stage

```dockerfile
FROM ${BASE_IMAGE} AS fetch
ARG UBUNTU_SNAPSHOT
ARG TARGETARCH
ARG KUBECTL_VERSION=<x.y.z>
ARG AWS_CLI_VERSION=<2.x.y>
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
```

1. Install the stage's own pinned packages from the same snapshot: `ca-certificates`, `curl`, `unzip`, `gnupg` (or just `gpg`, if it's enough to import and verify). Clean the apt lists in the same `RUN`. DL3008 applies here too.
2. **kubectl:** download `https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl` and its `kubectl.sha256` with `curl -fsSL`, then run `echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check`. Put the binary at `/out/kubectl` with mode 0755.
3. **AWS CLI:**
   - Map the architecture: `amd64` → `x86_64` and `arm64` → `aarch64`. Fail on anything else.
   - Download `https://awscli.amazonaws.com/awscli-exe-linux-${aws_arch}-${AWS_CLI_VERSION}.zip` and its `.sig`.
   - Run `COPY shell/linux/aws-cli.asc /tmp/aws-cli.asc`, then `gpg --import` it into a throwaway `GNUPGHOME` and run `gpg --verify awscliv2.sig awscliv2.zip`.
   - Unzip, then run `./aws/install --install-dir /usr/local/aws-cli --bin-dir /out/bin`.
4. Any failed download or verification fails the build. `curl -f` and `set -e` via `RUN` semantics handle that; don't add `|| true`.
5. Don't hard-code `amd64` anywhere. `TARGETARCH` is set by buildx, and `dpkg --print-architecture` is an acceptable fallback when it's empty, for example with plain `docker build`.

## Final stage

After the apt layer and before `USER tingle`, copy the tools in as root:

```dockerfile
COPY --from=fetch /out/kubectl /usr/local/bin/kubectl
COPY --from=fetch /usr/local/aws-cli /usr/local/aws-cli
RUN ln -s /usr/local/aws-cli/v2/current/bin/aws /usr/local/bin/aws \
    && ln -s /usr/local/aws-cli/v2/current/bin/aws_completer /usr/local/bin/aws_completer
```

`COPY` of a directory keeps the internal `v2/current` symlink. Check that `aws --version` and `kubectl version --client` work as `tingle` on both platforms.

Keep the layer order: base → apt → upstream tools → user. That way bumping `KUBECTL_VERSION` or `AWS_CLI_VERSION` only rebuilds the last layers.

## Files to Change
- `shell/linux/Dockerfile` — new `fetch` stage with its `ARG`s, verified downloads and AWS install; final-stage `COPY --from=fetch` and the `aws` symlinks.
