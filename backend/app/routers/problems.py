import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models.problem import Problem, ProblemSummary
from app.services.problem_service import list_problems, get_problem
from app.services.ai_service import chat_completion, chat_completion_stream

logger = logging.getLogger(__name__)

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

    try:
        solution = await chat_completion(
            messages,
            temperature=0.3,
            max_tokens=4096,
            timeout=120.0,
        )
    except Exception as e:
        logger.error("Solution generation failed for %s: %s", problem_id, e)
        raise HTTPException(status_code=504, detail="AI service timed out — please try again")

    # Strip markdown code fences if the AI added them
    solution = solution.strip()
    if solution.startswith("```python"):
        solution = solution[len("```python") :].strip()
    if solution.startswith("```"):
        solution = solution[3:].strip()
    if solution.endswith("```"):
        solution = solution[:-3].strip()

    return SolutionResponse(solution=solution)


def _build_solution_messages(problem: Problem) -> list[dict]:
    """Build the prompt messages for solution generation (shared by both endpoints)."""
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
    return [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Generate the solution now."},
    ]


@router.get("/{problem_id}/solution/stream")
async def stream_solution(problem_id: str):
    """SSE endpoint that streams the solution as the LLM generates it."""
    problem = get_problem(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    messages = _build_solution_messages(problem)

    async def generate():
        try:
            async for chunk in chat_completion_stream(
                messages,
                temperature=0.3,
                max_tokens=4096,
                timeout=120.0,
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as e:
            logger.error("Stream failed for %s: %s", problem_id, e)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
