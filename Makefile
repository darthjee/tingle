.PHONY: tests

tests:
	docker-compose run --rm tingle_tests pytest
