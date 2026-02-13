#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

cd "$FRONTEND_DIR"

# Install dependencies if needed
if [ ! -d node_modules ]; then
  echo "Installing frontend dependencies..."
  pnpm install
fi

echo "Starting Vue dev server on http://localhost:5173"
exec pnpm dev
