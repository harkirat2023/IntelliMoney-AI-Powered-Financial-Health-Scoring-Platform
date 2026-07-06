import logging
from datetime import datetime

from app.copilot.models.models import (
    ChatMessage, ChatSession, ConversationMemory, ConversationSummary,
)
from app.copilot.repositories.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    ConversationMemoryRepository,
    ConversationSummaryRepository,
)
from app.copilot.services.llm_service import LLMService, TokenCounter

logger = logging.getLogger(__name__)


class MemoryService:
    SUMMARIZE_THRESHOLD = 3000

    def __init__(self, session_repo: ChatSessionRepository,
                 message_repo: ChatMessageRepository,
                 memory_repo: ConversationMemoryRepository,
                 summary_repo: ConversationSummaryRepository,
                 llm_service: LLMService):
        self._session_repo = session_repo
        self._message_repo = message_repo
        self._memory_repo = memory_repo
        self._summary_repo = summary_repo
        self._llm = llm_service

    async def get_or_create_session(self, user_id: str,
                                    session_id: str | None = None) -> tuple[ChatSession, list[ChatMessage]]:
        if session_id:
            session = await self._session_repo.get_by_id(session_id)
            if session and session.user_id == user_id:
                messages = await self._message_repo.get_by_session(session_id)
                return session, messages
        session = ChatSession(user_id=user_id, title="New Chat")
        session = await self._session_repo.create(session)
        return session, []

    async def add_message(self, user_id: str, session_id: str, role: str,
                          content: str, metadata: dict | None = None) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, user_id=user_id,
                          role=role, content=content, metadata=metadata or {})
        msg = await self._message_repo.create(msg)
        await self._session_repo.update(session_id, {
            "message_count": (await self._message_repo.get_by_session(session_id)).__len__(),
        })
        await self._maybe_summarize(session_id, user_id)
        return msg

    async def _maybe_summarize(self, session_id: str, user_id: str):
        messages = await self._message_repo.get_by_session(session_id)
        total_tokens = sum(TokenCounter.count(m.content) for m in messages)
        if total_tokens < self.SUMMARIZE_THRESHOLD:
            return
        existing = await self._summary_repo.get_by_session(session_id)
        if existing:
            return
        combined = "\n".join(f"{m.role}: {m.content}" for m in messages[-20:])
        summary_text, _ = await self._llm.generate(
            "Summarize this financial conversation concisely.",
            [{"role": "user", "content": f"Summarize:\n{combined}"}],
        )
        summary = ConversationSummary(
            user_id=user_id, session_id=session_id,
            summary=summary_text, last_message_at=datetime.utcnow(),
        )
        await self._summary_repo.upsert(summary)

    async def get_summary(self, session_id: str) -> str | None:
        s = await self._summary_repo.get_by_session(session_id)
        return s.summary if s else None

    async def get_sessions(self, user_id: str) -> list[ChatSession]:
        return await self._session_repo.get_by_user(user_id)

    async def delete_all(self, user_id: str):
        await self._message_repo.delete_by_user(user_id)
        await self._session_repo.delete_by_user(user_id)
        await self._memory_repo.delete_by_user(user_id)
        await self._summary_repo.delete_by_user(user_id)
