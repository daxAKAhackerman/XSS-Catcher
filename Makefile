SHELL := /usr/bin/env bash
POSTGRES_USER = user
POSTGRES_DB = xss
POSTGRES_PASSWORD := $(shell cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)\n

generate-secrets:
	@echo POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) >> .env
	@echo POSTGRES_USER=$(POSTGRES_USER) >> .env
	@echo POSTGRES_DB=$(POSTGRES_DB) >> .env

update:
	@docker-compose build
	@docker-compose up -d

deploy: generate-secrets
	@docker-compose build
	@docker-compose up -d

start: 
	@docker-compose up -d

stop: 
	@docker-compose down
