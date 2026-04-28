#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXE="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON_EXE" ]]; then
  echo "Virtual environment not found. Run install.sh first." >&2
  exit 1
fi

"$PYTHON_EXE" -m beaconutilities.cli "$@"
