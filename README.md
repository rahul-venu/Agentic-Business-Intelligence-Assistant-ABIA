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
### Graph Workflow Components
* **Planner Node**: Converts natural language into a structured `QueryPlan` JSON using Groq (`llama-3.3-70b-versatile`).
* **Validator Node**: Checks if referenced tables, columns, and filter values exist in the schema metadata before execution.
* **Executor Node**: Executes multi-table `INNER`/`LEFT` joins, row filters, `.groupby()`, and `.agg()` in Pandas.
* **Responder Node**: Formats raw Pandas outputs into clean, human-readable Markdown tables with exact non-exponentiated numbers.
* **Conditional Routing / Retry Loop**: Captures errors during validation or execution and prompts the planner to self-heal (up to 3 retries).

---

## 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **LLM Engine** | Groq API (`llama-3.3-70b-versatile`) |
| **Agent Orchestration** | LangGraph (`StateGraph`) |
| **Structured Output** | Pydantic v2 Schema Constraints |
| **Data Processing Engine** | Pandas |
| **Tracing & Observability** | LangSmith |
| **Environment / Config** | Python 3.10+, `python-dotenv` |

---

## 📁 Repository Structure

```
abia/
├── .env.example                # Template for required environment variables
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies for this project
├── app.py                      # Streamlit app
├── main.py                     # CLI entrypoint for running test queries
├── LICENSE                     # MIT License
│
├── data/                       # Local relational storage (CSV format)
|   ├── notebooks/
|   |   └── sanity_check.py     # Pure Pandas reference script for manual sanity checks
|   |
│   ├── customer_data.csv       # (customer_id, signup_date, segment, country, churned)
│   ├── product_data.csv        # (product_id, category, price, cost)
│   └── sales_data.csv          # (order_id, date, customer_id, product_id, revenue, quantity, region, channel)
|
├── eval/
│   ├── test_queries.json       # Benchmark evaluation queries
│   └── syn_datagen.py          # Synthetic dataset generator with domain consistency
|
└── src/
    ├── config/
    │   └── settings.py         # Project configuration & environment loader
    ├── schemas/
    │   └── plan_schema.py      # Pydantic QueryPlan schema definition
    ├── utils/
    │   ├── data_loader.py      # Singleton DataLoader with caching
    │   └── metadata.py         # Schema metadata & categorical sample extractor
    ├── agents/
    │   ├── planner.py          # Groq LLM Semantic Compiler
    │   ├── validator.py        # Schema validation guardrails
    │   └── executor.py         # Pure Pandas execution engine
    └── graph/
        └── workflow.py         # LangGraph State Machine & Conditional Edges
```







