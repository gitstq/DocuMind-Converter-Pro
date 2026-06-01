# Makefile for DocuMind Converter

.PHONY: help install install-dev test test-cov lint format clean build upload docs

PYTHON := python3
PIP := pip3

help:
	@echo "Available targets:"
	@echo "  install      - Install package and dependencies"
	@echo "  install-dev  - Install package with dev dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linters"
	@echo "  format       - Format code"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  upload       - Upload to PyPI"
	@echo "  docs         - Build documentation"

install:
	$(PIP) install -e ".[all]"

install-dev:
	$(PIP) install -e ".[all,dev]"
	pre-commit install

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src/documind --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/
	mypy src/
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/
	isort src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	$(PYTHON) -m build

upload: build
	twine upload dist/*

docs:
	cd docs && mkdocs build

# Development shortcuts
dev:
	$(PYTHON) -m documind

convert-sample:
	$(PYTHON) -m documind convert sample.pdf -o output.md
