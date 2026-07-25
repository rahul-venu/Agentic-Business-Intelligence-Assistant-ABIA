# ABIA: Agentic Business Intelligence Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Groq Llama-3.3-70B](https://img.shields.io/badge/LLM-Groq%20Llama--3.3--70B-green.svg)](https://groq.com/)
[![LangSmith](https://img.shields.io/badge/Observability-LangSmith-blueviolet.svg)](https://www.langchain.com/langsmith)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, stateful **Agentic Business Intelligence Assistant** designed to query complex multi-table relational datasets using natural language. 

ABIA solves the two most significant hurdles in LLM-powered data analytics: **Mathematical Hallucinations** and **Dynamic Code Execution Safety Risks**.

---

## 🎯 Core Engineering Principles

1. **Zero Math Hallucinations**: The LLM acts strictly as a **Semantic Compiler** (generating structured JSON Query Plans). 100% of arithmetic, table joins, filtering, and aggregations are handled deterministically by **Pandas**.
2. **Deterministic Execution Safety**: Eliminates the safety hazards of dynamic Python `exec()` / `eval()` by executing strictly typed Pydantic Query Plans.
3. **Self-Healing Loop**: Powered by a stateful **LangGraph** flow. If a query plan fails schema validation or execution, the system automatically loops error messages back to the LLM for self-correction.
4. **Token Efficiency**: Full DataFrames are **never** passed to the LLM. The system dynamically extracts schema metadata, column types, and unique domain samples, keeping token usage minimal and fitting within free-tier rate limits.

---

## 🏗 System Architecture
```
The assistant is built as a stateful cyclic graph using LangGraph:

         ┌──────────────────────┐
         │      User Query      │
         └──────────┬───────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│             Planner Node              │◄─────────────────┐
│           (Groq LLM Plan)             │                  │
└──────────────────┬────────────────────┘                  │
                   │                                       │
                   ▼                                       │
┌───────────────────────────────────────┐                  │
│            Validator Node             │                  │
│          (Schema Guardrails)          │                  │
└──────────────────┬────────────────────┘                  │
                   │                                       │
                   ├───────────────(Invalid Plan)──────────┤
                   │                                       │ (Auto-Retry Loop)
                   │ (Valid Plan)                          │
                   ▼                                       │
┌───────────────────────────────────────┐                  │
│             Executor Node             │                  │
│         (Pandas Data Engine)          │                  │
└──────────────────┬────────────────────┘                  │
                   │                                       │
                   ├───────────────(Execution Err)─────────┘
                   │
                   │ (Execution Success)
                   ▼
┌───────────────────────────────────────┐
│            Responder Node             │
│           (Markdown Table)            │
└───────────────────────────────────────┘
```
