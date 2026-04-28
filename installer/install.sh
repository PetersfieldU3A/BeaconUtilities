#!/usr/bin/env bash
set -euo pipefail

INSTALL_CHROMIUM=0
if [[ "${1:-}" == "--install-chromium" ]]; then
  INSTALL_CHROMIUM=1
fi

INSTALL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$INSTALL_ROOT"

WHEEL_PATH="$(ls -t beacon_utilities-*.whl 2>/dev/null | head -n 1 || true)"
if [[ -z "$WHEEL_PATH" ]]; then
  echo "No wheel file matching beacon_utilities-*.whl found in $INSTALL_ROOT" >&2
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  BASE_PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  BASE_PYTHON="python"
else
  echo "Python was not found. Install Python 3.11+ and rerun this installer." >&2
  exit 1
fi

if [[ ! -d .venv ]]; then
  echo "Creating virtual environment in .venv"
  "$BASE_PYTHON" -m venv .venv
fi

VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Virtual environment python executable not found: $VENV_PYTHON" >&2
  exit 1
fi

echo "Upgrading pip"
"$VENV_PYTHON" -m pip install --upgrade pip

echo "Installing BeaconUtilities from $WHEEL_PATH"
"$VENV_PYTHON" -m pip install --upgrade "$WHEEL_PATH"

if [[ "$INSTALL_CHROMIUM" -eq 1 ]]; then
  echo "Installing Playwright Chromium runtime"
  "$VENV_PYTHON" -m playwright install chromium
fi

if [[ ! -f config/config.ini && -f config/config.example.ini ]]; then
  cp config/config.example.ini config/config.ini
  echo "Created config/config.ini from config.example.ini"
fi

cat > start-user-docs.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8020}"
DOCS_DIR="$SCRIPT_DIR/docs"
PYTHON_EXE="$SCRIPT_DIR/.venv/bin/python"

if [[ ! -d "$DOCS_DIR" ]]; then
  echo "Docs folder not found: $DOCS_DIR" >&2
  exit 1
fi

if [[ ! -x "$PYTHON_EXE" ]]; then
  echo "Virtual environment not found. Run install.sh first." >&2
  exit 1
fi

URL="http://127.0.0.1:${PORT}"
echo "Starting user docs at $URL"
echo "Press Ctrl+C to stop the docs server."

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "$URL" >/dev/null 2>&1 || true
fi

cd "$DOCS_DIR"
"$PYTHON_EXE" -m http.server "$PORT"
EOF
chmod +x start-user-docs.sh

cat > start-beacon-backup.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_SCRIPT="$SCRIPT_DIR/run.sh"
OUTPUT_FILE="${1:-}"

if [[ ! -x "$RUN_SCRIPT" ]]; then
  echo "Launcher script not found: $RUN_SCRIPT" >&2
  exit 1
fi

if [[ -z "$OUTPUT_FILE" ]]; then
  "$RUN_SCRIPT" backup-beacon
else
  "$RUN_SCRIPT" backup-beacon --output-file "$OUTPUT_FILE"
fi
EOF
chmod +x start-beacon-backup.sh

echo
echo "Installation complete."
echo "Next steps:"
echo "  1. Edit config/config.ini"
echo "  2. Run: ./.venv/bin/python -m beaconutilities.cli sync --dry-run"
echo "  3. Start docs: ./start-user-docs.sh"
echo "  4. Run backup: ./start-beacon-backup.sh"
