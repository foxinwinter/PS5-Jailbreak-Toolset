#!/bin/bash
# E.M.B.E.R Development Script

cd "$(dirname "$0")"

echo "Starting E.M.B.E.R in development mode..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Running E.M.B.E.R..."
python3 -m main
