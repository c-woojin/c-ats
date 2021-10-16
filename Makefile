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