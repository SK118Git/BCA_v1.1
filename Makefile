# Makefile for Flasc BCA project

.PHONY: install install-dev install-build build clean run help

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in development mode
	pip install -e .

install-dev:  ## Install with development dependencies
	pip install -e ".[dev]"

install-build:  ## Install with build dependencies (PyInstaller)
	pip install -e ".[build]"

install-all:  ## Install with all dependencies
	pip install -e ".[all,build]"

build:  ## Build executable using PyInstaller
	python build.py

build-gui:  ## Build using Auto-py-to-exe GUI
	auto-py-to-exe

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.spec __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

run:  ## Run the application directly
	python src/main.py

test-exe:  ## Test the built executable (Windows)
	@if [ -f "dist/BCA_Tool.exe" ]; then \
		echo "Testing executable..."; \
		./dist/BCA_Tool.exe; \
	else \
		echo "Executable not found. Run 'make build' first."; \
	fi

# Quick development workflow
dev-setup: install-all  ## Complete development setup
	@echo "✅ Development environment ready!"
	@echo "Run 'make build' to create executable"
	@echo "Run 'make run' to test directly with Python"