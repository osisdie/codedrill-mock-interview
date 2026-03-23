#!/usr/bin/env bash
# Generate solutions for all coding problems using claude -p
# Usage: ./scripts/generate_solutions.sh
# Requires: claude CLI, jq

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$PROJECT_ROOT/backend/data/problems"
INDEX_FILE="$DATA_DIR/problem_index.json"

if ! command -v claude &>/dev/null; then
  echo "Error: 'claude' CLI not found. Install it first."
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: 'jq' not found. Install it first."
  exit 1
fi

TOTAL=$(jq '.problems | length' "$INDEX_FILE")
echo "Found $TOTAL problems in index"

COUNT=0
SKIPPED=0
FAILED=0

PROMPT_FILE=$(mktemp)
trap 'rm -f "$PROMPT_FILE"' EXIT

for i in $(seq 0 $((TOTAL - 1))); do
  FILE=$(jq -r ".problems[$i].file" "$INDEX_FILE")
  ID=$(jq -r ".problems[$i].id" "$INDEX_FILE")
  FILEPATH="$DATA_DIR/$FILE"

  if [ ! -f "$FILEPATH" ]; then
    echo "[$((i+1))/$TOTAL] SKIP (file not found): $FILE"
    FAILED=$((FAILED + 1))
    continue
  fi

  # Skip if solution already exists
  HAS_SOLUTION=$(jq 'has("solution") and (.solution | length > 0)' "$FILEPATH")
  if [ "$HAS_SOLUTION" = "true" ]; then
    echo "[$((i+1))/$TOTAL] SKIP (already has solution): $ID"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  TITLE=$(jq -r '.title' "$FILEPATH")
  DESC=$(jq -r '.description' "$FILEPATH")
  CONSTRAINTS=$(jq -r '.constraints | join(", ")' "$FILEPATH")
  STARTER=$(jq -r '.starter_code' "$FILEPATH")
  EXAMPLES=$(jq -r '.examples[] | "Input: \(.input)\nOutput: \(.output)"' "$FILEPATH")

  # Write prompt to temp file to avoid shell escaping issues
  cat > "$PROMPT_FILE" <<PROMPT_EOF
You are an expert Python programmer and educator.
Generate a clean, well-commented solution for the following coding problem.

CRITICAL FORMAT RULES:
1. Start with a block of comments explaining:
   - What the problem is asking (1-2 lines)
   - The approach/algorithm you will use (2-4 lines)
   - Time and space complexity (1-2 lines)
   - Key steps of the solution (numbered list)
2. Then write the actual code with inline comments on non-obvious lines.
3. Output ONLY valid Python code (with comments). No markdown, no backticks, no explanation outside of comments.
4. The function signature must match the starter code exactly.

Problem: ${TITLE}
${DESC}

Constraints: ${CONSTRAINTS}

Starter code:
${STARTER}

Examples:
${EXAMPLES}
PROMPT_EOF

  echo "[$((i+1))/$TOTAL] Generating: $ID ($TITLE)..."

  SOLUTION=$(cat "$PROMPT_FILE" | claude -p --output-format text 2>/dev/null || echo "")

  if [ -z "$SOLUTION" ]; then
    echo "  FAILED: empty response"
    FAILED=$((FAILED + 1))
    continue
  fi

  # Strip markdown code fences if present
  SOLUTION=$(echo "$SOLUTION" | sed '/^```python$/d; /^```$/d')

  # Write solution into the JSON file using jq
  TMPFILE=$(mktemp)
  jq --arg sol "$SOLUTION" '. + {solution: $sol}' "$FILEPATH" > "$TMPFILE" && mv "$TMPFILE" "$FILEPATH"

  COUNT=$((COUNT + 1))
  echo "  OK"
done

echo ""
echo "Done! Generated: $COUNT, Skipped: $SKIPPED, Failed: $FAILED"
