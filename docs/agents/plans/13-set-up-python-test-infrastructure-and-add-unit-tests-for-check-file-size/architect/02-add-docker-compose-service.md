# Add docker-compose service

Create a root-level `docker-compose.yml` with a single `tingle_tests`
service, mirroring the naming idiom of `majora`'s `*_tests` service without
its base/dev image split (tingle has no app server or database to justify
that split — see `plan.md` Notes).

```yaml
services:
  tingle_tests:
    build:
      context: .
      dockerfile: python/Dockerfile
    volumes:
      - ./python:/app
```

Depends on `python/Dockerfile` existing (see `python.md`) — this file only
references it by path, no other coupling.

**Watch for**: the bind-mounted `./python:/app` volume can shadow the
image's `/app` ownership set up in `python/Dockerfile` (host-owned files
mounted into a container running as a non-root user). If `docker-compose run
--rm tingle_tests pytest` hits permission errors writing `coverage.xml`,
this is the first place to check — it may need a writable coverage output
path outside the mounted tree, or a matching UID between host and container
user.

## Files to Change

- `docker-compose.yml` — new file, single `tingle_tests` service as shown
  above.
