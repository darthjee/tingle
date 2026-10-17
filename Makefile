.PHONY: tests rubycritic-image js-complexity-image php-complexity-image

tests:
	docker-compose run --rm tingle_tests pytest

rubycritic-image:
	docker build -t tingle_rubycritic:dev docker/rubycritic

js-complexity-image:
	docker build -t tingle_js_complexity:dev docker/js_complexity

php-complexity-image:
	docker build -t tingle_php_complexity:dev docker/php_complexity
