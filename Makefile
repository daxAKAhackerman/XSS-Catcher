SHELL := /usr/bin/env bash
SRC_SERVER_DIR := server
SRC_CLIENT_DIR := client
COLLECTOR_SCRIPT_DIR := collector_script
TEST_DIR := $(SRC_SERVER_DIR)/tests

.PHONY: build install lock-requirements lint test test-coverage-report run-backend build-collector-script build-frontend run-frontend run-database run-testing-database start stop init-dev

build:
	docker volume create xsscatcher-db
	docker build -t xsscatcher -f docker/Dockerfile .

install:
	python3 -m pip install pipenv -U
	python3 -m pipenv install --dev
	python3 -m pipenv run pre-commit install
	npm install --prefix $(SRC_CLIENT_DIR)
	npm install --prefix $(COLLECTOR_SCRIPT_DIR)

lock-requirements:
	pipenv requirements > $(SRC_SERVER_DIR)/requirements.txt

lint:
	python3 -m pipenv run black --line-length=160 $(SRC_SERVER_DIR)
	python3 -m pipenv run isort --profile black $(SRC_SERVER_DIR)
	npm run --prefix $(SRC_CLIENT_DIR) lint

test:
	FLASK_DEBUG=1 python3 -m pipenv run pytest $(TEST_DIR)

test-coverage-report:
	FLASK_DEBUG=1 python3 -m pipenv run pytest --cov-report term-missing --cov=$(SRC_SERVER_DIR) $(TEST_DIR)

run-backend:
	cd $(SRC_SERVER_DIR) && FLASK_DEBUG=1 python3 -m pipenv run flask run

build-collector-script:
	cd $(COLLECTOR_SCRIPT_DIR) && npx webpack

build-frontend:
	npm run --prefix $(SRC_CLIENT_DIR) build

run-frontend:
	npm run --prefix $(SRC_CLIENT_DIR) serve

run-database:
	docker run -p 5432:5432 -d -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres -e POSTGRES_USER=postgres --rm --name xsscatcher-dev-db postgres:14.12
	sleep 5
	cd $(SRC_SERVER_DIR) && FLASK_DEBUG=1 python3 -m pipenv run flask db upgrade
	cd $(SRC_SERVER_DIR) && FLASK_DEBUG=1 python3 -m pipenv run python -c "import app; tmpapp = app.create_app(); app.models.init_app(tmpapp)"

run-testing-database:
	docker run -p 5433:5432 -d -e POSTGRES_PASSWORD=testing -e POSTGRES_DB=testing -e POSTGRES_USER=testing --rm --name xsscatcher-testing-db postgres:14.12

start:
	docker run -p 8080:80 -v xsscatcher-db:/var/lib/postgresql/14/main/ -d --name xsscatcher xsscatcher

stop:
	docker stop xsscatcher
	docker rm xsscatcher
