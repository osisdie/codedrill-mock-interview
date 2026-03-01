#!/usr/bin/env bash
set -euo pipefail

PORT=8573
NAME="Backend (uvicorn)"

pid=$(ss -tlnp 2>/dev/null | grep ":${PORT} " | grep -oP 'pid=\K\d+' | head -1)

if [ -z "$pid" ]; then
  echo "$NAME is not running (port $PORT free)"
  exit 0
fi

echo "Stopping $NAME (PID $pid) on port $PORT..."
kill "$pid" 2>/dev/null

# Wait up to 5s for graceful shutdown
for i in $(seq 1 10); do
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "$NAME stopped"
    exit 0
  fi
  sleep 0.5
done

# Force kill if still running
echo "Graceful shutdown timed out — force killing PID $pid"
kill -9 "$pid" 2>/dev/null || true
echo "$NAME stopped (forced)"
