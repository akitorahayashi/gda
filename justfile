# ==============================================================================
# justfile for typ-tmpl automation
# ==============================================================================

# default target
default: help

# Show available recipes
help:
    @echo "Usage: just [recipe]"
    @echo "Available recipes:"
    @just --list | tail -n +2 | awk '{printf "  \033[36m%-20s\033[0m %s\n", $1, substr($0, index($0, $2))}'

# ==============================================================================
# Environment Setup
# ==============================================================================

# Initialize project: install dependencies and create the .env file
setup:
    @echo "🐍 Installing python dependencies with uv..."
    @uv sync

# ==============================================================================
# Development Commands
# ==============================================================================

# Run the CLI application
run *args:
    @uv run typ-tmpl {{args}}

# ==============================================================================
# CODE QUALITY
# ==============================================================================

# Automatically format and fix code (Ruff)
fix:
    @echo "🔧 Formatting and fixing code..."
    @uv run ruff format .
    @uv run ruff check . --fix

# Run static checks (Ruff, Mypy)
check: fix
    @echo "🔍 Running static checks..."
    @uv run ruff format --check .
    @uv run ruff check .
    @uv run mypy .

# ==============================================================================
# TESTING
# ==============================================================================

# Run complete test suite
test:
    @just unit-test
    @just intg-test
    @echo "✅ All tests passed!"

# Alias for test (backward compatibility)
local-test:
    @just test

# Run unit tests
unit-test:
    @echo "🚀 Running unit tests..."
    @uv run pytest tests/unit

# Run integration tests
intg-test:
    @echo "🚀 Running integration tests..."
    @uv run pytest tests/intg

# ==============================================================================
# CLEANUP
# ==============================================================================

# Remove cache files
clean:
    @echo "Cleaning up..."
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @rm -rf .venv .pytest_cache .ruff_cache .mypy_cache
    @echo "Done"
