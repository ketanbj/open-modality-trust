PYTHON ?= python3
DIST ?= core/dist

.PHONY: help check-python install demo test lint check-docs verify-evidence check-workspace check build
.DEFAULT_GOAL := help

help:
	@printf '%s\n' 'Run from the umbrella root in a Python 3.11+ environment:' '  make install           Install core, pinned sight/tactile adapters and development tools' '  make demo              Run both local adapter demos' '  make test              Run shared core and both adapter tests' '  make lint              Check shared-core/workspace Python lint and formatting' '  make check-docs        Check umbrella and pinned-modality Markdown links and headings' '  make verify-evidence   Verify pinned visual/tactile recorded evidence' '  make check-workspace   Check exact submodule pins and metadata' '  make check             Run all checks above except demos/install' '  make build             Build the shared-core package locally' 'Modality-specific commands live in each modality Makefile; see docs/development.md.'

check-python:
	$(PYTHON) -c 'import sys; sys.version_info >= (3, 11) or sys.exit("Python 3.11+ is required; set PYTHON=/path/to/a/supported/python")'

install: check-python
	$(PYTHON) -m pip install -e core -e 'modalities/openast[dev]' -e 'modalities/openatt[dev]'

demo:
	$(PYTHON) -m openast demo --output output/sight
	$(PYTHON) -m openatt demo --output output/tactile

test:
	$(PYTHON) -m pytest -q core/tests modalities/openast/tests modalities/openatt/tests

lint:
	$(PYTHON) -m ruff check core/src core/tests scripts
	$(PYTHON) -m ruff format --check core/src core/tests scripts

check-docs:
	$(PYTHON) scripts/check_docs.py
	$(PYTHON) modalities/openavt/scripts/check_docs.py
	$(PYTHON) modalities/openast/scripts/check_docs.py
	$(PYTHON) modalities/openatt/scripts/check_docs.py

verify-evidence:
	$(PYTHON) modalities/openast/scripts/verify_evidence.py
	$(PYTHON) modalities/openatt/scripts/verify_evidence.py

check-workspace:
	$(PYTHON) scripts/check_workspace.py --require-checkouts

check: check-workspace lint check-docs test verify-evidence

build:
	$(PYTHON) -m build core --outdir "$(DIST)"
