import json

from app.services.session_service import get_session, _save_session
from app.services.problem_service import get_problem
from app.services.ai_service import chat_completion
from app.models.scoring import EvaluationResult, ScoreCategory


SCORING_PROMPT = """You are evaluating a coding interview candidate. Analyze their performance and return a JSON evaluation.

**Problem**: {problem_title}
{problem_description}

**Candidate's Code**:
```python
{code}
```

**Test Results**: {test_summary}

**Interview Transcript**:
{interview_transcript}

Evaluate the candidate across these 3 categories (score 0-100 each):

1. **Correctness** - Did the code pass tests? Is the logic sound?
2. **Code Quality** - Is it clean, readable, well-structured? Good naming? Efficient?
3. **Communication** - Did they explain their approach well? Handle interview questions thoughtfully?

Return ONLY valid JSON in this exact format, no markdown fences:
{{
  "overall_score": <weighted average>,
  "categories": [
    {{"name": "Correctness", "score": <0-100>, "feedback": "<2-3 sentences>"}},
    {{"name": "Code Quality", "score": <0-100>, "feedback": "<2-3 sentences>"}},
    {{"name": "Communication", "score": <0-100>, "feedback": "<2-3 sentences>"}}
  ],
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "improvements": ["<improvement 1>", "<improvement 2>"]
}}"""


async def evaluate_session(session_id: str) -> EvaluationResult:
    session = get_session(session_id)
    if not session:
        raise ValueError("Session not found")

    problem = get_problem(session.problem_id)
    if not problem:
        raise ValueError("Problem not found")

    passed = sum(1 for r in session.test_results if r.passed)
    total = len(session.test_results)
    test_summary = f"{passed}/{total} tests passed" if total > 0 else "No tests run"

    transcript_lines = []
    for msg in session.interview_messages:
        role = "Interviewer" if msg["role"] == "assistant" else "Candidate"
        transcript_lines.append(f"{role}: {msg['content']}")
    interview_transcript = "\n".join(transcript_lines) if transcript_lines else "No interview conducted"

    prompt = SCORING_PROMPT.format(
        problem_title=problem.title,
        problem_description=problem.description,
        code=session.code,
        test_summary=test_summary,
        interview_transcript=interview_transcript,
    )

    messages = [{"role": "user", "content": prompt}]

    try:
        response = await chat_completion(messages, temperature=0.3)
        # Strip markdown fences if present
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()

        data = json.loads(clean)
    except (json.JSONDecodeError, Exception):
        # Fallback: generate score from test results only
        correctness_score = int((passed / total) * 100) if total > 0 else 0
        data = {
            "overall_score": correctness_score,
            "categories": [
                {
                    "name": "Correctness",
                    "score": correctness_score,
                    "feedback": f"Passed {passed}/{total} test cases.",
                },
                {
                    "name": "Code Quality",
                    "score": 50,
                    "feedback": "AI evaluation unavailable. Review your code for readability and efficiency.",
                },
                {
                    "name": "Communication",
                    "score": 50,
                    "feedback": "AI evaluation unavailable.",
                },
            ],
            "summary": f"Passed {passed}/{total} tests. AI detailed evaluation was unavailable.",
            "strengths": ["Attempted the problem"],
            "improvements": ["Configure AI service for detailed feedback"],
        }

    result = EvaluationResult(
        session_id=session_id,
        overall_score=data["overall_score"],
        categories=[ScoreCategory(**c) for c in data["categories"]],
        summary=data["summary"],
        strengths=data.get("strengths", []),
        improvements=data.get("improvements", []),
    )

    session.score = result.model_dump()
    session.status = "scored"
    _save_session(session)

    return result
