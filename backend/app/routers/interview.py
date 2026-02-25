from fastapi import APIRouter, HTTPException

from app.models.chat import (
    InterviewStartRequest,
    InterviewChatRequest,
    InterviewResponse,
)
from app.services.session_service import get_session, _save_session
from app.services.problem_service import get_problem
from app.services.ai_service import chat_completion

router = APIRouter(prefix="/api/interview", tags=["interview"])

SYSTEM_PROMPT = """You are a senior technical interviewer conducting a coding interview.

The candidate has just solved (or attempted) the following problem:
**{problem_title}**
{problem_description}

Their submitted code:
```python
{code}
```

Test results: {test_summary}

Your role:
1. Ask about their approach, time/space complexity, and trade-offs
2. Ask follow-up questions about edge cases they may have missed
3. Ask 1-2 questions relating to real-world applications of this concept
4. Be professional but conversational — this should feel like a real technical interview

Guidelines:
- Ask ONE question at a time, wait for the candidate's response
- Keep responses concise (2-4 sentences + 1 question)
- After 5-6 exchanges, wrap up naturally by saying you have no more questions
- When wrapping up, end your message with exactly: [INTERVIEW_COMPLETE]"""


def _build_interview_context(session_id: str) -> tuple[list[dict], str]:
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    problem = get_problem(session.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    passed = sum(1 for r in session.test_results if r.passed)
    total = len(session.test_results)
    test_summary = f"{passed}/{total} tests passed" if total > 0 else "No tests run"

    system_msg = SYSTEM_PROMPT.format(
        problem_title=problem.title,
        problem_description=problem.description,
        code=session.code,
        test_summary=test_summary,
    )

    messages = [{"role": "system", "content": system_msg}]
    for msg in session.interview_messages:
        messages.append({"role": msg["role"], "content": msg["content"]})

    return messages, session_id


@router.post("/start", response_model=InterviewResponse)
async def start_interview(req: InterviewStartRequest):
    messages, session_id = _build_interview_context(req.session_id)

    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Clear previous interview if restarting
    session.interview_messages = []
    _save_session(session)

    messages_for_ai = messages + [{"role": "user", "content": "I'm ready for the interview. Please begin."}]

    reply = await chat_completion(messages_for_ai)
    is_complete = "[INTERVIEW_COMPLETE]" in reply
    clean_reply = reply.replace("[INTERVIEW_COMPLETE]", "").strip()

    session.interview_messages.append({"role": "user", "content": "I'm ready for the interview. Please begin."})
    session.interview_messages.append({"role": "assistant", "content": clean_reply})
    _save_session(session)

    return InterviewResponse(message=clean_reply, is_complete=is_complete)


@router.post("/chat", response_model=InterviewResponse)
async def chat(req: InterviewChatRequest):
    messages, session_id = _build_interview_context(req.session_id)

    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.interview_messages.append({"role": "user", "content": req.message})
    messages.append({"role": "user", "content": req.message})

    reply = await chat_completion(messages)
    is_complete = "[INTERVIEW_COMPLETE]" in reply
    clean_reply = reply.replace("[INTERVIEW_COMPLETE]", "").strip()

    session.interview_messages.append({"role": "assistant", "content": clean_reply})
    _save_session(session)

    return InterviewResponse(message=clean_reply, is_complete=is_complete)
