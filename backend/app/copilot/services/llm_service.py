import logging
from typing import Any

import tiktoken
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class TokenCounter:
    _enc = tiktoken.get_encoding("cl100k_base")

    @classmethod
    def count(cls, text: str) -> int:
        return len(cls._enc.encode(text))

    @classmethod
    def truncate(cls, text: str, max_tokens: int = 3000) -> str:
        tokens = cls._enc.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return cls._enc.decode(tokens[:max_tokens])


class LLMService:
    def __init__(self):
        cfg = get_settings()
        self._model = cfg.groq_model
        self._temperature = cfg.groq_temperature
        self._max_tokens = cfg.groq_max_tokens
        self._api_key = cfg.groq_api_key

    def _get_llm(self, streaming: bool = False) -> ChatGroq:
        return ChatGroq(
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            groq_api_key=self._api_key,
            streaming=streaming,
        )

    async def generate(self, system_prompt: str, messages: list[dict],
                       tools: list[Any] | None = None) -> tuple[str, dict]:
        llm = self._get_llm()
        langchain_messages = [SystemMessage(content=system_prompt)]
        for m in messages:
            if m["role"] == "user":
                langchain_messages.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                langchain_messages.append(AIMessage(content=m["content"]))
        try:
            if tools:
                llm_with_tools = llm.bind_tools(tools)
                response = await llm_with_tools.ainvoke(langchain_messages)
            else:
                response = await llm.ainvoke(langchain_messages)
            return response.content, {
                "token_usage": self._estimate_tokens(system_prompt, messages, response.content),
            }
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again.", {"error": str(e)}

    def _estimate_tokens(self, system: str, msgs: list[dict], response: str) -> dict:
        prompt_tokens = TokenCounter.count(system) + sum(
            TokenCounter.count(m.get("content", "")) for m in msgs
        )
        completion_tokens = TokenCounter.count(response)
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

