SHELL := /usr/bin/env bash
POSTGRES_PASSWORD := $(shell cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)\n
CLIENT_DIR=client
SERVER_DIR=server
DB_PASSWORD_FILE=.db_password

install:
	@python3 -m pip install pipenv -U
	@python3 -m pipenv install --dev
	@python3 -m pipenv run pre-commit install
	@npm install --prefix $(CLIENT_DIR)

init-dev:
	@cd $(SERVER_DIR) && python3 -m pipenv run flask db upgrade
	@cd $(SERVER_DIR) && python3 -m pipenv run python -c "import app; tmpapp = app.create_app(); app.models.init_app(tmpapp)"

lint:
	@npm run --prefix $(CLIENT_DIR) lint
	@python3 -m pipenv run black --line-length=160 $(SERVER_DIR)
	@python3 -m pipenv run isort --profile black $(SERVER_DIR)

test:
	@python3 -m pipenv run pytest $(SERVER_DIR)/tests

test-coverage-report:
	@python3 -m pipenv run pytest -v --cov=app --cov=config --cov-report html:cov_html $(SERVER_DIR)/tests

run-web-app:
	@npm --prefix client run serve

run-backend-server: lint
	@cd $(SERVER_DIR) && FLASK_DEBUG=1 pipenv run flask run

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

backup-database:
	@echo $(shell docker-compose ps | grep backend | awk -F ' ' '{print $1}')
	@docker cp $(shell docker-compose ps | grep backend | awk -F ' ' '{print $1}'):/var/www/html/server/app.db database-backup.db && echo "[!] A SQLite database was found inside the backend container. As mentionned in the release notes for XSS-Catcher v2.0.0, the local SQLite database in the backend container is no longer supported, and was replaced by a PostgreSQL database container. Your data was backed up to database-backup.db, but will not be migrated automatically. "

update: generate-secrets
	@docker-compose build
	@docker-compose up -d

start: generate-secrets
	@docker-compose up -d

stop:
	@docker-compose down

lock-requirements:
	@pipenv requirements > $(SERVER_DIR)/requirements.txt
