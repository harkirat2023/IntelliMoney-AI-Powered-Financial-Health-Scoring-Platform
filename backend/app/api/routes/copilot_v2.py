import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.copilot.schemas import (
    ChatHistoryResponse, ChatMessageResponse, ChatRequest, ChatResponse,
    ChatSessionResponse, CopilotSettings, FeedbackRequest, FeedbackResponse,
    SuggestionResponse,
)
from app.copilot.services.copilot_service import CopilotService
from app.copilot.services.llm_service import LLMService
from app.copilot.services.memory_service import MemoryService
from app.copilot.services.rag_service import RAGService
from app.copilot.repositories.repositories import (
    MongoChatMessageRepository, MongoChatSessionRepository,
    MongoConversationMemoryRepository, MongoConversationSummaryRepository,
)
from app.core.config import get_settings
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/copilot", tags=["Copilot"])


def _get_services(db: AsyncIOMotorDatabase) -> tuple:
    session_repo = MongoChatSessionRepository(db)
    message_repo = MongoChatMessageRepository(db)
    memory_repo = MongoConversationMemoryRepository(db)
    summary_repo = MongoConversationSummaryRepository(db)
    llm = LLMService()
    rag = RAGService()
    memory = MemoryService(session_repo, message_repo, memory_repo, summary_repo, llm)
    copilot = CopilotService(db, memory, llm, rag)
    return copilot, memory, message_repo


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_id = str(current_user["_id"])
    copilot, _, _ = _get_services(db)
    result = await copilot.process_message(user_id, body.message, body.session_id)
    return ChatResponse(**result)


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def get_sessions(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_id = str(current_user["_id"])
    _, memory, _ = _get_services(db)
    sessions = await memory.get_sessions(user_id)
    return [
        ChatSessionResponse(
            id=s.id, title=s.title, message_count=s.message_count,
            created_at=s.created_at, updated_at=s.updated_at,
        ) for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
async def get_session_history(
    session_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_id = str(current_user["_id"])
    _, _, message_repo = _get_services(db)
    session_repo = MongoChatSessionRepository(db)
    session = await session_repo.get_by_id(session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = await message_repo.get_by_session(session_id)
    return ChatHistoryResponse(
        session=ChatSessionResponse(
            id=session.id, title=session.title, message_count=session.message_count,
            created_at=session.created_at, updated_at=session.updated_at,
        ),
        messages=[
            ChatMessageResponse(
                id=m.id, session_id=m.session_id, role=m.role, content=m.content,
                metadata=m.metadata, feedback=m.feedback, created_at=m.created_at,
            ) for m in messages
        ],
    )


@router.delete("/sessions", response_model=dict)
async def delete_all_sessions(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_id = str(current_user["_id"])
    _, memory, _ = _get_services(db)
    await memory.delete_all(user_id)
    return {"message": "All sessions and history deleted"}


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    body: FeedbackRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_id = str(current_user["_id"])
    copilot, _, _ = _get_services(db)
    result = await copilot.record_feedback(
        user_id, body.session_id, body.message_id, body.rating, body.feedback_text,
    )
    return FeedbackResponse(**result)


@router.get("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_id = str(current_user["_id"])
    copilot, _, _ = _get_services(db)
    suggestions = await copilot.get_suggestions(user_id)
    return SuggestionResponse(suggestions=suggestions)


@router.get("/settings", response_model=CopilotSettings)
async def get_settings_endpoint(
    current_user: dict[str, Any] = Depends(get_current_user),
):
    cfg = get_settings()
    return CopilotSettings(
        model=cfg.openai_model or "gpt-4o",
        temperature=cfg.openai_temperature or 0.3,
        max_tokens=cfg.openai_max_tokens or 1024,
    )
