export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test

build:
	docker-compose build

up:
	docker-compose up -d app

down:
	docker-compose down --remove-orphans

logs:
	docker-compose logs app | tail -100

install:
	pip install -r requirements.txt

test: up
	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/unit /tests/integration /tests/e2e

black:
	black -l 86 $$(find * -name '*.py')

flake:
	flake8 .

mypy:
	mypy .

