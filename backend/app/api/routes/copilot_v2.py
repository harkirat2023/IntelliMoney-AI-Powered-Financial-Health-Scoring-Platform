import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.agent.executor import ProposalExecutor
from app.agent.schemas import Proposal, ProposalStatus
from app.api.deps import get_current_user
from app.copilot.schemas import (
    ChatHistoryResponse, ChatMessageResponse, ChatRequest, ChatResponse,
    ChatSessionResponse, CopilotSettings, FeedbackRequest, FeedbackResponse,
    ProposalResponse, SuggestionResponse,
)
from app.copilot.services.copilot_service import CopilotService
from app.copilot.services.llm_service import LLMService
from app.copilot.services.memory_service import MemoryService
from app.copilot.repositories.repositories import (
    MongoChatMessageRepository, MongoChatSessionRepository,
    MongoConversationMemoryRepository, MongoConversationSummaryRepository,
)
from app.core.config import get_settings
from app.db.mongodb import get_database
from app.utils.object_id import to_object_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/copilot", tags=["Copilot"])


def _get_services(db: AsyncIOMotorDatabase) -> tuple:
    session_repo = MongoChatSessionRepository(db)
    message_repo = MongoChatMessageRepository(db)
    memory_repo = MongoConversationMemoryRepository(db)
    summary_repo = MongoConversationSummaryRepository(db)
    llm = LLMService()
    memory = MemoryService(session_repo, message_repo, memory_repo, summary_repo, llm)
    copilot = CopilotService(db, memory, llm)
    return copilot, memory, message_repo


def _get_agent_services(db: AsyncIOMotorDatabase) -> tuple:
    from app.agent.service import AgentCopilotService
    session_repo = MongoChatSessionRepository(db)
    message_repo = MongoChatMessageRepository(db)
    memory_repo = MongoConversationMemoryRepository(db)
    summary_repo = MongoConversationSummaryRepository(db)
    llm = LLMService()
    memory = MemoryService(session_repo, message_repo, memory_repo, summary_repo, llm)
    agent = AgentCopilotService(db, memory, llm)
    return agent, memory


class ProposalConfirmRequest(BaseModel):
    message_id: str = Field(default="", description="Chat message that produced the proposal")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    user_id = str(current_user["_id"])
    agent, _ = _get_agent_services(db)
    try:
        result = await agent.process_message(user_id, body.message, body.session_id)
    except Exception as exc:  # noqa: BLE001 - never 500 the chat endpoint
        logger.error("Copilot chat failed for user %s: %s", user_id, exc)
        result = {
            "session_id": body.session_id or "",
            "message": (
                "I'm sorry, I couldn't reach the language model right now. "
                "Please try again in a moment."
            ),
            "message_id": "",
            "sources": [],
            "proposal": None,
        }
    return ChatResponse(**result)


@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    user_id = str(current_user["_id"])
    try:
        oid = to_object_id(proposal_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Proposal not found") from exc
    doc = await db.agent_proposals.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return _proposal_response(doc)


@router.post("/proposals/{proposal_id}/confirm", response_model=ProposalResponse)
async def confirm_proposal(
    proposal_id: str,
    body: ProposalConfirmRequest | None = None,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    user_id = str(current_user["_id"])
    try:
        oid = to_object_id(proposal_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Proposal not found") from exc
    doc = await db.agent_proposals.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if doc.get("status") != ProposalStatus.PENDING.value:
        raise HTTPException(status_code=409, detail="Proposal is not pending")
    proposal = Proposal(
        id=str(doc["_id"]), user_id=user_id,
        session_id=doc.get("session_id", ""),
        status=ProposalStatus(doc.get("status", ProposalStatus.PENDING.value)),
        actions=doc.get("actions", []),
        created_at=doc.get("created_at"), updated_at=doc.get("updated_at"),
    )
    executor = ProposalExecutor(db)
    executed = await executor.execute(proposal)
    return ProposalResponse(
        id=executed.id, status=executed.status.value,
        actions=[a.model_dump(mode="json") for a in executed.actions],
        execution=[r.model_dump(mode="json") for r in executed.execution],
        message=(
            "All actions applied." if executed.status == ProposalStatus.EXECUTED
            else "Some actions failed. Review the execution report."
        ),
        created_at=executed.created_at, updated_at=executed.updated_at,
    )


@router.post("/proposals/{proposal_id}/cancel", response_model=ProposalResponse)
async def cancel_proposal(
    proposal_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    user_id = str(current_user["_id"])
    try:
        oid = to_object_id(proposal_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Proposal not found") from exc
    doc = await db.agent_proposals.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if doc.get("status") != ProposalStatus.PENDING.value:
        raise HTTPException(status_code=409, detail="Proposal is not pending")
    await db.agent_proposals.update_one(
        {"_id": oid},
        {"$set": {"status": ProposalStatus.CANCELLED.value}},
    )
    doc["status"] = ProposalStatus.CANCELLED.value
    return _proposal_response(doc)


def _proposal_response(doc: dict) -> ProposalResponse:
    return ProposalResponse(
        id=str(doc["_id"]),
        status=doc.get("status", ProposalStatus.PENDING.value),
        actions=doc.get("actions", []),
        execution=doc.get("execution", []),
        message=doc.get("message", ""),
        created_at=doc.get("created_at"), updated_at=doc.get("updated_at"),
    )


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def get_sessions(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
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
) -> Any:
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
) -> Any:
    user_id = str(current_user["_id"])
    _, memory, _ = _get_services(db)
    await memory.delete_all(user_id)
    return {"message": "All sessions and history deleted"}


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    body: FeedbackRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
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
) -> Any:
    user_id = str(current_user["_id"])
    copilot, _, _ = _get_services(db)
    suggestions = await copilot.get_suggestions(user_id)
    return SuggestionResponse(suggestions=suggestions)


@router.get("/settings", response_model=CopilotSettings)
async def get_settings_endpoint(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> Any:
    cfg = get_settings()
    return CopilotSettings(
        model=cfg.groq_model,
        temperature=cfg.groq_temperature,
        max_tokens=cfg.groq_max_tokens,
    )
