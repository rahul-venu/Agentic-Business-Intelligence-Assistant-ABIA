# ABIA: Agentic Business Intelligence Assistant & Dashboard

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Orchestration - LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![LLM - Groq Llama--3](https://img.shields.io/badge/LLM-Groq%20Llama--3-green.svg)](https://groq.com/)
[![Web UI - Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Visualization - Plotly](https://img.shields.io/badge/Visualization-Plotly-3F4F75.svg)](https://plotly.com/)
[![Observability - LangSmith](https://img.shields.io/badge/Observability-LangSmith-blueviolet.svg)](https://www.langchain.com/langsmith)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**ABIA** (Agentic Business Intelligence Assistant) is an enterprise-grade, stateful AI system designed to convert natural language business queries into executable analytical plans over relational datasets.

ABIA eliminates the two biggest risks in LLM-powered analytics: **Mathematical Hallucinations** and **Unsafe Dynamic Code Execution (`exec()`)**.

---

## 🎯 Core Architectural Principles

1. **Zero Math Hallucinations**: The LLM acts strictly as a **Semantic Compiler** that outputs a structured, strongly typed Pydantic `QueryPlan` (JSON). **Pandas** performs 100% of arithmetic, table joins, row filtering, grouping, derived metric formulas, and aggregations.
2. **Deterministic Execution Safety**: Prevents code injection risks by executing pre-validated Pydantic execution plans rather than dynamically generating and running Python scripts.
3. **Self-Healing State Graph**: Powered by **LangGraph**. If an execution plan fails schema validation or Pandas processing, the error is fed back into the Planner node for automatic self-correction (up to 3 retries).
4. **Auto-Injecting Join Guardrail**: Automatically detects missing table references and injects required relational joins (`customer_data`, `product_data`) if omitted by the LLM.
5. **Token Efficiency**: Full datasets are never sent to the LLM. Ingests lightweight schema metadata (column types and domain sample values), keeping prompts compact (~700–800 tokens) and fitting within free-tier API rate limits.

---

## 🏗 System Architecture

ABIA is built as a stateful cyclic graph using **LangGraph**:

```text
                  ┌────────────────────────┐
                  │       User Query       │
                  └───────────┬────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │   Planner Node   │◄─────────────────┐
                     │  (Groq LLM Plan) │                  │
                     └────────┬─────────┘                  │
                              │                            │
                              ▼                            │
                     ┌──────────────────┐                  │
                     │  Validator Node  ├─(Invalid Plan)───┤ (Auto-Retry Loop)
                     │(Schema Guardrails)                  │
                     └────────┬─────────┘                  │
                              │ (Valid Plan)               │
                              ▼                            │
                     ┌──────────────────┐                  │
                     │  Executor Node   ├─(Execution Err)──┘
                     │ (Pandas Engine)  │
                     └────────┬─────────┘
                              │ (Execution Success)
                              ▼
                     ┌───────────────────┐
                     │  Responder Node   │
                     │(Executive Insight)│
                     └────────┬──────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │        Streamlit UI          │
               │ (KPI Cards + Plotly Visuals) │
               └──────────────────────────────┘
```

## 🛠 Tech Stack
Layer	                Technology
LLM Engine	            Groq API (llama-3.3-70b-versatile / llama-3.1-8b-instant)
Agent Orchestration	    LangGraph (StateGraph)
Schema Validation	    Pydantic v2 (Pre-validated array parsing)
Data Engine	Pandas      (Vectorized multi-table operations)
Interactive UI	        Streamlit (Custom CSS, secrets handler, responsive layout)
Data Visualization	    Plotly Express (Interactive Line, Bar, Pie, Scatter, Area charts)
Observability	        LangSmith (Full state & prompt execution tracing)

## 📁 Repository Structure

```text
abia/
├── .env.example                # Environment variable configuration template
├── .gitignore                  # Git ignore rules (blocks .env and .venv/)
├── LICENSE                     # MIT License
├── README.md                   # System documentation
├── requirements.txt            # Python dependencies
├── app.py                      # Interactive Streamlit Web App & Executive Dashboard
├── main.py                     # CLI entrypoint for batch benchmark evaluation
│
├── data/                       # Local relational storage (CSV format)
│   ├── customer_data.csv       # (customer_id, signup_date, segment, country, churned)
│   ├── product_data.csv        # (product_id, category, price, cost)
│   ├── sales_data.csv          # (order_id, date, customer_id, product_id, revenue
quantity, region, channel)
│   └── notebooks/
│       └── sanity_check.py     # Pure Pandas ground-truth verification script
│
├── eval/
│   ├── test_queries.json       # Benchmark evaluation query suite
│   └── syn_datagen.py          # Domain-consistent synthetic dataset generator
│
└── src/
    ├── config/
    │   └── settings.py         # Application configuration loader
    ├── schemas/
    │   └── plan_schema.py      # Pydantic QueryPlan schema with array pre-validators
    ├── utils/
    │   ├── data_loader.py      # Singleton DataLoader
    │   └── metadata.py         # Schema metadata & categorical sample extractor
    ├── agents/
    │   ├── planner.py          # Groq LLM Semantic Compiler
    │   ├── validator.py        # Prefix-tolerant guardrail agent with Auto-Join injection
    │   └── executor.py         # Pure Pandas multi-metric execution engine
    └── graph/
        └── workflow.py         # LangGraph state machine & responder node
```
## 🚀 Quickstart Guide

## 1. Prerequisites

Python 3.10+

Groq API Key (_[Get a free key here](https://groq.com)_)

LangSmith API Key (*Optional, for execution tracing*)

## 2. Installation

Clone the repository and set up your virtual environment:

```bash
# Clone repository
git clone https://github.com/your-username/abia.git
cd abia

# Create virtual environment
python -m venv .venv

# Activate virtual environment

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Environment Setup

Copy .env.example to .env and fill in your API keys:
```bash
cp .env.example .env
```

```Env

GROQ_API_KEY="gsk_your_groq_api_key_here"
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_API_KEY="lsv2_your_langsmith_api_key_here"
LANGCHAIN_PROJECT="ABIA"
``` 
## 4. Generate Datasets

Generate domain-consistent, correlated synthetic CSV datasets inside data/:

```bash
python eval/syn_datagen.py
```

## 💻 Running the System

Option A: Interactive Streamlit Web Dashboard (Recommended)

Launch the web app featuring adaptive KPI summary cards, custom CSS styling, dynamic Plotly charts, and one-click CSV exporting:

```bash
streamlit run app.py
```

Option B: CLI Batch Test Runner

Execute benchmark questions defined in eval/test_queries.json:
```bash
python main.py
```

## 🌐 Live Cloud Deployment

ABIA is designed to deploy to Streamlit Community Cloud with secret management and full LangSmith tracing.
Streamlit Secrets Configuration
Add the following TOML block under **App Settings** → **Secrets:**
```Toml
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_API_KEY = "lsv2_your_actual_langsmith_api_key_here"
LANGCHAIN_PROJECT = "ABIA"
```

**Note:** `app.py` includes an automated runtime secrets handler that copies `st.secrets` into `os.environ`, ensuring LangChain, Groq, and LangSmith initialize without configuration errors.

## 🧪 Ground-Truth Sanity Checking

To verify that agent execution matches raw dataset calculations down to the cent, run the pure Pandas benchmark script:
```bash
python data/notebooks/sanity_check.py
```

### 📈 Supported Business Analytics Capabilities

<table border="0" style="border-collapse: collapse; border: none; width: 100%;">
  <thead>
    <tr style="border: none;">
      <th align="left" style="border: none; padding: 8px;">Capability</th>
      <th align="left" style="border: none; padding: 8px;">Example User Query</th>
      <th align="left" style="border: none; padding: 8px;">Engine Action</th>
      <th align="left" style="border: none; padding: 8px;">Visual Output</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold;">Regional Sales</td>
      <td style="border: none; padding: 8px; font-style: italic;">"Total revenue by region"</td>
      <td style="border: none; padding: 8px;">Group by <code>region</code>, sum <code>revenue</code></td>
      <td style="border: none; padding: 8px;">📊 Bar Chart + KPI Cards</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold;">Trend Comparisons</td>
      <td style="border: none; padding: 8px; font-style: italic;">"Revenue trend for Asia compared to Europe"</td>
      <td style="border: none; padding: 8px;">Extract <code>month</code> from <code>date</code>, group by <code>month</code> + <code>region</code>, pre-aggregate sums</td>
      <td style="border: none; padding: 8px;">📈 Multi-Series Line Chart</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold;">Profitability</td>
      <td style="border: none; padding: 8px; font-style: italic;">"Top 5 products by profit margin"</td>
      <td style="border: none; padding: 8px;">Compute <code>(revenue - cost) / revenue * 100</code>, sort descending</td>
      <td style="border: none; padding: 8px;">📊 Leaderboard Bar Chart</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold;">Churn Analysis</td>
      <td style="border: none; padding: 8px; font-style: italic;">"Revenue generated by churned vs active customers"</td>
      <td style="border: none; padding: 8px;">Join <code>customer_data</code>, group by <code>churned</code></td>
      <td style="border: none; padding: 8px;">🍩 Donut Chart + Insights</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold;">Market Share</td>
      <td style="border: none; padding: 8px; font-style: italic;">"Revenue share by sales channel"</td>
      <td style="border: none; padding: 8px;">Group by <code>channel</code>, compute proportions</td>
      <td style="border: none; padding: 8px;">🍩 Donut Chart</td>
    </tr>
  </tbody>
</table>

## 🛡 Observability & Tracing

Full end-to-end execution tracing is captured via LangSmith. Every system prompt, structured JSON output, validation state, retry loop, and Pandas execution state is logged.
View execution logs on your LangSmith Dashboard under the project ABIA.

## 📜 License
Distributed under the MIT License. See LICENSE for details.
