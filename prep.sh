#!/bin/bash

# Unix build script for BCA
set -e  # Exit on error

echo "Building BCA executable..."
echo ""

PYTHON_BIN=$(./prep/find_py.sh)


# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_BIN -m venv venv
fi

# Activate venv
# shellcheck disable=SC1091
source venv/bin/activate

# Install build dependencies
echo "Installing build dependencies..."
venv/bin/python -m pip install ".[dependencies,build]"

echo "Starting build process..."
venv/bin/python build.py

