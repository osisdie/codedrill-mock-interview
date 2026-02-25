from datetime import datetime

from app.services.problem_service import get_problem
from app.services.session_service import get_session, _save_session
from app.sandbox.runner import run_code


class ExecutionError(Exception):
    pass


def execute_run(session_id: str) -> dict:
    """Run visible test cases only."""
    session = get_session(session_id)
    if not session:
        raise ExecutionError("Session not found")

    problem = get_problem(session.problem_id)
    if not problem:
        raise ExecutionError("Problem not found")

    visible_tests = [{"input": tc.input, "expected": tc.expected} for tc in problem.test_cases if not tc.is_hidden]

    results = run_code(session.code, visible_tests)
    all_passed = all(r.passed for r in results)

    return {
        "results": [r.model_dump() for r in results],
        "all_passed": all_passed,
        "error": None,
    }


def execute_submit(session_id: str) -> dict:
    """Run all test cases (visible + hidden) and save results."""
    session = get_session(session_id)
    if not session:
        raise ExecutionError("Session not found")

    problem = get_problem(session.problem_id)
    if not problem:
        raise ExecutionError("Problem not found")

    all_tests = [{"input": tc.input, "expected": tc.expected} for tc in problem.test_cases]

    results = run_code(session.code, all_tests)
    all_passed = all(r.passed for r in results)

    session.test_results = results
    session.status = "submitted"
    session.submitted_at = datetime.now().isoformat()
    _save_session(session)

    return {
        "results": [r.model_dump() for r in results],
        "all_passed": all_passed,
        "error": None,
    }
