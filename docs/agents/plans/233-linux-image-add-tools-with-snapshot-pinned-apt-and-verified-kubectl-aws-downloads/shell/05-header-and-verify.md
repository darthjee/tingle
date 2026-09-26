# Header comment and local verification

Rewrite the Dockerfile header comment for the new image:

- It's the toolbox image for `tingle linux`, grouped as in the issue (GNU baseline, git and friends, data and network, editing and search, archives and dev, terminal and processes, plus `kubectl` and `aws` from upstream).
- Reproducibility: a digest-pinned base, `UBUNTU_SNAPSHOT` apt pins, and `KUBECTL_VERSION` / `AWS_CLI_VERSION` `ARG`s verified by sha256 or PGP in the `fetch` stage. Point to `docs/agents/tingle-linux-image.md` for the bump procedure.
- Keep the existing notes: it runs as non-root uid 1000, and there's no `CMD`/`ENTRYPOINT`.

Then check the whole image locally on both platforms. Use emulation where needed, or build each platform on a native host:

- `docker buildx build --platform linux/<arch> --load -t tingle-dev:<arch> -f shell/linux/Dockerfile .` succeeds.
- Every command in the plan.md smoke-check table passes with `docker run --rm --network none --platform linux/<arch> tingle-dev:<arch> bash -c '<cmd>'`.
- `docker run --rm tingle-dev:<arch> sed --version` still reports GNU sed, and `id -u` is `1000`.
- `docker run --rm tingle-dev:<arch> bash -c 'command -v gpg gpg-agent'` finds nothing, and there's no `awscliv2.zip`, `/aws` or `kubectl.sha256` anywhere in the image.
- `tingle linux sed` behaves as before. Make sure `shell/linux/docker_run.sh` isn't touched.

Report the resolved snapshot date, base digest, tool versions and any smoke-check substitutions to the architect and product-owner.

## Files to Change
- `shell/linux/Dockerfile` — header comment.
