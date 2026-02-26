from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import chat_completion
from app.services.problem_service import get_problem

router = APIRouter(prefix="/api/code-chat", tags=["code-chat"])

SYSTEM_PROMPT = """You are a helpful coding tutor. The student is working on this problem:

**{problem_title}**
{problem_description}

Their current code:
```python
{code}
```

{selection_context}

Guidelines:
- Be concise but educational (2-5 sentences).
- If they selected specific code, focus your explanation on that selection.
- Use simple language. Explain the "why" not just the "what".
- If they ask about a bug, hint at the solution without giving it away directly.
- You may use short code snippets in your response when helpful."""


class CodeChatRequest(BaseModel):
    problem_id: str
    code: str
    message: str
    selected_text: str | None = None


class CodeChatResponse(BaseModel):
    reply: str


@router.post("", response_model=CodeChatResponse)
async def ask_code_question(req: CodeChatRequest):
    problem = get_problem(req.problem_id)
    title = problem.title if problem else "Unknown Problem"
    description = problem.description if problem else ""

    selection_context = ""
    if req.selected_text:
        selection_context = (
            f"The student selected this specific code/comment:\n"
            f"```\n{req.selected_text}\n```\n"
            f"Focus your answer on explaining this selection."
        )

    system_msg = SYSTEM_PROMPT.format(
        problem_title=title,
        problem_description=description,
        code=req.code,
        selection_context=selection_context,
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": req.message},
    ]

    reply = await chat_completion(messages, temperature=0.5)
    return CodeChatResponse(reply=reply)
