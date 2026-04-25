#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)

if ! command -v python >/dev/null 2>&1; then
    echo "ERROR: python was not found in PATH." >&2
    exit 1
fi

cd "$PROJECT_ROOT"
python -m tools.devtools bootstrap dev
