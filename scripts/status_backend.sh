#!/usr/bin/env bash
set -euo pipefail

PORT=8573
NAME="Backend (uvicorn)"

pid=$(ss -tlnp 2>/dev/null | grep ":${PORT} " | grep -oP 'pid=\K\d+' | head -1)

if [ -n "$pid" ]; then
  echo "$NAME is RUNNING on port $PORT (PID $pid)"
  # Show uptime if /proc available
  if [ -d "/proc/$pid" ]; then
    elapsed=$(ps -o etime= -p "$pid" 2>/dev/null | xargs)
    echo "  Uptime: ${elapsed:-unknown}"
  fi
  # Quick health check
  status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${PORT}/api/problems" --max-time 3 2>/dev/null || echo "000")
  if [ "$status" = "200" ]; then
    echo "  Health: OK (HTTP $status)"
  else
    echo "  Health: DEGRADED (HTTP $status)"
  fi
  exit 0
else
  echo "$NAME is NOT running (port $PORT free)"
  exit 1
fi
