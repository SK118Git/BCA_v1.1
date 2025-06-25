#!/bin/bash

MIN_MAJOR=3
MIN_MINOR=10

for ver in 3.15 3.14 3.13 3.12 3.11 3.10 3 ""; do
    PYTHON_BIN=$(command -v python$ver 2>/dev/null)
    if [ -n "$PYTHON_BIN" ]; then
        # Get version info
        PY_VER=$("$PYTHON_BIN" --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo "$PY_VER" | awk -F. '{print $1}')
        MINOR=$(echo "$PY_VER" | awk -F. '{print $2}')
        if [ "$MAJOR" -gt "$MIN_MAJOR" ] || { [ "$MAJOR" -eq "$MIN_MAJOR" ] && [ "$MINOR" -ge "$MIN_MINOR" ]; }; then
            echo "$PYTHON_BIN"
            exit 0
        fi
    fi
done

echo "Error: No suitable python3.11+ interpreter found." >&2
exit 1
