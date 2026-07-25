import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.schemas.plan_schema import QueryPlan
from src.config.settings import settings

class PlannerAgent:
    def __init__(self):
        llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=0.0
        )
        self.structured_llm = llm.with_structured_output(QueryPlan)

    def plan(self, user_query: str, schema_metadata: dict, error_context: str = None) -> QueryPlan:
        # 1. Format metadata as clean JSON
        metadata_str = json.dumps(schema_metadata, indent=2)

        # 2. Build system message string using standard Python string formatting
        system_content = f"""You are an expert Data Intelligence Planner.
Your task is to convert user natural language business questions into an exact JSON Query Plan.

SCHEMA METADATA:
{metadata_str}

STRICT RULES:
1. ONLY reference tables and columns listed in the schema metadata.
2. ALWAYS match string literal filter values exact values found in 'allowed_values' or 'sample_values'.
3. DO NOT compute numbers yourself. Only output execution steps.
4. GROUPBY RULE FOR TOP-N QUERIES:
   - When asked for "top product", "top category", "top customer", etc., you MUST include the target entity column (e.g., 'product_id', 'category', 'customer_id') in the 'group_by' list.
5. COLUMN MAPPING RULES:
   - For geographic regions ("Europe", "APAC", "North America"), filter on 'sales_data.region'.
   - For specific countries ("India", "USA", "UK", "Germany"), filter on 'customer_data.country'.
6. If joining tables:
   - 'sales_data' joins 'customer_data' on 'customer_id'
   - 'sales_data' joins 'product_data' on 'product_id'
"""

        # 3. Safely append error context if retry is triggered
        if error_context:
            system_content += f"\n\nPREVIOUS ATTEMPT FAILED WITH ERROR:\n{error_context}\nPlease correct the query plan to fix this error."

        # 4. Construct direct message objects (No template parsing issues!)
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_query)
        ]

        # 5. Invoke structured LLM directly
        return self.structured_llm.invoke(messages)
    

#----------------------------------------------------------------
# FOR TESTING PURPOSES
#----------------------------------------------------------------

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