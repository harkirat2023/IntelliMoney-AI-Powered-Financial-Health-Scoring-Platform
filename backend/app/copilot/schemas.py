from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    metadata: dict = {}
    feedback: str | None = None
    created_at: datetime | None = None


class ChatSessionResponse(BaseModel):
    id: str
    title: str = "New Chat"
    message_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    session_id: str
    message: str
    message_id: str
    sources: list[str] = []


class ChatHistoryResponse(BaseModel):
    session: ChatSessionResponse | None = None
    messages: list[ChatMessageResponse] = []


class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    rating: int = Field(ge=1, le=5)
    feedback_text: str = ""


class FeedbackResponse(BaseModel):
    id: str
    message: str = "Feedback recorded"


class SuggestionResponse(BaseModel):
    suggestions: list[str] = []


class CopilotSettings(BaseModel):
    model: str = "gpt-4o"
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=64, le=4096)
    use_streaming: bool = True
