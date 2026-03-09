# ============================================================
#  Road Safety - project helper targets
#  Usage:  make <target>
# ============================================================

.DEFAULT_GOAL := help
POETRY        := poetry
PYTEST        := $(POETRY) run pytest
RUFF          := $(POETRY) run ruff

SRC_DIR  := src
TEST_DIR := tests

# ------------------------------------------------------------
#  Help
# ------------------------------------------------------------
.PHONY: help
help:
	@echo ""
	@echo "  Road Safety - available make targets"
	@echo "  -------------------------------------"
	@echo "  make install      Install all dependencies (dev included)"
	@echo "  make test         Run the full test suite"
	@echo "  make test-cov     Run tests with HTML coverage report"
	@echo "  make test-fast    Run tests, stop on first failure"
	@echo "  make lint         Check source code with ruff"
	@echo "  make format       Auto-format source code with ruff"
	@echo "  make chat         Launch the interactive CLI (chat mode)"
	@echo "  make insights     Print road-safety insights"
	@echo "  make map          Generate the accident map (accidents_map.html)"
	@echo "  make dashboard    Launch the Streamlit dashboard"
	@echo "  make clean        Remove generated artefacts"
	@echo ""

# ------------------------------------------------------------
#  Dependencies
# ------------------------------------------------------------
.PHONY: install
install:
	$(POETRY) install

# ------------------------------------------------------------
#  Tests
# ------------------------------------------------------------
.PHONY: test
test:
	$(PYTEST) $(TEST_DIR) -v

.PHONY: test-cov
test-cov:
	$(PYTEST) $(TEST_DIR) --cov=$(SRC_DIR)/road_safety --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "  HTML coverage report: htmlcov/index.html"

.PHONY: test-fast
test-fast:
	$(PYTEST) $(TEST_DIR) -x -q

# ------------------------------------------------------------
#  Linting / formatting
# ------------------------------------------------------------
.PHONY: lint
lint:
	$(RUFF) check $(SRC_DIR) $(TEST_DIR)

.PHONY: format
format:
	$(RUFF) format $(SRC_DIR) $(TEST_DIR)

# ------------------------------------------------------------
#  Application shortcuts
# ------------------------------------------------------------
.PHONY: chat
chat:
	$(POETRY) run road-safety chat

.PHONY: insights
insights:
	$(POETRY) run road-safety insights

.PHONY: map
map:
	$(POETRY) run road-safety map

.PHONY: dashboard
dashboard:
	$(POETRY) run road-safety dashboard

# ------------------------------------------------------------
#  Cleanup
# ------------------------------------------------------------
.PHONY: clean
clean:
	rm -rf htmlcov .coverage .pytest_cache accidents_map.html
	find . -type d -name __pycache__ -print0 | xargs -0 rm -rf 2>/dev/null || true
