import json
import subprocess
import tempfile
from pathlib import Path

from app.config import settings
from app.sandbox.policies import BLOCKED_IMPORTS
from app.sandbox.wrapper_template import WRAPPER_TEMPLATE
from app.models.session import SubmissionResult


class SandboxError(Exception):
    pass


def check_blocked_imports(code: str) -> str | None:
    for imp in BLOCKED_IMPORTS:
        for pattern in [f"import {imp}", f"from {imp}"]:
            if pattern in code:
                return f"Blocked import detected: '{imp}' is not allowed for security reasons."
    return None


def run_code(user_code: str, test_cases: list[dict]) -> list[SubmissionResult]:
    blocked = check_blocked_imports(user_code)
    if blocked:
        return [
            SubmissionResult(
                test_index=i,
                passed=False,
                input=tc["input"],
                expected=tc["expected"],
                actual="",
                error=blocked,
            )
            for i, tc in enumerate(test_cases)
        ]

    tests_json = json.dumps(test_cases)
    script = WRAPPER_TEMPLATE.format(user_code=user_code, tests_json=tests_json)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "solution.py"
        script_path.write_text(script)

        try:
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                timeout=settings.sandbox_timeout,
                cwd=tmpdir,
            )
        except subprocess.TimeoutExpired:
            return [
                SubmissionResult(
                    test_index=i,
                    passed=False,
                    input=tc["input"],
                    expected=tc["expected"],
                    actual="",
                    error=f"Time limit exceeded ({settings.sandbox_timeout}s)",
                )
                for i, tc in enumerate(test_cases)
            ]

        stdout = result.stdout
        stderr = result.stderr

        if "__RESULTS__" in stdout:
            results_str = stdout.split("__RESULTS__", 1)[1].strip()
            try:
                raw = json.loads(results_str)
                return [SubmissionResult(**r) for r in raw]
            except json.JSONDecodeError:
                pass

        error_msg = stderr.strip() if stderr else "Unknown error during execution"
        return [
            SubmissionResult(
                test_index=i,
                passed=False,
                input=tc["input"],
                expected=tc["expected"],
                actual="",
                error=error_msg,
            )
            for i, tc in enumerate(test_cases)
        ]
