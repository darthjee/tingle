# Add non-root test Dockerfile

Create `python/Dockerfile` — a single-stage image, no base/dev split (see
`plan.md` Notes for why that split doesn't apply here). Must run as a
non-root user: `python:3.11-slim` runs as root by default, and several
planned tests (steps 06/08 — `FileAnalyzer.count_lines`,
`SkipChecks.is_binary_file`) `chmod 000` a file expecting a permission
error; root ignores file-mode bits entirely, so a root container would make
those tests silently pass without exercising the code path.

```dockerfile
FROM python:3.11-slim

RUN useradd --create-home --uid 1000 tingle
WORKDIR /app

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
RUN chown -R tingle:tingle /app
USER tingle

CMD ["pytest"]
```

This is what `architect`'s `docker-compose.yml` builds from
(`dockerfile: python/Dockerfile`) — see that file's step for the
volume-mount/ownership caveat this Dockerfile's `chown` doesn't fully solve
on its own.

## Files to Change

- `python/Dockerfile` — new file, non-root single-stage image as shown
  above.
