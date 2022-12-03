SHELL := /usr/bin/env bash
POSTGRES_PASSWORD = $(shell openssl rand -hex 32)
CLIENT_DIR := client
SERVER_DIR := server
DB_PASSWORD_FILE := .db_password
DB_BACKUP_FILE := database-backup.db
BACKEND_CONTAINER_NAME = $(shell docker-compose ps | grep backend | awk -F ' ' '{print $$1}')
DB_CONTAINER_NAME = $(shell docker-compose ps | grep db | awk -F ' ' '{print $$1}')
DB_VOLUME_NAME = $(shell docker inspect $(DB_CONTAINER_NAME) | jq -r '.[0].Mounts[] | select(.Type == "volume") | .Name')

export DOCKER_DEFAULT_PLATFORM := linux/amd64

install:
	@python3 -m pip install pipenv -U
	@python3 -m pipenv install --dev
	@python3 -m pipenv run pre-commit install
	@npm install --prefix $(CLIENT_DIR)

init-dev:
	@cd $(SERVER_DIR) && python3 -m pipenv run flask db upgrade
	@cd $(SERVER_DIR) && python3 -m pipenv run python -c "import app; tmpapp = app.create_app(); app.models.init_app(tmpapp)"

lock-requirements:
	@pipenv requirements > $(SERVER_DIR)/requirements.txt

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
	@echo $(POSTGRES_PASSWORD) > .db_password
else
	@echo "[-] Database password are already set"
endif

backup-database:
	@docker cp $(BACKEND_CONTAINER_NAME):/var/www/html/server/app.db $(DB_BACKUP_FILE) && echo "[!] A SQLite database was found inside the backend container. As mentionned in the release notes for XSS-Catcher v2.0.0, the local SQLite database in the backend container is no longer supported, and was replaced by a PostgreSQL database container. Your data was backed up to database-backup.db. If you want to import your backup to the new PostgreSQL, you can run 'make import-db'. Note that this will delete any potential content in the PostgreSQL database."

update: generate-secrets backup-database
	@docker-compose build
	@docker-compose up -d

start: generate-secrets
	@docker-compose up -d

stop:
	@docker-compose down

import-db:
ifneq ($(wildcard ./$(DB_BACKUP_FILE)),)
	@docker volume rm $(DB_VOLUME_NAME)
	@docker cp $(DB_BACKUP_FILE) $(BACKEND_CONTAINER_NAME):/var/www/html/server/$(DB_BACKUP_FILE)
	@docker exec $(BACKEND_CONTAINER_NAME) /var/www/html/server/db_engine_migrate.sh
endif
