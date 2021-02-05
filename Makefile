SHELL := /usr/bin/env bash
POSTGRES_USER = user
POSTGRES_DB = xss
POSTGRES_PASSWORD := $(shell cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)\n
CLIENT_DIR=client

install:
	@python3 -m pip install pipenv -U
	@pipenv install --dev
	@pipenv run pre-commit install

lint:
	@npm run --prefix $(CLIENT_DIR) lint
	@pipenv run black --line-length=160 server/app server/tests server/config.py server/xss.py
	@pipenv run isort --profile black server/app server/tests server/config.py server/xss.py

test:
	@pipenv run pytest server/tests

test-coverage-report:
	@pipenv run pytest -v --cov=app --cov-report html:cov_html server/tests

generate-secrets:
ifeq ($(wildcard ./.env),)
	@echo POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) >> .env
	@echo POSTGRES_USER=$(POSTGRES_USER) >> .env
	@echo POSTGRES_DB=$(POSTGRES_DB) >> .env
else
	@echo "[-] Docker environment variables are already set"
endif

deploy: generate-secrets
	@docker-compose build
	@docker-compose up -d

update:
	@docker-compose build
	@docker-compose up -d

start:
	@docker-compose up -d

stop:
	@docker-compose down
