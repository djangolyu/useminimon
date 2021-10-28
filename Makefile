.PHONY: all
all: style-check type-check test

.PHONY: clean
clean: clean-pycache clean-generated clean-testfiles clean-mypyfiles

.PHONY: clean-pycache
clean-pycache:
	find . -name __pycache__ -exec rm -rf {} +

.PHONY: clean-generated
clean-generated:
	find . -name '.DS_Store' -exec rm -f {} +
	rm -rf src/*.egg-info/
	rm -rf dist/

.PHONY: clean-testfiles
clean-testfiles:
	rm -rf .cache/
	rm -rf .pytest_cache/
	rm -f .coverage .junit.xml

.PHONY: clean-mypyfiles
clean-mypyfiles:
	find . -name '.mypy_cache' -exec rm -rf {} +

.PHONY: style-check
style-check:
	@pipenv run flake8

.PHONY: type-check
type-check:
	@pipenv run mypy src

.PHONY: test
test:
	@pipenv run python -X dev -m pytest -v $(TEST)

.PHONY: covertest
covertest:
	@pipenv run python -X dev -m pytest -v --cov=src \
		--cov-report term-missing \
		--junitxml=.junit.xml \
		$(TEST)

.PHONY: build
build:
	@pipenv run python -m build
