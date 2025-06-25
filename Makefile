# Makefile for BCA project (Windows + Unix compatible)
.PHONY: help venv install install-dev install-build install-all build build-gui clean run test-exe dev-setup echo_python
ifeq ($(OS),Windows_NT) 
PYTHON := $(shell cmd /C prep\\find_py.bat)
POWERSHELL := C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
HELP_COMMAND := $(POWERSHELL) -NoProfile -ExecutionPolicy Bypass -File prep/make_help.ps1 "$(MAKEFILE_LIST)"
ifeq ($(PYTHON),1)
  $(info No valid Python install found!)
else ifeq ($(PYTHON),2)
  $(info Major version less than 3)
else ifeq ($(PYTHON),3)
  $(info Minor version less than 10)
endif

VENV_PYTHON := venv\Scripts\python.exe
ACTIVATE := .\venv\Scripts\activate
RUN_EXE := dist\BCA_Tool.exe
DELETE := del
else
PYTHON := $(shell ./prep/find_py.sh)
HELP_COMMAND := ./prep/make_help.sh $(MAKEFILE_LIST)
VENV_PYTHON := venv/bin/python
ACTIVATE := source venv/bin/activate
RUN_EXE := ./dist/BCA_Tool
DELETE := rm
endif

help:  ## Show this help message
	@echo "Available commands:"
	@$(HELP_COMMAND)

venv:  ## Create virtual environment if it doesn't exist
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		"$(PYTHON)" -m venv venv; \
	else \
		echo "Virtual environment already exists."; \
	fi

install: venv  ## Install package in development mode inside venv
	$(VENV_PYTHON) -m pip install ".[all, build]"

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