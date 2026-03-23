#!/usr/bin/env bash
# Git pre-push hook — blocks push on lint, test, security, or commit message failures.
# Install: ln -sf ../../scripts/pre-push.sh .git/hooks/pre-push
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# Load nvm if available (needed for npx/node in git hooks)
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

MAIN=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@refs/remotes/origin/@@' || echo main)
FAIL=0
WARN=0

pass()  { echo "  [PASS] $1"; }
fail()  { echo "  [FAIL] $1"; FAIL=$((FAIL+1)); }
warn()  { echo "  [WARN] $1"; WARN=$((WARN+1)); }

echo "========================================"
echo "  PRE-PUSH REVIEW"
echo "========================================"

# ── 1. Lint: Backend (ruff) ──────────────────
if command -v ruff > /dev/null 2>&1; then
  if ruff check backend/app/ --no-fix > /dev/null 2>&1; then
    pass "Lint — Backend (ruff)"
  else
    fail "Lint — Backend (ruff)"
    ruff check backend/app/ --no-fix 2>&1 | head -20
  fi
else
  warn "Lint — Backend: ruff not found"
fi

# ── 1. Lint: Frontend (tsc) ──────────────────
if (cd frontend && npx tsc --noEmit) > /dev/null 2>&1; then
  pass "Lint — Frontend (tsc)"
else
  fail "Lint — Frontend (tsc)"
  (cd frontend && npx tsc --noEmit 2>&1) | head -20
fi

# ── 2. Tests: Backend (pytest) ───────────────
if [ -d backend/tests ] && [ "$(find backend/tests -name '*.py' | head -1)" ]; then
  if python3 -m pytest backend/tests/ -x -q > /dev/null 2>&1; then
    pass "Tests — Backend (pytest)"
  else
    fail "Tests — Backend (pytest)"
    python3 -m pytest backend/tests/ -x -q 2>&1 | tail -20
  fi
else
  warn "Tests — Backend: no unit tests found"
fi

# ── 2. Tests: Frontend ───────────────────────
if [ -f frontend/eslint.config.js ] || [ -f frontend/eslint.config.mjs ] || [ -f frontend/.eslintrc.json ]; then
  if (cd frontend && npx eslint . --max-warnings=0) > /dev/null 2>&1; then
    pass "Tests — Frontend (eslint)"
  else
    fail "Tests — Frontend (eslint)"
    (cd frontend && npx eslint . --max-warnings=0 2>&1) | head -20
  fi
else
  pass "Tests — Frontend (tsc covers type checks; no eslint config)"
fi

# ── 2. Validate solutions ────────────────────
if [ -f scripts/validate_solutions.py ]; then
  if python3 scripts/validate_solutions.py > /dev/null 2>&1; then
    pass "Solutions — All valid Python syntax"
  else
    fail "Solutions — Syntax errors detected"
    python3 scripts/validate_solutions.py 2>&1 | tail -10
  fi
fi

# ── 3. Security: secrets in diff ────────────
DIFF=$(git diff "$MAIN"...HEAD -- . ':!*.lock' ':!node_modules' ':!.venv' ':!*.sample' 2>/dev/null || true)
SECRETS_FOUND=""
while IFS= read -r pattern; do
  if echo "$DIFF" | grep -qiE -- "$pattern"; then
    SECRETS_FOUND+="  Pattern matched: $pattern"$'\n'
  fi
done <<'PATTERNS'
AIza[0-9A-Za-z_-]{35}
sk-[A-Za-z0-9]{20,}
ghp_[A-Za-z0-9]{36}
glpat-[A-Za-z0-9_-]{20}
xoxb-[0-9]{10,}
-----BEGIN (RSA |EC )?PRIVATE KEY-----
PATTERNS

if [ -z "$SECRETS_FOUND" ]; then
  pass "Security — No secrets in diff"
else
  fail "Security — Possible secrets detected"
  echo "$SECRETS_FOUND"
fi

# ── 4. Conventional commits ─────────────────
COMMITS=$(git log "$MAIN"..HEAD --format="%H %s" 2>/dev/null || true)
CC_OK=true
if [ -n "$COMMITS" ]; then
  while IFS= read -r line; do
    hash="${line%% *}"
    subject="${line#* }"
    short="${hash:0:8}"

    # Check conventional commit format
    if ! echo "$subject" | grep -qP '^(feat|fix|refactor|docs|style|test|ci|chore|perf|build|revert)(\(.+\))?!?: .+'; then
      fail "Commit $short — not conventional: $subject"
      CC_OK=false
    fi

    # Check for AI model mentions (subject + body)
    body=$(git log -1 --format="%B" "$hash")
    if echo "$body" | grep -qiP '(claude|anthropic|openai|co-authored-by.*(claude|anthropic|openai|copilot))'; then
      fail "Commit $short — mentions AI model: $subject"
      CC_OK=false
    fi
  done <<< "$COMMITS"
fi
$CC_OK && pass "Conventional Commits"

# ── 5. CHANGELOG freshness ──────────────────
if [ -f CHANGELOG.md ]; then
  CL_DATE=$(grep -oP '\d{4}-\d{2}-\d{2}' CHANGELOG.md | head -1)
  if [ -n "$CL_DATE" ]; then
    DAYS_AGO=$(( ($(date +%s) - $(date -d "$CL_DATE" +%s)) / 86400 ))
    if [ "$DAYS_AGO" -le 7 ]; then
      pass "CHANGELOG up to date ($CL_DATE)"
    elif [ "$DAYS_AGO" -le 30 ]; then
      warn "CHANGELOG may need updating (last entry: $CL_DATE, ${DAYS_AGO}d ago)"
    else
      fail "CHANGELOG stale (last entry: $CL_DATE, ${DAYS_AGO}d ago)"
    fi
  else
    warn "CHANGELOG.md has no parseable date"
  fi
else
  warn "CHANGELOG.md not found"
fi

# ── 6. README existence ─────────────────────
if [ -f README.md ]; then
  pass "README.md exists"
else
  warn "README.md not found — consider creating one"
fi

# ── Result ───────────────────────────────────
echo "========================================"
if [ "$FAIL" -gt 0 ]; then
  echo "  RESULT: FAIL ($FAIL issue(s), $WARN warning(s))"
  echo "========================================"
  exit 1
else
  echo "  RESULT: PASS ($WARN warning(s))"
  echo "========================================"
  exit 0
fi
