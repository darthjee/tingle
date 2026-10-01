.PHONY: tests rubycritic-image

tests:
	docker-compose run --rm tingle_tests pytest

rubycritic-image:
	docker build -t tingle_rubycritic:dev docker/rubycritic
