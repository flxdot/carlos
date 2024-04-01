# Do not edit! This file was generated via the /lib/py_monorepo_manager
# Any manual changes to this file will eventually be overwritten by CI

default: format

all:
	make format
	make ruff
	make mypy
	make pytest
	make coverage

format:
	poetry run ruff check carlos --fix-only
	poetry run black .
	poetry run isort . --profile=black

pytest:
	# we run coverage instead of pytest directly to get the coverage of
	# the pytest plugins as well
	# --concurrency=thread,greenlet ensures that we get coverage for
	# async as well as sync code. Without that code after connection.rollback()
	# is not covered
	poetry run coverage run --concurrency=thread,greenlet --source=carlos -m pytest .

coverage:
	poetry run coverage html -d tests/coverage_report
	poetry run coverage report --fail-under=100

mypy:
	poetry run mypy carlos

ruff:
	poetry run ruff check carlos

# Some alias to keep the old names
test:
	make pytest
	make coverage

type-check:
	make mypy

lint:
	make ruff

ci-check:
	make format
	make ruff
	make mypy
	make pytest
	make coverage
