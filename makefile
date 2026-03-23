.PHONY: all test lint format

all: test lint

test:
	@echo "Running tests..."

lint:
	@echo "Running linting..."

format:
	@echo "Running formatting..."

install-hooks:
	ln -sf ../../.gemini/hooks/pre-commit.py .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
