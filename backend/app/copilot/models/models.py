from datetime import datetime


class ChatSession:
    def __init__(self, user_id: str, title: str = "New Chat", message_count: int = 0,
                 created_at: datetime | None = None, updated_at: datetime | None = None,
                 id: str | None = None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.message_count = message_count
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "ChatSession":
        return cls(id=str(doc.get("_id")), user_id=str(doc.get("user_id")),
                   title=doc.get("title", "New Chat"), message_count=doc.get("message_count", 0),
                   created_at=doc.get("created_at"), updated_at=doc.get("updated_at"))

    def to_mongo(self) -> dict:
        d = {"user_id": self.user_id, "title": self.title,
             "message_count": self.message_count, "created_at": self.created_at,
             "updated_at": self.updated_at}
        if self.id:
            d["_id"] = self.id
        return d


class ChatMessage:
    def __init__(self, session_id: str, user_id: str, role: str, content: str,
                 metadata: dict | None = None, feedback: str | None = None,
                 created_at: datetime | None = None, id: str | None = None):
        self.id = id
        self.session_id = session_id
        self.user_id = user_id
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.feedback = feedback
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "ChatMessage":
        return cls(id=str(doc.get("_id")), session_id=str(doc.get("session_id")),
                   user_id=str(doc.get("user_id")), role=doc.get("role"),
                   content=doc.get("content"), metadata=doc.get("metadata", {}),
                   feedback=doc.get("feedback"), created_at=doc.get("created_at"))

    def to_mongo(self) -> dict:
        d = {"session_id": self.session_id, "user_id": self.user_id, "role": self.role,
             "content": self.content, "metadata": self.metadata, "feedback": self.feedback,
             "created_at": self.created_at}
        if self.id:
            d["_id"] = self.id
        return d


class ConversationMemory:
    def __init__(self, user_id: str, session_id: str, memory_type: str, content: str,
                 summary: str = "", token_count: int = 0, created_at: datetime | None = None,
                 id: str | None = None):
        self.id = id
        self.user_id = user_id
        self.session_id = session_id
        self.memory_type = memory_type
        self.content = content
        self.summary = summary
        self.token_count = token_count
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "ConversationMemory":
        return cls(id=str(doc.get("_id")), user_id=str(doc.get("user_id")),
                   session_id=str(doc.get("session_id")),
                   memory_type=doc.get("memory_type", "buffer"),
                   content=doc.get("content", ""), summary=doc.get("summary", ""),
                   token_count=doc.get("token_count", 0),
                   created_at=doc.get("created_at"))

    def to_mongo(self) -> dict:
        d = {"user_id": self.user_id, "session_id": self.session_id,
             "memory_type": self.memory_type, "content": self.content,
             "summary": self.summary, "token_count": self.token_count,
             "created_at": self.created_at}
        if self.id:
            d["_id"] = self.id
        return d


class ConversationSummary:
    def __init__(self, user_id: str, session_id: str, summary: str,
                 last_message_at: datetime | None = None, created_at: datetime | None = None,
                 id: str | None = None):
        self.id = id
        self.user_id = user_id
        self.session_id = session_id
        self.summary = summary
        self.last_message_at = last_message_at
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "ConversationSummary":
        return cls(id=str(doc.get("_id")), user_id=str(doc.get("user_id")),
                   session_id=str(doc.get("session_id")),
                   summary=doc.get("summary", ""),
                   last_message_at=doc.get("last_message_at"),
                   created_at=doc.get("created_at"))

    def to_mongo(self) -> dict:
        d = {"user_id": self.user_id, "session_id": self.session_id,
             "summary": self.summary, "last_message_at": self.last_message_at,
             "created_at": self.created_at}
        if self.id:
            d["_id"] = self.id
        return d


class AiFeedback:
    def __init__(self, user_id: str, session_id: str, message_id: str,
                 rating: int, feedback_text: str = "", created_at: datetime | None = None,
                 id: str | None = None):
        self.id = id
        self.user_id = user_id
        self.session_id = session_id
        self.message_id = message_id
        self.rating = rating
        self.feedback_text = feedback_text
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "AiFeedback":
        return cls(id=str(doc.get("_id")), user_id=str(doc.get("user_id")),
                   session_id=str(doc.get("session_id")),
                   message_id=str(doc.get("message_id")),
                   rating=doc.get("rating", 0),
                   feedback_text=doc.get("feedback_text", ""),
                   created_at=doc.get("created_at"))

    def to_mongo(self) -> dict:
        d = {"user_id": self.user_id, "session_id": self.session_id,
             "message_id": self.message_id, "rating": self.rating,
             "feedback_text": self.feedback_text, "created_at": self.created_at}
        if self.id:
            d["_id"] = self.id
        return d
