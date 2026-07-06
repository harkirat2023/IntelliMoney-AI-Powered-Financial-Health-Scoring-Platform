# LangChain AI Copilot

**Phase:** 11 | **Version:** 1.11

## Overview

The LangChain AI Copilot is a conversational AI assistant embedded within IntelliMoney. It leverages OpenAI's language models through a LangChain orchestration layer, combining Retrieval-Augmented Generation (RAG) via FAISS vector storage, conversation memory with automatic summarization, and a 11-tool registry for financial domain operations. The module implements injection detection, PII masking, and context building to ensure secure and relevant responses. It comprises 5 models, 5 repositories, 5 services, and 7 REST endpoints consumed by 4 frontend pages.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND                                     │
│                                                                         │
│  ┌────────────────┐ ┌──────────────────┐ ┌──────────────────────────┐  │
│  │CopilotChat     │ │CopilotHistory    │ │CopilotSettings           │  │
│  │Page            │ │Page              │ │Page                      │  │
│  └───────┬────────┘ └────────┬─────────┘ └────────────┬─────────────┘  │
│          │                   │                        │                 │
│  ┌───────┴───────────────────┴────────────────────────┴──────────────┐ │
│  │                    CopilotLayout (3-item nav)                     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  CopilotHistoryDetailPage                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
├──────────────────────┼─────────────────────────────────────────────────┤
│                  API │ 7 routes                                        │
├──────────────────────┼─────────────────────────────────────────────────┤
│                       BACKEND                                          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     CopilotService (orchestrator)               │   │
│  │  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐   │   │
│  │  │ Injection   │    │ PII Masking  │    │ Context Builder  │   │   │
│  │  │ Detection   │    │              │    │                  │   │   │
│  │  └─────────────┘    └──────────────┘    └──────────────────┘   │   │
│  │  ┌─────────────┐    ┌──────────────┐                          │   │
│  │  │ Tool        │    │ Response     │                          │   │
│  │  │ Execution   │    │ Formatting   │                          │   │
│  │  └─────────────┘    └──────────────┘                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌──────────────┐  ┌────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  LLMService  │  │ RAGService │  │ MemoryService│  │ToolRegistry│  │
│  │  (tiktoken)  │  │ (FAISS)    │  │(auto-summary)│  │ (11 tools) │  │
│  └──────────────┘  └────────────┘  └──────────────┘  └────────────┘  │
│                                                                         │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────┐ │
│  │ChatSession │ │ChatMessage │ │Conversation│ │Conversation│ │AiFeed│ │
│  │Repo        │ │Repo        │ │Memory Repo │ │Summary Repo│ │backR │ │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └──────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### Models (5)

| Model | Description |
|---|---|
| **ChatSession** | Conversation session metadata |
| **ChatMessage** | Individual message within a session |
| **ConversationMemory** | Short-term conversation context |
| **ConversationSummary** | Auto-generated summaries for long sessions |
| **AiFeedback** | User feedback on copilot responses |

### Repositories (5)

One repository per model.

### Services (5)

| Service | File / Responsibility |
|---|---|
| **LLMService** | OpenAI integration with `tiktoken`-based token counting; configurable model, max tokens, temperature |
| **RAGService** | FAISS vector store for retrieval-augmented generation |
| **MemoryService** | Manages conversation context; auto-summarization triggers at 10 messages |
| **ToolRegistry** | Registers and dispatches 11 financial tools (see below) |
| **CopilotService** | Orchestrator: injection detection → PII masking → context building → tool execution → response formatting |

### Tool Registry (11 tools)

| Tool | Description |
|---|---|
| `get_spending_summary` | Retrieve spending by period |
| `get_budget_status` | Current budget status |
| `get_financial_score` | Financial health score |
| `get_recommendations` | Financial recommendations |
| `get_transactions` | Transaction history |
| `create_expense` | Record a new expense |
| `get_anomalies` | Detect anomalous transactions |
| `get_report` | Generate financial report |
| `get_goal_progress` | Goal tracking status |
| `get_upcoming_bills` | Upcoming bill payments |
| `get_subscription_insights` | Subscription analysis |

### System Prompts

Two prompts govern copilot behavior:

- **SYSTEM_PROMPT** — Base personality and behavior guidelines.
- **FINANCIAL_CONTEXT_PROMPT** — Injects financial domain context; contains an injection guard that detects and blocks prompt injection attempts.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/copilot/chat` | Send message, receive response |
| GET | `/copilot/sessions` | List all sessions |
| GET | `/copilot/sessions/{id}` | Get session messages |
| DELETE | `/copilot/sessions` | Clear all sessions |
| POST | `/copilot/feedback` | Submit response feedback |
| GET | `/copilot/suggestions` | Get suggested questions |
| GET | `/copilot/settings` | Get copilot configuration |

## Frontend Pages & Layout

### Pages (4)

| Page | Description |
|---|---|
| **CopilotChatPage** | Main chat interface |
| **CopilotHistoryPage** | Session history list |
| **CopilotHistoryDetailPage** | Individual session detail |
| **CopilotSettingsPage** | Copilot configuration UI |

### Layout

**CopilotLayout** provides a 3-item navigation header.

## Event Types

No events published by this module.

## Configuration

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API authentication key | — |
| `OPENAI_MODEL` | Language model identifier | `gpt-4` |
| `OPENAI_MAX_TOKENS` | Maximum tokens per response | `2048` |
| `OPENAI_TEMPERATURE` | Response randomness | `0.7` |

## Status & Version

| Property | Value |
|---|---|
| Phase | 11 |
| Version | 1.11 |
| Backend directory | `backend/app/copilot/` |
| Models | 5 |
| Repositories | 5 |
| Services | 5 |
| Tools | 11 |
| Endpoints | 7 |
| Frontend pages | 4 |
| Auto-summarization threshold | 10 messages |
| Vector store | FAISS |
