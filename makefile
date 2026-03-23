.PHONY: all test lint format clean install-hooks

all: lint test

test:
	uv run pytest --cov=src/codesmells tests/

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	rm -rf .venv .pytest_cache .ruff_cache src/codesmells/__pycache__ tests/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +

install-hooks:
	ln -sf ../../.gemini/hooks/pre-commit.py .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
