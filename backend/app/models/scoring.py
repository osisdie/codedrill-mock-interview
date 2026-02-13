from pydantic import BaseModel


class ScoreCategory(BaseModel):
    name: str
    score: int  # 0-100
    feedback: str


class EvaluationRequest(BaseModel):
    session_id: str


class EvaluationResult(BaseModel):
    session_id: str
    overall_score: int  # 0-100
    categories: list[ScoreCategory]
    summary: str
    strengths: list[str]
    improvements: list[str]
