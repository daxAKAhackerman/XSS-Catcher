SHELL := /usr/bin/env bash
POSTGRES_PASSWORD := $(shell cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)\n
CLIENT_DIR=client
DB_PASSWORD_FILE=.db_password

install:
	@python3 -m pip install pipenv -U
	@pipenv install --dev
	@pipenv run pre-commit install
	@npm install --prefix $(CLIENT_DIR)

lint:
	@npm run --prefix $(CLIENT_DIR) lint
	@pipenv run black --line-length=160 server/app server/tests server/config.py server/xss.py
	@pipenv run isort --profile black server/app server/tests server/config.py server/xss.py

test:
	@pipenv run pytest server/tests

test-coverage-report:
	@pipenv run pytest -v --cov=app --cov-report html:cov_html server/tests

run-web-app:
	@npm --prefix client run serve

run-backend-server: lint
	@cd server && FLASK_ENV=development pipenv run flask run

generate-secrets:
ifeq ($(wildcard ./$(DB_PASSWORD_FILE)),)
ifneq ($(wildcard ./.env),)
	@grep POSTGRES_PASSWORD .env | awk -F '=' '{print $2}' > $(DB_PASSWORD_FILE)
else
	@echo $(POSTGRES_PASSWORD) > .db_password
endif
else
	@echo "[-] Database password are already set"
endif

update: generate-secrets
	@docker-compose build
	@docker-compose up -d

start: generate-secrets
	@docker-compose up -d

stop:
	@docker-compose down
