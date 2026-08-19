"""Agent-based copilot service.

Implements a LangChain tool-calling agent loop over the Groq LLM without
relying on ``create_react_agent`` (which has a typing incompatibility on
Python 3.14). The loop is simple and deterministic:

  user message
    -> LLM (tools bound)
    -> if tool_calls: execute each tool, append results, repeat (max N)
    -> final text answer

Only read/calculation tools run during the loop. The single write-planning
tool (``propose_actions``) stores a proposal for later explicit user
confirmation — it never mutates financial data.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import build_tools
from app.copilot.services.llm_service import LLMService
from app.copilot.services.memory_service import MemoryService

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 8


class AgentCopilotService:
    def __init__(self, db: AsyncIOMotorDatabase, memory_service: MemoryService,
                 llm_service: LLMService):
        self._db = db
        self._memory = memory_service
        self._llm = llm_service

    async def process_message(self, user_id: str, message: str,
                              session_id: str | None = None) -> dict:
        session, history = await self._memory.get_or_create_session(user_id, session_id)

        context = await self._build_context(user_id)
        tools, proposal_created = build_tools(self._db, user_id, session.id)

        messages = self._build_messages(history, message, context)
        response_text = await self._run_agent_loop(messages, tools)

        await self._memory.add_message(user_id, session.id, "user", message)
        ai_msg = await self._memory.add_message(user_id, session.id, "assistant", response_text)

        proposal = proposal_created[0].model_dump(mode="json") if proposal_created else None
        return {
            "session_id": session.id,
            "message": response_text,
            "message_id": ai_msg.id,
            "sources": [],
            "proposal": proposal,
        }

    async def _run_agent_loop(self, messages: list, tools: list) -> str:
        llm = self._llm._get_llm()
        llm_with_tools = llm.bind_tools(tools)
        tool_map = {t.name: t for t in tools}

        current = messages
        for _ in range(MAX_TOOL_ITERATIONS):
            response = await llm_with_tools.ainvoke(current)
            tool_calls = getattr(response, "tool_calls", None) or []
            if not tool_calls:
                return str(response.content) if response.content else (
                    "I couldn't find an answer for that. Please rephrase your question."
                )

            current = current + [response]
            for call in tool_calls:
                tool = tool_map.get(call.get("name", ""))
                if tool is None:
                    content = f"Unknown tool '{call.get('name')}'."
                else:
                    try:
                        args = call.get("args") or {}
                        result = await tool.ainvoke(args)
                        content = result if isinstance(result, str) else json.dumps(result, default=str)
                    except Exception as exc:  # noqa: BLE001 - surface errors to the LLM to self-correct
                        logger.warning("Tool %s failed: %s", call.get("name"), exc)
                        content = f"Tool error: {exc}"
                current = current + [
                    ToolMessage(content=content, tool_call_id=call.get("id", ""))
                ]
        return (
            "I need to gather more information to answer accurately. "
            "Please clarify your request or rephrase the question."
        )

    # ---- helpers -----------------------------------------------------------
    async def _build_context(self, user_id: str) -> dict:
        ctx: dict[str, Any] = {}
        health = await self._db.financial_health.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)]
        )
        if health:
            ctx["financial_health"] = {
                "score": health.get("score"), "risk_level": health.get("risk_level"),
            }
        budget = await self._db.budget_intelligence.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)]
        )
        if budget:
            ctx["budget"] = {
                "score": budget.get("budget_score"),
                "categories_count": len(budget.get("categories", [])),
            }
        cash = await self._db.cash_flow_summary.find_one(
            {"user_id": user_id}, sort=[("calculated_at", -1)]
        )
        if cash:
            ctx["cash_flow"] = {
                "income": cash.get("total_income"),
                "expenses": cash.get("total_expenses"),
                "net_savings": cash.get("net_savings"),
            }
        return ctx

    def _build_messages(self, history: list, message: str, context: dict) -> list:
        system = [SYSTEM_PROMPT]
        if context:
            system.append(f"\n## Current User Context\n{json.dumps(context, indent=2)}")
        system.append(f"\n## Date & Time\n{datetime.utcnow().isoformat()}")
        messages: list = [SystemMessage(content="\n\n".join(system))]
        for m in history[-20:]:
            role = getattr(m, "role", "")
            content = getattr(m, "content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        messages.append(HumanMessage(content=message))
        return messages