SHELL := /bin/sh
COMPOSE ?= docker compose
PYTHON ?= python3
PREVIEW_PYTHON ?= .venv/bin/python
PREVIEW_URL ?= http://127.0.0.1:8000
DEV = $(COMPOSE) run --rm dev

.PHONY: help setup data train verify test test-local check run down preview docker
help:
	@echo 'setup: build development image; data: download/validate original CSV'
	@echo 'train: full research run; test: automated checks; run/down: local app'
	@echo 'preview: UI screenshots (after design phase); docker: production build'
	@echo 'check: standard-library source checks; test-local: pytest in your environment'

setup:
	mkdir -p local outputs/figures models
	$(COMPOSE) build dev

data:
	$(DEV) python -m scripts.fetch_data

train:
	$(DEV) python -m ml.run_all

verify:
	$(DEV) python -m scripts.verify_reproducibility

test:
	$(DEV) python -m pytest -q tests --ignore=tests/e2e

test-local:
	$(PYTHON) -m pytest -q tests --ignore=tests/e2e

check:
	$(PYTHON) -m unittest discover -s tests -p 'check_*.py' -v

run:
	$(PYTHON) -m scripts.check_ready
	$(COMPOSE) up --build -d web

down:
	$(COMPOSE) down

preview:
	$(PYTHON) -m scripts.check_ready --preview
	$(PREVIEW_PYTHON) -m scripts.capture_previews --url $(PREVIEW_URL) --channel chrome
	$(PYTHON) -m scripts.check_contrast

docker:
	docker build --target runtime -t primera:local .
