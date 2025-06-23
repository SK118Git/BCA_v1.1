# Makefile for BCA project (Windows + Unix compatible)

SHELL := /bin/bash

.PHONY: help venv install install-dev install-build install-all build build-gui clean run test-exe dev-setup echo_python

ifeq ($(OS),Windows_NT)
PY_VER := $(shell call prep/find_py.bat)
ifeq ($(strip $(PY_VER)),)
	PYTHON := py 
else 
	PYTHON := py -$(PY_VER)
endif
VENV_PYTHON := venv\Scripts\python.exe
ACTIVATE := .\venv\Scripts\activate
RUN_EXE := dist\BCA_Tool.exe
DELETE := del
else
PYTHON := $(shell ./prep/find_py.sh)
VENV_PYTHON := venv/bin/python
ACTIVATE := source venv/bin/activate
RUN_EXE := ./dist/BCA_Tool
DELETE := rm
endif

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

venv:  ## Create virtual environment if it doesn't exist
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		"$(PYTHON)" -m venv venv; \
	else \
		echo "Virtual environment already exists."; \
	fi

install: venv  ## Install package in development mode inside venv
	$(VENV_PYTHON) -m pip install ".[dependencies, build]"

install-dev: venv  ## Install with development dependencies
	$(VENV_PYTHON) -m pip install -e . 

install-build: venv  ## Install with build dependencies (PyInstaller)
	$(VENV_PYTHON) -m pip install ".[build]"

install-all: venv  ## Install with all dependencies
	$(VENV_PYTHON) -m pip install ".[all,build]"

build:  venv ## Build executable using PyInstaller
	$(VENV_PYTHON) build.py

build-gui:  ## Build using Auto-py-to-exe GUI
	$(VENV_PYTHON) -m auto_py_to_exe

clean:  ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@$(DELETE) -rf build/ dist/ *.spec __pycache__/
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec $(DELETE) -rf {} +

run: venv  ## Run the application directly
	$(VENV_PYTHON) src/main.py

test-exe:  ## Test the built executable
	@if [ -f "$(RUN_EXE)" ]; then \
		echo "Testing executable..."; \
		$(RUN_EXE); \
	else \
		echo "Executable not found. Run 'make build' first."; \
	fi

dev-setup: install-all  ## Complete development setup
	@echo "✅ Development environment ready!"
	@echo "Run 'make build' to create executable"
	@echo "Run 'make run' to test directly with Python"

echo_python: ## Show Python exeecutable being used
	@echo $(PYTHON) 