# =============================================================================
# Codebase Companion — Makefile
# =============================================================================
# Common tasks. Run `make help` to see all targets.
#
# Prerequisites: Python 3.11+, pip, git
# =============================================================================

PYTHON      := python3
VENV        := .venv
VENV_BIN    := $(VENV)/bin
PIP         := $(VENV_BIN)/pip
PYTEST      := $(VENV_BIN)/pytest
STREAMLIT   := $(VENV_BIN)/streamlit
PYTHON_VENV := $(VENV_BIN)/python

.DEFAULT_GOAL := help

# ── Help ──────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  Codebase Companion — available targets"
	@echo "  ─────────────────────────────────────────"
	@echo "  make install      Create virtual env and install all dependencies"
	@echo "  make run          Launch the Streamlit web UI  (http://localhost:8501)"
	@echo "  make cli          Launch the interactive CLI"
	@echo "  make test         Run the pytest test suite"
	@echo "  make test-cov     Run tests with HTML coverage report"
	@echo "  make lint         Check code style with ruff (if installed)"
	@echo "  make clean        Remove generated data, vector store, and caches"
	@echo "  make clean-all    Also remove the virtual environment"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────
.PHONY: install
install: $(VENV)/bin/activate
	@echo "✓ Virtual environment ready. Activate with: source $(VENV)/bin/activate"

$(VENV)/bin/activate: requirements.txt
	@echo "→ Creating virtual environment in $(VENV)/"
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip --quiet
	@echo "→ Installing dependencies (this may take a few minutes)..."
	$(PIP) install -r requirements.txt --quiet
	@touch $(VENV)/bin/activate

# ── Run ───────────────────────────────────────────────────────────────────────
.PHONY: run
run: $(VENV)/bin/activate
	@if [ ! -f .env ]; then \
		echo ""; \
		echo "  ERROR: .env file not found."; \
		echo "  Run:  cp .env.example .env"; \
		echo "  Then set OPENAI_API_KEY in .env before continuing."; \
		echo ""; \
		exit 1; \
	fi
	$(STREAMLIT) run streamlit_app.py

.PHONY: cli
cli: $(VENV)/bin/activate
	@if [ ! -f .env ]; then \
		echo ""; \
		echo "  ERROR: .env file not found."; \
		echo "  Run:  cp .env.example .env"; \
		echo "  Then set OPENAI_API_KEY in .env before continuing."; \
		echo ""; \
		exit 1; \
	fi
	$(PYTHON_VENV) main.py

# ── Tests ─────────────────────────────────────────────────────────────────────
.PHONY: test
test: $(VENV)/bin/activate
	$(PYTEST) tests/ -v --tb=short

.PHONY: test-cov
test-cov: $(VENV)/bin/activate
	$(PIP) install pytest-cov --quiet
	$(PYTEST) tests/ -v --tb=short \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html:htmlcov
	@echo ""
	@echo "→ HTML coverage report: htmlcov/index.html"

# ── Lint ──────────────────────────────────────────────────────────────────────
.PHONY: lint
lint: $(VENV)/bin/activate
	@$(VENV_BIN)/ruff check app/ tests/ 2>/dev/null \
		|| echo "ruff not installed — run: $(PIP) install ruff"

# ── Clean ─────────────────────────────────────────────────────────────────────
.PHONY: clean
clean:
	@echo "→ Removing generated data, vector store, and caches..."
	rm -rf chroma_db/ data/ htmlcov/ .pytest_cache/ __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc"     -delete 2>/dev/null || true
	@echo "✓ Clean done (virtual environment preserved)"

.PHONY: clean-all
clean-all: clean
	@echo "→ Removing virtual environment..."
	rm -rf $(VENV)/
	@echo "✓ Full clean done"
