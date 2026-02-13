from pydantic import BaseModel


class TestCase(BaseModel):
    input: str
    expected: str
    is_hidden: bool = False


class Problem(BaseModel):
    id: str
    title: str
    category: str  # "algorithms" | "fastapi" | "django"
    difficulty: str  # "easy" | "medium" | "hard"
    description: str
    examples: list[dict]
    constraints: list[str]
    starter_code: str
    test_cases: list[TestCase]
    time_limit_minutes: int = 30
    tags: list[str] = []


class ProblemSummary(BaseModel):
    id: str
    title: str
    category: str
    difficulty: str
    tags: list[str] = []
    time_limit_minutes: int = 30
