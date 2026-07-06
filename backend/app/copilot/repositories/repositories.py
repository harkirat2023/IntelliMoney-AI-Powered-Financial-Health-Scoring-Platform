from abc import ABC, abstractmethod
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.copilot.models.models import (
    AiFeedback, ChatMessage, ChatSession, ConversationMemory, ConversationSummary,
)


class ChatSessionRepository(ABC):
    @abstractmethod
    async def create(self, session: ChatSession) -> ChatSession: ...
    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 20) -> list[ChatSession]: ...
    @abstractmethod
    async def get_by_id(self, session_id: str) -> ChatSession | None: ...
    @abstractmethod
    async def update(self, session_id: str, data: dict) -> bool: ...
    @abstractmethod
    async def delete_by_user(self, user_id: str) -> int: ...


class ChatMessageRepository(ABC):
    @abstractmethod
    async def create(self, msg: ChatMessage) -> ChatMessage: ...
    @abstractmethod
    async def get_by_session(self, session_id: str, limit: int = 100) -> list[ChatMessage]: ...
    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 50) -> list[ChatMessage]: ...
    @abstractmethod
    async def update_feedback(self, message_id: str, feedback: str) -> bool: ...
    @abstractmethod
    async def delete_by_user(self, user_id: str) -> int: ...


class ConversationMemoryRepository(ABC):
    @abstractmethod
    async def upsert(self, memory: ConversationMemory) -> ConversationMemory: ...
    @abstractmethod
    async def get_by_session(self, session_id: str) -> ConversationMemory | None: ...
    @abstractmethod
    async def delete_by_user(self, user_id: str) -> int: ...


class ConversationSummaryRepository(ABC):
    @abstractmethod
    async def upsert(self, summary: ConversationSummary) -> ConversationSummary: ...
    @abstractmethod
    async def get_by_session(self, session_id: str) -> ConversationSummary | None: ...
    @abstractmethod
    async def delete_by_user(self, user_id: str) -> int: ...


class AiFeedbackRepository(ABC):
    @abstractmethod
    async def create(self, feedback: AiFeedback) -> AiFeedback: ...
    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 50) -> list[AiFeedback]: ...


class MongoChatSessionRepository(ChatSessionRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.chat_sessions

    async def create(self, session: ChatSession) -> ChatSession:
        doc = session.to_mongo()
        doc["created_at"] = doc["updated_at"] = datetime.utcnow()
        r = await self._collection.insert_one(doc)
        session.id = str(r.inserted_id)
        return session

    async def get_by_user(self, user_id: str, limit: int = 20) -> list[ChatSession]:
        cursor = self._collection.find({"user_id": user_id}).sort("updated_at", -1).limit(limit)
        return [ChatSession.from_mongo(d) for d in await cursor.to_list(length=limit)]

    async def get_by_id(self, session_id: str) -> ChatSession | None:
        d = await self._collection.find_one({"_id": session_id})
        return ChatSession.from_mongo(d) if d else None

    async def update(self, session_id: str, data: dict) -> bool:
        data["updated_at"] = datetime.utcnow()
        r = await self._collection.update_one({"_id": session_id}, {"$set": data})
        return r.modified_count > 0

    async def delete_by_user(self, user_id: str) -> int:
        r = await self._collection.delete_many({"user_id": user_id})
        return r.deleted_count


class MongoChatMessageRepository(ChatMessageRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.chat_messages

    async def create(self, msg: ChatMessage) -> ChatMessage:
        doc = msg.to_mongo()
        doc["created_at"] = datetime.utcnow()
        r = await self._collection.insert_one(doc)
        msg.id = str(r.inserted_id)
        return msg

    async def get_by_session(self, session_id: str, limit: int = 100) -> list[ChatMessage]:
        cursor = self._collection.find({"session_id": session_id}).sort("created_at", 1).limit(limit)
        return [ChatMessage.from_mongo(d) for d in await cursor.to_list(length=limit)]

    async def get_by_user(self, user_id: str, limit: int = 50) -> list[ChatMessage]:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        return [ChatMessage.from_mongo(d) for d in await cursor.to_list(length=limit)]

    async def update_feedback(self, message_id: str, feedback: str) -> bool:
        r = await self._collection.update_one({"_id": message_id}, {"$set": {"feedback": feedback}})
        return r.modified_count > 0

    async def delete_by_user(self, user_id: str) -> int:
        r = await self._collection.delete_many({"user_id": user_id})
        return r.deleted_count


class MongoConversationMemoryRepository(ConversationMemoryRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.conversation_memory

    async def upsert(self, memory: ConversationMemory) -> ConversationMemory:
        doc = memory.to_mongo()
        doc["created_at"] = datetime.utcnow()
        await self._collection.update_one(
            {"user_id": memory.user_id, "session_id": memory.session_id},
            {"$set": doc}, upsert=True)
        return memory

    async def get_by_session(self, session_id: str) -> ConversationMemory | None:
        d = await self._collection.find_one({"session_id": session_id})
        return ConversationMemory.from_mongo(d) if d else None

    async def delete_by_user(self, user_id: str) -> int:
        r = await self._collection.delete_many({"user_id": user_id})
        return r.deleted_count


class MongoConversationSummaryRepository(ConversationSummaryRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.conversation_summary

    async def upsert(self, summary: ConversationSummary) -> ConversationSummary:
        doc = summary.to_mongo()
        doc["created_at"] = datetime.utcnow()
        await self._collection.update_one(
            {"user_id": summary.user_id, "session_id": summary.session_id},
            {"$set": doc}, upsert=True)
        return summary

    async def get_by_session(self, session_id: str) -> ConversationSummary | None:
        d = await self._collection.find_one({"session_id": session_id})
        return ConversationSummary.from_mongo(d) if d else None

    async def delete_by_user(self, user_id: str) -> int:
        r = await self._collection.delete_many({"user_id": user_id})
        return r.deleted_count


class MongoAiFeedbackRepository(AiFeedbackRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db.ai_feedback

    async def create(self, feedback: AiFeedback) -> AiFeedback:
        doc = feedback.to_mongo()
        doc["created_at"] = datetime.utcnow()
        r = await self._collection.insert_one(doc)
        feedback.id = str(r.inserted_id)
        return feedback

    async def get_by_user(self, user_id: str, limit: int = 50) -> list[AiFeedback]:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        return [AiFeedback.from_mongo(d) for d in await cursor.to_list(length=limit)]
