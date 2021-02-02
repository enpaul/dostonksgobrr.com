# tox-poetry-installer makefile

VERSION  = $(shell cat pyproject.toml | grep "^version =" | cut -d "\"" -f 2)

.PHONY: help
# Put it first so that "make" without argument is like "make help"
# Adapted from:
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## List Makefile targets
	$(info Makefile documentation)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

clean-tox:
	rm --recursive --force ./.mypy_cache
	rm --recursive --force ./.tox
	rm --recursive --force tests/__pycache__/
	rm --recursive --force .pytest_cache/
	rm --force .coverage

clean-py:
	rm --recursive --force ./dist
	rm --recursive --force ./build
	rm --recursive --force ./*.egg-info
	rm --recursive --force ./**/__pycache__/

clean: clean-tox clean-py; ## Clean temp build/cache files and directories

wheel: ## Build Python binary distribution wheel package
	poetry build --format wheel

source: ## Build Python source distribution package
	poetry build --format sdist

test: ## Run the project testsuite(s)
	poetry run tox --recreate

dev: ## Create the local dev environment
	poetry install
	poetry run pre-commit install

image:  ## Build the docker image
	docker build . --tag dostonksgobrr:$(VERSION)

latest: test image  ## Build the docker image and tag as latest
	docker tag dostonksgobrr:$(VERSION) dostonksgobrr:latest

run: dev  # Run the debug server locally
	poetry run python -m dostonksgobrr -d
