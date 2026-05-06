#!/usr/bin/env bash

# Resolve the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCANNER_DIR="$DIR/scanner"
VENV_DIR="$SCANNER_DIR/venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating Python virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    
    echo "[*] Installing dependencies..."
    "$VENV_DIR/bin/pip" install -q -r "$SCANNER_DIR/requirements.txt"
fi

# Run the scanner with all arguments passed to this script
"$VENV_DIR/bin/python" "$SCANNER_DIR/scanner.py" "$@"
