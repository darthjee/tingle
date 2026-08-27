# Add Makefile test target

Create a root-level `Makefile` with a single `tests` target, mirroring
`majora`'s `tests:` target naming (`docker-compose run $(PROJECT)_tests
/bin/bash` there runs an interactive shell; tingle's runs `pytest` directly
since there's nothing else to do inside the container):

```make
.PHONY: tests

tests:
	docker-compose run --rm tingle_tests pytest
```

Depends on the `tingle_tests` service from `docker-compose.yml` (previous
step).

## Files to Change

- `Makefile` — new file, single `tests` target as shown above.
