import json
from pathlib import Path

from app.config import settings
from app.models.problem import Problem, ProblemSummary


_problems_cache: dict[str, Problem] = {}


def _get_data_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / settings.data_dir


def _load_problems() -> dict[str, Problem]:
    global _problems_cache
    if _problems_cache:
        return _problems_cache

    data_dir = _get_data_dir()
    index_path = data_dir / "problem_index.json"
    with open(index_path) as f:
        index = json.load(f)

    for entry in index["problems"]:
        file_path = data_dir / entry["file"]
        with open(file_path) as f:
            data = json.load(f)
        _problems_cache[data["id"]] = Problem(**data)

    return _problems_cache


def list_problems(category: str | None = None, difficulty: str | None = None) -> list[ProblemSummary]:
    problems = _load_problems()
    result = []
    for p in problems.values():
        if category and p.category != category:
            continue
        if difficulty and p.difficulty != difficulty:
            continue
        result.append(
            ProblemSummary(
                id=p.id,
                title=p.title,
                category=p.category,
                difficulty=p.difficulty,
                tags=p.tags,
                time_limit_minutes=p.time_limit_minutes,
            )
        )
    return result


def get_problem(problem_id: str) -> Problem | None:
    problems = _load_problems()
    return problems.get(problem_id)


def reload_problems() -> None:
    global _problems_cache
    _problems_cache = {}
    _load_problems()
