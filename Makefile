.PHONY: run build

down:
	docker-compose down

build:
	docker-compose build

up: build
	docker-compose up

test: build
	docker-compose up -d test
	sleep 6 # This should be function to wait for `airflow initdb` to complete before continuing
	docker-compose run test bash -c "py.test -s -v tests"

test-shell: build
	docker-compose up -d test
	docker-compose exec test bash

lint: build
	docker-compose run test bash -c "flake8 --max-line-length=120 dags tests tasks"
