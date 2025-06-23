#!/bin/bash

# Unix build script for BCA
set -e  # Exit on error

echo "Building BCA executable..."
echo

# Check if Python is available
if ! command -v python3 &>/dev/null; then
    echo "Python not found! Please install Python 3.11 or higher."
    exit 1
fi

# Get Python version string, e.g., "Python 3.11.3"
PY_VER=$(python3 --version | awk '{print $2}')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
    echo "Python 3.11 or higher is required!"
    exit 1
fi


# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
# shellcheck disable=SC1091
source venv/bin/activate

# Install build dependencies
echo "Installing build dependencies..."
python3 -m pip install .

echo "Starting build process..."
python3 build.py

# Check if build was successful
if [ -f "dist/BCA_Tool" ]; then
    echo
    echo "Build completed successfully!"
    echo "Executable created: dist/BCA_Tool"
    echo
    read -p "Would you like to test the executable? (y/n): " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "Testing executable..."
        ./dist/BCA_Tool
    fi
else
    echo
    echo "Build failed! Check the output above for errors."
    exit 1
fi

echo
