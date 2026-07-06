import json
import logging
import re
from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.copilot.prompts import FINANCIAL_CONTEXT_PROMPT, SYSTEM_PROMPT
from app.copilot.schemas import CopilotSettings
from app.copilot.services.llm_service import LLMService, TokenCounter
from app.copilot.services.memory_service import MemoryService
from app.copilot.services.rag_service import RAGService
from app.copilot.services.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class CopilotService:
    def __init__(self, db: AsyncIOMotorDatabase, memory_service: MemoryService,
                 llm_service: LLMService, rag_service: RAGService):
        self._db = db
        self._memory = memory_service
        self._llm = llm_service
        self._rag = rag_service
        self._settings = CopilotSettings()

    async def process_message(self, user_id: str, message: str,
                              session_id: str | None = None) -> dict:
        if self._is_injection_attempt(message):
            return {"session_id": session_id or "", "message": self._injection_response(),
                    "message_id": "", "sources": []}

        session, history = await self._memory.get_or_create_session(user_id, session_id)
        if session.title == "New Chat":
            title = self._generate_title(message)
            await self._memory._session_repo.update(session.id, {"title": title})

        context = await self._build_context(user_id)
        tool_registry = ToolRegistry(self._db, user_id)
        tools = tool_registry.get_tools()
        tool_map = {t.__name__: t for t in tools}

        messages = self._build_messages(history, context, message)
        system_prompt = self._build_system_prompt(context)

        rag_context = await self._rag.search(message)
        if rag_context:
            context_str = "\n\n".join(r["content"] for r in rag_context)
            messages.insert(0, {"role": "system",
                                "content": f"Additional context from previous conversations:\n{context_str}"})

        response_text, meta = await self._llm.generate(system_prompt, messages, tools)

        if "<tool_call>" in response_text.lower():
            response_text = await self._execute_tool_calls(response_text, tool_map, user_id)

        await self._memory.add_message(user_id, session.id, "user", message)
        ai_msg = await self._memory.add_message(user_id, session.id, "assistant", response_text)

        pii_masked = self._mask_pii(response_text)

        await self._rag.index_document(
            f"User: {message}\nAssistant: {pii_masked}",
            {"user_id": user_id[:8], "session_id": session.id, "timestamp": datetime.utcnow().isoformat()},
        )

        return {"session_id": session.id, "message": pii_masked,
                "message_id": ai_msg.id, "sources": []}

    async def get_suggestions(self, user_id: str) -> list[str]:
        base = [
            "What's my financial health score?",
            "How am I doing on my budget this month?",
            "Where is my money going?",
            "Show me my top savings opportunities",
            "Summarize my financial month",
            "Do I have any overspending categories?",
        ]
        health = await self._db.financial_health.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)]
        )
        if health:
            score = health.get("score", 0)
            if score < 50:
                base.insert(0, "How can I improve my financial health?")
            elif score >= 80:
                base.insert(0, "How can I maintain my good financial health?")
        budget = await self._db.budget_intelligence.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)]
        )
        if budget:
            cats = budget.get("categories", [])
            overspent = [c for c in cats if c.get("status") == "over"]
            if overspent:
                base.insert(1, f"How do I reduce spending in {overspent[0]['category']}?")
        return base[:8]

    async def record_feedback(self, user_id: str, session_id: str,
                              message_id: str, rating: int, feedback_text: str = "") -> dict:
        from app.copilot.models.models import AiFeedback
        fb = AiFeedback(user_id=user_id, session_id=session_id,
                        message_id=message_id, rating=rating,
                        feedback_text=feedback_text)
        from app.copilot.repositories.repositories import MongoAiFeedbackRepository
        repo = MongoAiFeedbackRepository(self._db)
        fb = await repo.create(fb)
        return {"id": fb.id, "message": "Feedback recorded"}

    async def _build_context(self, user_id: str) -> dict:
        ctx = {}
        health = await self._db.financial_health.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)]
        )
        if health:
            ctx["financial_health"] = {"score": health.get("score"),
                                       "risk_level": health.get("risk_level")}
        budget = await self._db.budget_intelligence.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)]
        )
        if budget:
            ctx["budget"] = {"score": budget.get("budget_score"),
                             "categories_count": len(budget.get("categories", []))}
        cash = await self._db.cash_flow_summary.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)]
        )
        if cash:
            ctx["cash_flow"] = {"income": cash.get("total_income"),
                                "expenses": cash.get("total_expenses"),
                                "net_savings": cash.get("net_savings")}
        return ctx

    def _build_system_prompt(self, context: dict) -> str:
        parts = [SYSTEM_PROMPT, FINANCIAL_CONTEXT_PROMPT]
        if context:
            parts.append(f"\n## Current User Context\n{json.dumps(context, indent=2)}")
        parts.append(f"\n## Date & Time\n{datetime.utcnow().isoformat()}")
        return "\n\n".join(parts)

    def _build_messages(self, history: list, context: dict, message: str) -> list[dict]:
        msgs = []
        summary_text = ""
        if history:
            s = history[0]
            if hasattr(s, "session_id"):
                pass
        msgs = [{"role": "user", "content": msg.content} if msg.role == "user"
                else {"role": "assistant", "content": msg.content}
                for msg in history[-20:]] if history else []
        msgs.append({"role": "user", "content": message})
        return msgs

    async def _execute_tool_calls(self, text: str, tool_map: dict, user_id: str) -> str:
        calls = re.findall(r"<tool_call>\s*(\w+)\s*(.*?)</tool_call>", text, re.DOTALL)
        results = []
        for tool_name, args in calls[:3]:
            fn = tool_map.get(tool_name)
            if fn:
                try:
                    result = await fn(args.strip())
                    results.append(f"**{tool_name}**:\n{result[:1000]}")
                except Exception as e:
                    results.append(f"**{tool_name}**: Error - {e}")
        return text + "\n\n" + "\n\n".join(results) if results else text

    def _is_injection_attempt(self, text: str) -> bool:
        patterns = [
            r"(?i)ignore\s+(all\s+)?(previous|above|system|instructions)",
            r"(?i)you\s+are\s+(not\s+)?(an?\s+)?(assistant|bot|ai)",
            r"(?i)forget\s+(everything|all)",
            r"(?i)system\s+prompt",
            r"(?i)role\s*(:|play|assume)",
            r"(?i)act\s+as\s+(if|though)",
            r"(?i)you\s+must\s+(not|never)",
        ]
        return any(re.search(p, text) for p in patterns)

    def _injection_response(self) -> str:
        return "I'm sorry, I can't process that request. Please ask a financial question."

    def _mask_pii(self, text: str) -> str:
        text = re.sub(r"\b\d{16}\b", "****", text)
        text = re.sub(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "****", text)
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "***@***.***", text)
        text = re.sub(r"\b(\d{3}[ -]?\d{3}[ -]?\d{4})\b", "***-***-****", text)
        text = re.sub(r"\b[A-Z]{2}\d{1,2}[A-Z]{1,2}\d{1,4}[A-Z]{3,4}\b", "***", text)
        return text

    def _generate_title(self, message: str) -> str:
        msg = message.strip().lower()
        if len(msg) > 60:
            msg = msg[:60]
        return msg[:50] + ("..." if len(message.strip()) > 50 else "")
