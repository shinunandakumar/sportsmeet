.PHONY: help env build up down restart logs ps migrate makemigrations superuser shell django-check

help:
	@echo "Targets:"
	@echo "  make env            Copy .env.example -> .env (if missing)"
	@echo "  make build          docker compose build"
	@echo "  make up             docker compose up"
	@echo "  make down           docker compose down"
	@echo "  make restart        down + up"
	@echo "  make logs           docker compose logs -f"
	@echo "  make ps             docker compose ps"
	@echo "  make migrate        Run Django migrations"
	@echo "  make makemigrations Create Django migrations"
	@echo "  make superuser      Create Django superuser"
	@echo "  make shell          Django shell"
	@echo "  make django-check   Django system check"

env:
	@test -f .env || cp .env.example .env

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart: down up

logs:
	docker compose logs -f

ps:
	docker compose ps

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

superuser:
	docker compose exec web python manage.py createsuperuser

shell:
	docker compose exec web python manage.py shell

django-check:
	docker compose exec web python manage.py check
