VENV_NAME := .venv
VENV_BIN_PATH := ./.venv/bin
VENV_PYTHON := $(VENV_BIN_PATH)/python
VENV_PIP := $(VENV_BIN_PATH)/pip
VENV_PYLINT := $(VENV_BIN_PATH)/pylint
VENV_TWINE := $(VENV_BIN_PATH)/twine

SOURCE_PATH = src/meru

clean:
	-rm -rf $(VENV_NAME)
	-rm -rf src/*.egg-info

develop: clean
	python3.7 -m venv .venv
	$(VENV_PIP) install --upgrade pip wheel
	$(VENV_PIP) install -e .[develop]

test:
	$(VENV_BIN_PATH)/py.test tests

lint:
	$(VENV_PYLINT) $(SOURCE_PATH)

ci: lint
	$(VENV_BIN_PATH)/py.test --cov=$(SOURCE_PATH) --cov-report xml:coverage.xml --junitxml=junit.xml tests

coverage:
	$(VENV_BIN_PATH)/py.test --cov=$(SOURCE_PATH) --cov-report term-missing tests

.PHONY: dist
dist:
	-rm -rf dist/
	$(VENV_PYTHON) setup.py sdist bdist_wheel

upload:
	$(VENV_TWINE) upload dist/*
