SHELL := /usr/bin/env bash
SRC_SERVER_DIR := server
SRC_CLIENT_DIR := client
COLLECTOR_SCRIPT_DIR := collector_script
TEST_DIR := $(SRC_SERVER_DIR)/tests

.PHONY: build start stop install lock-requirements lint test test-coverage-report run-backend build-frontend run-frontend

build:
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

build-frontend:
	npm run --prefix $(SRC_CLIENT_DIR) build

run-frontend:
	npm run --prefix $(SRC_CLIENT_DIR) serve

start:
	docker run -p 8080:80 -d --name xsscatcher xsscatcher

stop:
	docker stop xsscatcher
	docker rm xsscatcher

init-dev:
	cd $(SRC_SERVER_DIR) && FLASK_DEBUG=1 python3 -m pipenv run flask db upgrade
	cd $(SRC_SERVER_DIR) && FLASK_DEBUG=1 python3 -m pipenv run python -c "import app; tmpapp = app.create_app(); app.models.init_app(tmpapp)"

build-collector-script:
	cd $(COLLECTOR_SCRIPT_DIR) && npx webpack
