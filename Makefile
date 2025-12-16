# Required variables
ifeq ($(OS),Windows_NT)
	PYTHON := python
	VENV := .venv-win
	PY := $(VENV)/Scripts/python
	FLAKE8 := $(VENV)/Scripts/flake8
	YARN := yarn --cwd lncrawl-web
else
	PYTHON := python3
	VENV := .venv-posix
	PY := $(VENV)/bin/python
	FLAKE8 := $(VENV)/bin/flake8
	NVM := "$$NVM_DIR"/nvm-exec
	YARN := $(NVM) yarn --cwd lncrawl-web
endif

VERSION := $(shell $(PYTHON) -c "print(open('lncrawl/VERSION').read().strip())")

# Default target (help/info)
.PHONY: clean version
_: version

version:
	@echo Current version: $(VERSION)

# Clean target
clean:
ifeq ($(OS),Windows_NT)
	@powershell -Command "try { Remove-Item -ErrorAction SilentlyContinue -Recurse -Force $(VENV), logs, build, dist } catch {}; exit 0"
	@powershell -Command "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter '*.egg-info' | Remove-Item -Recurse -Force"
	@powershell -Command "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force"
	@powershell -Command "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter 'node_modules' | Remove-Item -Recurse -Force"
else
	@rm -rf $(VENV) logs build dist
	@find . -name '*.egg-info' -type d -exec rm -rf '{}'
	@find . -name '__pycache__' -type d -exec rm -rf '{}'
	@find . -name 'node_modules' -type d -exec rm -rf '{}'
endif


# Setup virtual environment in .venv
setup:
ifeq ($(wildcard $(VENV)/pyvenv.cfg),)
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install -q -U pip
else
	$(info $(VENV) already exists.)
endif

# Install dependencies in .venv
install-py: setup
	$(PY) -m pip install -r requirements.txt

# Install node modules in lncrawl-web
install-web:
	$(YARN) install

install: install-py install-web

# Build wheel package and executable
build-web:
	$(YARN) build

build-wheel:
	$(PY) -m build -w

build-exe:
	$(PY) setup_pyi.py

build: version install build-web build-wheel build-exe

# Lint project files
start-server:
	$(PY) -m lncrawl -ll server

watch-server:
	$(PY) -m lncrawl -ll server --watch

start-web:
	$(YARN) dev

start:
	+$(MAKE) -j2 watch-server start-web

# Lint project files
lint-py:
	$(FLAKE8) --config .flake8 -v --count --show-source --statistics

lint-web:
	$(YARN) lint

lint: lint-py lint-web

# Push tag
pull:
	git pull --rebase --autostash

remove-tag:
	git push --delete origin "v$(VERSION)"
	git tag -d "v$(VERSION)"

push-tag: pull
	git tag "v$(VERSION)"
	git push --tags

push-tag-force: pull
	git push --delete origin "v$(VERSION)"
	git tag -d "v$(VERSION)"
	git tag "v$(VERSION)"
	git push --tags
