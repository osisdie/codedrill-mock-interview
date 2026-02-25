#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

cd "$BACKEND_DIR"

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
fi

# Install dependencies if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
  echo "Installing backend dependencies..."
  pip install -r requirements.txt
fi

echo "Starting FastAPI backend on http://localhost:8001"
echo "Swagger UI: http://localhost:8001/docs"
# exec uvicorn main:app --reload --port 8001
exec uvicorn main:app --port 8001
