from fastapi import APIRouter, HTTPException

from app.models.problem import Problem, ProblemSummary
from app.services.problem_service import list_problems, get_problem

router = APIRouter(prefix="/api/problems", tags=["problems"])


@router.get("", response_model=list[ProblemSummary])
def get_problems(category: str | None = None, difficulty: str | None = None):
    return list_problems(category=category, difficulty=difficulty)


@router.get("/{problem_id}", response_model=Problem)
def get_problem_detail(problem_id: str):
    problem = get_problem(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem
