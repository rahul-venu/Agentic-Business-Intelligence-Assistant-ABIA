import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from src.config.settings import settings
from src.schemas.plan_schema import QueryPlan


class PlannerAgent:
    def __init__(self):
        llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=0.0,
        )
        self.structured_llm = llm.with_structured_output(QueryPlan)

    def plan(
        self, user_query: str, schema_metadata: dict, error_context: str = None
    ) -> QueryPlan:
        metadata_str = json.dumps(schema_metadata, indent=2)

        system_content = f"""You are an expert Data Intelligence Planner.
Your task is to convert user natural language business questions into an exact JSON Query Plan.

SCHEMA METADATA:
{metadata_str}

STRICT RULES:
0. JSON STRUCTURAL FORMATTING (CRITICAL FOR TOOL CALLING):
   - Output 'group_by', 'aggregations', 'joins', 'filters', and 'derived_metrics' as NATIVE JSON ARRAYS (e.g. ["region"]), NEVER as stringified JSON strings (DO NOT use "[\"region\"]").
1. ONLY reference tables and columns listed in the schema metadata.
2. ALWAYS match string literal filter values exact values found in 'allowed_values' or 'sample_values'.
3. DO NOT compute numbers yourself. Only output execution steps.

4. DYNAMIC CONTEXTUAL COLUMN SELECTION (CRITICAL):
   - Dynamically select the most meaningful dimension columns (in 'group_by') and metric columns (in 'aggregations' or 'derived_metrics') that directly answer the user's specific intent.
   - For Financial/Profit questions: Include revenue, cost, profit, or profit margin %.
   - For Pricing/Product catalog questions: Include price, cost, category, or product_id.
   - For Customer/Churn questions: Group by customer demographics (country, segment, churned) and count customer_ids or sum sales.
   - For Volume/Activity questions: Include order counts, quantity, or channel breakdowns.

5. ENTITY GROUPBY RULE:
   - Always include the entity column being asked about (e.g., 'product_id', 'category', 'country', 'segment', 'channel') in 'group_by'.

6. TOP-N LEADERBOARD RULE:
   - For "top", "best", "worst", or ranking queries, set 'limit' to 5 (unless user specifies a number like 1 or 10) so the output provides comparison context.

7. TIME-SERIES & TREND RULE:
   - When asked for "trend", "over time", "monthly", or "yearly", set 'time_granularity' to 'month' or 'year' AND include the group/entity column in 'group_by'.

8. DERIVED BUSINESS METRICS:
   - Use derived_metrics for 'profit', 'margin_pct', or 'aov' when requested or relevant to financial performance.

9. COLUMN MAPPING RULES:
   - Use raw column names WITHOUT table prefixes (e.g., use 'region', NOT 'sales_data.region'; use 'country', NOT 'customer_data.country').
   - For geographic regions ("Europe", "Asia", "North America"), filter on 'region'.
   - For specific countries ("Germany", "USA", "UK", "India"), filter on 'country'.

10. DYNAMIC CHART SELECTION:
   - Use 'line' for trends, 'bar' for categorical rankings, 'pie' for share/distribution, 'scatter' for correlations.

11. MANDATORY TABLE JOIN RULES:
   - If referencing 'segment', 'country', or 'churned', you MUST join 'customer_data' on 'customer_id'.
   - If referencing 'category', 'price', or 'cost', you MUST join 'product_data' on 'product_id'.   
"""
        if error_context:
            system_content += f"\n\nPREVIOUS ATTEMPT FAILED WITH ERROR:\n{error_context}\nPlease correct the query plan to fix this error."

        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_query),
        ]

        return self.structured_llm.invoke(messages)


# ----------------------------------------------------------------
# FOR TESTING PURPOSES
# ----------------------------------------------------------------

# if __name__ == "__main__":
#     from src.utils.data_loader import DataLoader
#     from src.utils.metadata import extract_schema_metadata

#     dfs = DataLoader.get_dataframes()
#     metadata = extract_schema_metadata(dfs)

#     planner = PlannerAgent()

#     query = "Total revenue by region"
#     print("=" * 60)
#     print(f"Testing Query: {query}")
#     print("=" * 60)

# plan = planner.plan(user_query=query, schema_metadata=metadata)
# print(json.dumps(plan.model_dump(), indent=2))
