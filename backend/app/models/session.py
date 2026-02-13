from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class SessionCreate(BaseModel):
    problem_id: str


class SubmissionResult(BaseModel):
    test_index: int
    passed: bool
    input: str
    expected: str
    actual: str
    error: str | None = None


class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    problem_id: str
    code: str = ""
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    submitted_at: str | None = None
    time_remaining_seconds: int | None = None
    test_results: list[SubmissionResult] = []
    interview_messages: list[dict] = []
    score: dict | None = None
    status: str = "in_progress"  # "in_progress" | "submitted" | "scored"


class SessionUpdate(BaseModel):
    code: str | None = None
    time_remaining_seconds: int | None = None
    status: str | None = None
