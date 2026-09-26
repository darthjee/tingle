# Add the AWS CLI public key

Store AWS's published PGP public key for the AWS CLI v2 installer in the repo, so the build doesn't fetch trust material at build time.

- Copy the key block exactly as it appears on the official AWS CLI install page ("Verify the integrity and authenticity of the downloaded zip file") into `shell/linux/aws-cli.asc`.
- Check its fingerprint with `gpg --show-keys --with-fingerprint shell/linux/aws-cli.asc` and compare it with the fingerprint on that page (currently `FB5D B77F D5C1 18B8 0511 ADA8 A631 0ACC 4672 475C`). Record the fingerprint and key expiry in a Dockerfile comment next to the `COPY`.
- If the published key has expired, `gpg --verify` still verifies the signature but warns. Treat a `BAD signature` or an unknown key as a failure, not an expiry warning. Rotating the key is part of the documented bump procedure.

## Files to Change
- `shell/linux/aws-cli.asc` — new file: the AWS CLI v2 PGP public key (ASCII-armoured).
