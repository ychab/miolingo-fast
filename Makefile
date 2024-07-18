.DEFAULT_GOAL := help
.PHONY: help
.EXPORT_ALL_VARIABLES:

CURRENT_MAKEFILE := $(lastword $(MAKEFILE_LIST))

include .env

help:
	@LC_ALL=C $(MAKE) -pRrq -f $(CURRENT_MAKEFILE) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

confirm:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]

################
# Local command
################

run:
	uvicorn miolingo.main:app

deps:
	poetry show --outdated

poetry:
	poetry update
	poetry lock
	poetry export -f requirements.txt --with prod -o requirements/prod.txt
	poetry export -f requirements.txt --with test -o requirements/test.txt
	poetry export -f requirements.txt --with test,dev -o requirements/dev.txt

precommit:
	pre-commit autoupdate

#########
# Alembic
#########

db_upgrade:
	alembic upgrade head

db_downgrade:
	alembic downgrade base

db_revision:
	alembic revision --autogenerate

################
# Docker command
################

ps:
	docker compose ps --all

up:
	docker compose up -d

up_wait:
	docker compose up --detach --wait

down:
	docker compose down --remove-orphans

down_clean:
	docker compose down --volumes --remove-orphans --rmi local

restart:
	docker compose restart

prune: confirm
	@# Be CAREFUL, would removed ALL unused stuff on your local machine!
	@# Be sure to have all your compose services RUNNING before executing it!
	docker system prune --all --force --volumes

reload: down up
reset: down_clean up

##############
# Docker utils
##############

dbshell:
	docker compose exec postgres psql -U ${MIOLINGO_POSTGRES_USER} -d ${MIOLINGO_POSTGRES_DB}
