from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.problem import Problem, ProblemSummary
from app.services.problem_service import list_problems, get_problem
from app.services.ai_service import chat_completion

router = APIRouter(prefix="/api/problems", tags=["problems"])

SOLUTION_PROMPT = """You are an expert Python programmer and educator.
Generate a clean, well-commented solution for the following coding problem.

**CRITICAL FORMAT RULES — follow exactly:**
1. Start with a block of comments explaining:
   - What the problem is asking (1-2 lines)
   - The approach/algorithm you will use (2-4 lines)
   - Time and space complexity (1-2 lines)
   - Key steps of the solution (numbered list)
2. Then write the actual code with inline comments on non-obvious lines.
3. Output ONLY valid Python code (with comments). No markdown, no backticks, no explanation outside of comments.
4. The function signature must match the starter code exactly.

Problem: {title}
{description}

Constraints: {constraints}

Starter code:
{starter_code}

Examples:
{examples}"""


class SolutionResponse(BaseModel):
    solution: str


@router.get("", response_model=list[ProblemSummary])
def get_problems(category: str | None = None, difficulty: str | None = None):
    return list_problems(category=category, difficulty=difficulty)


@router.get("/{problem_id}", response_model=Problem)
def get_problem_detail(problem_id: str):
    problem = get_problem(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.get("/{problem_id}/solution", response_model=SolutionResponse)
async def get_solution(problem_id: str):
    problem = get_problem(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    examples_text = "\n".join(
        f"  Input: {ex.get('input', '')}  Output: {ex.get('output', '')}" for ex in problem.examples
    )

    prompt = SOLUTION_PROMPT.format(
        title=problem.title,
        description=problem.description,
        constraints=", ".join(problem.constraints),
        starter_code=problem.starter_code,
        examples=examples_text,
    )

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Generate the solution now."},
    ]

    solution = await chat_completion(messages, temperature=0.3)

    # Strip markdown code fences if the AI added them
    solution = solution.strip()
    if solution.startswith("```python"):
        solution = solution[len("```python") :].strip()
    if solution.startswith("```"):
        solution = solution[3:].strip()
    if solution.endswith("```"):
        solution = solution[:-3].strip()

    return SolutionResponse(solution=solution)
