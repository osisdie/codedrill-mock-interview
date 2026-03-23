#!/usr/bin/env python3
"""Validate that all problems have syntactically valid Python solutions."""

import ast
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "problems"
INDEX_FILE = DATA_DIR / "problem_index.json"


def main():
    with open(INDEX_FILE) as f:
        index = json.load(f)

    problems = index["problems"]
    errors = []
    missing = []

    for entry in problems:
        filepath = DATA_DIR / entry["file"]
        pid = entry["id"]

        if not filepath.exists():
            errors.append(f"{pid}: file not found ({entry['file']})")
            continue

        with open(filepath) as f:
            data = json.load(f)

        solution = data.get("solution", "")
        if not solution or not solution.strip():
            missing.append(pid)
            continue

        try:
            ast.parse(solution)
        except SyntaxError as e:
            errors.append(f"{pid}: SyntaxError at line {e.lineno}: {e.msg}")

    print(f"Total problems: {len(problems)}")
    print(f"With valid solutions: {len(problems) - len(missing) - len(errors)}")

    if missing:
        print(f"\nMissing solutions ({len(missing)}):")
        for pid in missing:
            print(f"  - {pid}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")

    if errors:
        sys.exit(1)
    elif missing:
        print("\nWARNING: Some problems are missing solutions.")
        sys.exit(0)
    else:
        print("\nAll solutions are valid!")


if __name__ == "__main__":
    main()
