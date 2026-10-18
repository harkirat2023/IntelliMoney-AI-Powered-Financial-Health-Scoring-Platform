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
from app.services.budget_service import get_budget_status
from app.utils.date_utils import month_bounds, utc_now
from app.utils.object_id import user_id_query

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
        summary = await self._memory.get_summary(session.id)

        # Budget-status questions have a deterministic, authoritative answer.
        # Answer these without making a language-model call so a temporary Groq
        # outage never prevents a user from seeing their actual budget state.
        try:
            response_text = await self._deterministic_answer(user_id, message)
            if response_text is None:
                messages = self._build_messages(history, message, context, summary)
                response_text = await self._run_agent_loop(messages, tools, context)
        except Exception as exc:  # noqa: BLE001 - never lose the chat on local errors
            logger.error("Copilot processing failed for user %s: %s", user_id, exc)
            response_text = (
                "I'm sorry, something went wrong while processing your request. "
                f"Here is your current financial summary: "
                f"{self._format_context_summary(context or {})}"
            )

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

    async def _deterministic_answer(self, user_id: str, message: str) -> str | None:
        normalized = " ".join(message.lower().split())
        overspending_terms = (
            "overspending", "overspend", "over budget", "exceeding budget",
        )
        if not any(term in normalized for term in overspending_terms):
            return None

        statuses = await get_budget_status(self._db, user_id)
        if not statuses:
            return (
                "You do not have any budgets for this month yet, so I can't "
                "identify overspending categories. Create a category budget to "
                "start tracking it."
            )

        over = [item for item in statuses if item.get("state") == "over"]
        warning = [
            item for item in statuses if item.get("state") in {"warning", "critical"}
        ]
        if over:
            details = "; ".join(
                f"{item['category']}: ₹{item['spent']:,.2f} of ₹{item['limit']:,.2f} "
                f"({item['percentage_used']:.0f}%)"
                for item in over
            )
            return f"Yes — you are over budget in {details}."
        if warning:
            details = "; ".join(
                f"{item['category']}: ₹{item['spent']:,.2f} of ₹{item['limit']:,.2f} "
                f"({item['percentage_used']:.0f}%)"
                for item in warning
            )
            return f"You are not over budget yet, but you are close in {details}."
        return "No — none of your budgeted categories are overspent this month."

    async def _run_agent_loop(self, messages: list, tools: list, context: dict | None = None) -> str:
        summary = self._format_context_summary(context or {})
        try:
            llm = self._llm._get_llm()
        except Exception as exc:
            logger.error("Copilot LLM unavailable: %s", exc)
            return (
                "I'm currently unable to reach the AI model. Here is your "
                f"current financial summary:\n{summary}"
            )
        try:
            llm_with_tools = llm.bind_tools(tools)
        except Exception as exc:
            logger.error("Could not bind copilot tools: %s", exc)
            return (
                "I'm currently unable to prepare the AI model. Here is your "
                f"current financial summary:\n{summary}"
            )
        tool_map = {t.name: t for t in tools}

        current = messages
        for _ in range(MAX_TOOL_ITERATIONS):
            try:
                response = await llm_with_tools.ainvoke(current)
            except Exception as exc:
                logger.error("Groq LLM invocation failed: %s", exc)
                return (
                    "I'm currently unable to reach the AI model, but here is "
                    f"your current financial summary:\n{summary}"
                )

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

    def _format_context_summary(self, context: dict) -> str:
        parts = []
        if context.get("monthly_income"):
            parts.append(f"Monthly Income: ₹{context['monthly_income']:,.2f}")
        if "cash_flow" in context:
            cf = context["cash_flow"]
            parts.append(
                f"Cash flow — Income: ₹{cf.get('income', 0):,.2f}, "
                f"Expenses: ₹{cf.get('expenses', 0):,.2f}, "
                f"Savings: ₹{cf.get('net_savings', 0):,.2f}"
            )
        spending = context.get("current_month_spending")
        if spending:
            parts.append(
                f"This month you spent ₹{spending.get('total', 0):,.2f} across "
                f"{spending.get('expense_count', 0)} transactions."
            )
            top = spending.get("top_categories", [])[:3]
            if top:
                parts.append(
                    "Top categories: "
                    + ", ".join(f"{t['category']} ₹{t['amount']:,.2f}" for t in top)
                )
        if "financial_health" in context:
            fh = context["financial_health"]
            parts.append(f"Health Score: {fh.get('score')}/100 ({fh.get('risk_level')})")
        if "current_budgets" in context:
            budgets = context["current_budgets"]
            over = [b for b in budgets if b.get("state") == "over"]
            close = [b for b in budgets if b.get("state") in {"warning", "critical"}]
            if over:
                parts.append(
                    "Overspent Categories: "
                    + ", ".join(
                        f"{b['category']} (₹{b['spent']:,.2f}/₹{b['limit']:,.2f})"
                        for b in over
                    )
                )
            elif close:
                parts.append(
                    "Categories near their limit: "
                    + ", ".join(
                        f"{b['category']} ({b['percentage_used']:.0f}%)" for b in close
                    )
                )
            else:
                parts.append("All category budgets are on track.")
        subs = context.get("subscriptions")
        if subs:
            parts.append(
                f"Subscriptions: {subs.get('count')} active, "
                f"₹{subs.get('monthly_cost', 0):,.2f}/month"
            )
        rec = context.get("recurring")
        if rec:
            parts.append(
                f"Recurring expenses: {rec.get('count')} active, "
                f"₹{rec.get('monthly_total', 0):,.2f}/month"
            )
        goals = context.get("goals")
        if goals:
            parts.append(
                "Goals: "
                + "; ".join(
                    f"{g.get('name')} (₹{g.get('current', 0):,.2f} of "
                    f"₹{g.get('target', 0):,.2f})"
                    for g in goals
                )
            )
        if context.get("unread_notifications"):
            parts.append(f"{context['unread_notifications']} unread notification(s)")
        return " | ".join(parts) if parts else "No financial data recorded yet."

    # ---- helpers -----------------------------------------------------------
    async def _build_context(self, user_id: str) -> dict:
        ctx: dict[str, Any] = {}
        uq = user_id_query(user_id)

        try:
            user = await self._db.users.find_one({"user_id": uq})
            if user:
                ctx["monthly_income"] = user.get("monthly_income") or 0
                if user.get("wallet_balance") is not None:
                    ctx["wallet_balance"] = user.get("wallet_balance")
                if user.get("full_name"):
                    ctx["name"] = user["full_name"]
        except Exception as e:
            logger.warning("Could not load user profile into context: %s", e)

        health = await self._db.financial_health.find_one(
            {"user_id": uq}, sort=[("calculated_at", -1)]
        )
        if health:
            ctx["financial_health"] = {
                "score": health.get("score"), "risk_level": health.get("risk_level"),
            }
        budget = await self._db.budget_intelligence.find_one(
            {"user_id": uq}, sort=[("calculated_at", -1)]
        )
        if budget:
            ctx["budget"] = {
                "score": budget.get("budget_score"),
                "categories_count": len(budget.get("categories", [])),
            }
        cash = await self._db.cash_flow_summary.find_one(
            {"user_id": uq}, sort=[("calculated_at", -1)]
        )
        if cash:
            ctx["cash_flow"] = {
                "income": cash.get("total_income"),
                "expenses": cash.get("total_expenses"),
                "net_savings": cash.get("net_savings"),
            }

        try:
            statuses = await get_budget_status(self._db, user_id)
            if statuses:
                ctx["current_budgets"] = [
                    {
                        "category": s["category"],
                        "limit": s["limit"],
                        "spent": s["spent"],
                        "state": s["state"],
                        "percentage_used": s["percentage_used"],
                    }
                    for s in statuses
                ]
        except Exception as e:
            logger.warning("Could not load current budgets into context: %s", e)

        # Current-month spending overview (drives context-aware answers even
        # when the LLM is unreachable).
        try:
            now = utc_now()
            start, end = month_bounds(now.year, now.month)
            docs = await self._db.expenses.find(
                {"user_id": uq, "date": {"$gte": start, "$lte": end}}
            ).sort("date", -1).to_list(length=1000)
            if docs:
                total = round(sum(d.get("amount", 0) for d in docs), 2)
                by_cat: dict[str, float] = {}
                for d in docs:
                    cat = d.get("category", "Other")
                    by_cat[cat] = round(by_cat.get(cat, 0) + d.get("amount", 0), 2)
                top = sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True)[:5]
                ctx["current_month_spending"] = {
                    "total": total,
                    "expense_count": len(docs),
                    "top_categories": [
                        {"category": c, "amount": a} for c, a in top
                    ],
                    "recent_expenses": [
                        {
                            "date": str(d.get("date", "")),
                            "description": d.get("description"),
                            "category": d.get("category"),
                            "amount": d.get("amount"),
                        }
                        for d in docs[:5]
                    ],
                }
        except Exception as e:
            logger.warning("Could not load current-month spending into context: %s", e)

        try:
            subs = await self._db.subscriptions.find({"user_id": uq}).to_list(length=None)
            active_subs = [s for s in subs if s.get("is_active", True)]
            if active_subs:
                ctx["subscriptions"] = {
                    "count": len(active_subs),
                    "monthly_cost": round(sum(
                        s.get("monthly_cost") or s.get("amount") or 0
                        for s in active_subs
                    ), 2),
                }
        except Exception as e:
            logger.warning("Could not load subscriptions into context: %s", e)

        try:
            recurring = await self._db.recurring_expenses.find(
                {"user_id": uq}
            ).to_list(length=None)
            active_rec = [r for r in recurring if r.get("is_active", True)]
            if active_rec:
                ctx["recurring"] = {
                    "count": len(active_rec),
                    "monthly_total": round(sum(
                        r.get("amount") or 0 for r in active_rec
                    ), 2),
                }
        except Exception as e:
            logger.warning("Could not load recurring expenses into context: %s", e)

        try:
            unread = await self._db.notifications.count_documents(
                {"user_id": uq, "read": False}
            )
            if unread:
                ctx["unread_notifications"] = unread
        except Exception as e:
            logger.warning("Could not load notifications into context: %s", e)

        try:
            goals = await self._db.financial_goals.find(
                {"user_id": uq}
            ).sort("created_at", -1).to_list(length=3)
            if goals:
                ctx["goals"] = [
                    {
                        "name": g.get("name"),
                        "target": g.get("target_amount") or 0,
                        "current": g.get("current_amount") or 0,
                        "goal_type": g.get("goal_type"),
                    }
                    for g in goals
                ]
        except Exception as e:
            logger.warning("Could not load goals into context: %s", e)

        return ctx

    def _build_messages(self, history: list, message: str, context: dict,
                        summary: str | None = None) -> list:
        system = [SYSTEM_PROMPT]
        if summary:
            system.append(f"\n## Conversation Summary\n{summary}")
        if context:
            system.append(f"\n## Current User Context\n{json.dumps(context, indent=2)}")
        system.append(f"\n## Date & Time\n{utc_now().isoformat()}")
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
