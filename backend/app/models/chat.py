from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class InterviewStartRequest(BaseModel):
    session_id: str


class InterviewChatRequest(BaseModel):
    session_id: str
    message: str


class InterviewResponse(BaseModel):
    message: str
    is_complete: bool = False
