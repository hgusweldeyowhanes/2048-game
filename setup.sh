#!/bin/bash
set -e
echo "2048 Game Setup"
echo "==============="

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found"
  exit 1
fi

if [ ! -d .venv ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "SUCCESS. Run:"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo ""
