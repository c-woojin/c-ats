export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

install:
	pip install -r requirements.txt

test:
	pytest --tb=short

black:
	black -l 86 $$(find * -name '*.py')

flake:
	flake8 .

mypy:
	mypy .

build:
	docker-compose build

up:
	docker-compose up -d app

down:
	docker-compose down

logs:
	docker-compose logs app | tail -100