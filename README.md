# ABIA: Agentic Business Intelligence Assistant 

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

<table border="0" style="border-collapse: collapse; border: none; width: 100%;">
  <tbody>
    <tr style="border: none;">
      <td valign="top" style="border: none; padding: 12px 16px 12px 8px; font-weight: bold !important; white-space: nowrap;">1. Zero Math Hallucinations</td>
      <td valign="top" style="border: none; padding: 12px 8px;">The LLM acts strictly as a <b>Semantic Compiler</b> that outputs a structured, strongly typed Pydantic <code>QueryPlan</code> (JSON). <b>Pandas</b> performs 100% of arithmetic, table joins, row filtering, grouping, derived metric formulas, and aggregations.</td>
    </tr>
    <tr style="border: none;">
      <td valign="top" style="border: none; padding: 12px 16px 12px 8px; font-weight: bold !important; white-space: nowrap;">2. Deterministic Execution Safety</td>
      <td valign="top" style="border: none; padding: 12px 8px;">Prevents code injection risks by executing pre-validated Pydantic execution plans rather than dynamically generating and running Python scripts.</td>
    </tr>
    <tr style="border: none;">
      <td valign="top" style="border: none; padding: 12px 16px 12px 8px; font-weight: bold !important; white-space: nowrap;">3. Self-Healing State Graph</td>
      <td valign="top" style="border: none; padding: 12px 8px;">Powered by <b>LangGraph</b>. If an execution plan fails schema validation or Pandas processing, the error is fed back into the Planner node for automatic self-correction (up to 3 retries).</td>
    </tr>
    <tr style="border: none;">
      <td valign="top" style="border: none; padding: 12px 16px 12px 8px; font-weight: bold !important; white-space: nowrap;">4. Auto-Injecting Join Guardrail</td>
      <td valign="top" style="border: none; padding: 12px 8px;">Automatically detects missing table references and injects required relational joins (<code>customer_data</code>, <code>product_data</code>) if omitted by the LLM.</td>
    </tr>
    <tr style="border: none;">
      <td valign="top" style="border: none; padding: 12px 16px 12px 8px; font-weight: bold !important; white-space: nowrap;">5. Token Efficiency</td>
      <td valign="top" style="border: none; padding: 12px 8px;">Full datasets are never sent to the LLM. Ingests lightweight schema metadata (column types and domain sample values), keeping prompts compact (~700–800 tokens) and fitting within free-tier API rate limits.</td>
    </tr>
  </tbody>
</table>

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

---
### 🛠 Tech Stack

<table border="0" style="border-collapse: collapse; border: none; width: 100%;">
  <thead>
    <tr style="border: none;">
      <th align="left" style="border: none; padding: 8px; width: 30%; font-weight: bold !important;">Layer</th>
      <th align="left" style="border: none; padding: 8px; width: 70%; font-weight: bold !important;">Technology</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold !important;">LLM Engine</td>
      <td style="border: none; padding: 8px;">Groq API (<code>llama-3.1-8b-instant</code> / <code>llama-3.3-70b-versatile</code>)</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold !important;">Agent Orchestration</td>
      <td style="border: none; padding: 8px;">LangGraph (<code>StateGraph</code>)</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold !important;">Schema Validation</td>
      <td style="border: none; padding: 8px;">Pydantic v2 (Pre-validated array parsing)</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold !important;">Data Engine</td>
      <td style="border: none; padding: 8px;">Pandas (Vectorized multi-table operations)</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold !important;">Interactive UI</td>
      <td style="border: none; padding: 8px;">Streamlit (Custom CSS, secrets handler, responsive layout)</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold !important;">Data Visualization</td>
      <td style="border: none; padding: 8px;">Plotly Express (Interactive Line, Bar, Pie, Scatter, Area charts)</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold !important;">Observability</td>
      <td style="border: none; padding: 8px;">LangSmith (Full state & prompt execution tracing)</td>
    </tr>
  </tbody>
</table>

---
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
│   ├── sales_data.csv          # (order_id, date, customer_id, product_id, revenue, quantity,  
|   |                              region, channel)
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

---
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
---
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
---
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

---
## 🧪 Ground-Truth Sanity Checking

To verify that agent execution matches raw dataset calculations down to the cent, run the pure Pandas benchmark script:
```bash
python data/notebooks/sanity_check.py
```

---
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
      <td style="border: none; padding: 8px; text-align: center;">📊 Bar Chart + KPI Cards</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold;">Trend Comparisons</td>
      <td style="border: none; padding: 8px; font-style: italic;">"Revenue trend for Asia compared to Europe"</td>
      <td style="border: none; padding: 8px;">Extract <code>month</code> from <code>date</code>, group by <code>month</code> + <code>region</code>, pre-aggregate sums</td>
      <td style="border: none; padding: 8px; text-align: center;">📈 Multi-Series Line Chart</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold;">Profitability</td>
      <td style="border: none; padding: 8px; font-style: italic;">"Top 5 products by profit margin"</td>
      <td style="border: none; padding: 8px;">Compute <code>(revenue - cost) / revenue * 100</code>, sort descending</td>
      <td style="border: none; padding: 8px; text-align: center;">📊 Leaderboard Bar Chart</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold;">Churn Analysis</td>
      <td style="border: none; padding: 8px; font-style: italic;">"Revenue generated by churned vs active customers"</td>
      <td style="border: none; padding: 8px;">Join <code>customer_data</code>, group by <code>churned</code></td>
      <td style="border: none; padding: 8px; text-align: center;">🍩 Donut Chart + Insights</td>
    </tr>
    <tr style="border: none;">
      <td style="border: none; padding: 8px; font-weight: bold;">Market Share</td>
      <td style="border: none; padding: 8px; font-style: italic;">"Revenue share by sales channel"</td>
      <td style="border: none; padding: 8px;">Group by <code>channel</code>, compute proportions</td>
      <td style="border: none; padding: 8px; text-align: center;">🍩 Donut Chart</td>
    </tr>
  </tbody>
</table>

---
## 🛡 Observability & Tracing

Full end-to-end execution tracing is captured via LangSmith. Every system prompt, structured JSON output, validation state, retry loop, and Pandas execution state is logged.
View execution logs on your LangSmith Dashboard under the project ABIA.

---
## 📜 License
Distributed under the MIT License. See _[LICENSE](https://github.com/rahul-venu/Agentic-Business-Intelligence-Assistant-ABIA/blob/main/LICENSE)_ for details.
