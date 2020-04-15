.DEFAULT_GOAL:=start

.EXPORT_ALL_VARIABLES:
COMPOSE_PROJECT_NAME = n3robot

include .env
export

.PHONY: build/images
build/images:
	@docker build  --tag n3robot-base:latest --file .cicd/dockerfiles/10-base.Dockerfile .
	@docker build --build-arg TELEGRAM_BOT_TOKEN_ARG="$(TELEGRAM_BOT_TOKEN)" \
			--build-arg MONGODB_PASSWORD_ARG="$(MONGODB_PASSWORD)" \
			--tag n3robot:latest -f .cicd/dockerfiles/15-app.Dockerfile .

.PHONY: start
start: build/images
	@mkdir -p data/db
	docker-compose --file .cicd/docker-compose.yml up

.PHONY: help
help:
	@echo "help"
