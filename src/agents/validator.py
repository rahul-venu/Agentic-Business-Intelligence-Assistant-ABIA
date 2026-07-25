from src.schemas.plan_schema import QueryPlan
from typing import Dict, Any, Tuple

class ValidatorAgent:
    def __init__(self, metadata: Dict[str, Any]):
        self.metadata = metadata

    def validate(self, plan: QueryPlan) -> Tuple[bool, str]:
        """Validates the QueryPlan against system metadata before execution."""
        # 1. Validate primary table
        if plan.primary_table not in self.metadata:
            return False, f"Primary table '{plan.primary_table}' does not exist."

        available_columns = set(self.metadata[plan.primary_table].keys())
        active_tables = {plan.primary_table}

        # 2. Validate joins
        for join in plan.joins:
            if join.table not in self.metadata:
                return False, f"Join table '{join.table}' does not exist."
            if join.on not in available_columns or join.on not in self.metadata[join.table].keys():
                return False, f"Join key '{join.on}' missing from base or join table."
            active_tables.add(join.table)
            available_columns.update(self.metadata[join.table].keys())

        # 3. Validate filters
        for f in plan.filters:
            if f.column not in available_columns:
                return False, f"Filter column '{f.column}' is not available in joined tables."

        # 4. Validate group_by
        for col in plan.group_by:
            if col not in available_columns:
                return False, f"GroupBy column '{col}' is not available."

        # 5. Validate aggregations
        for agg in plan.aggregations:
            if agg.column not in available_columns:
                return False, f"Aggregation column '{agg.column}' is not available."

        return True, "Valid Plan"


#----------------------------------------------------------------
# FOR TESTING PURPOSES
#----------------------------------------------------------------

# if __name__ == "__main__":
#     from src.utils.data_loader import DataLoader
#     from src.utils.metadata import extract_schema_metadata
#     from src.schemas.plan_schema import QueryPlan, AggregationSpec

#     # 1. Load schema metadata
#     dfs = DataLoader.get_dataframes()
#     metadata = extract_schema_metadata(dfs)

#     # 2. Instantiate Validator
#     validator = ValidatorAgent(metadata)

#     # Test Case 1: Valid Plan
#     valid_plan = QueryPlan(
#         thought_process="Valid query for revenue by region",
#         primary_table="sales_data",
#         group_by=["region"], # This column exists
#         aggregations=[AggregationSpec(column="revenue", function="sum", alias="total_revenue")]
#     )
#     is_valid, msg = validator.validate(valid_plan)
#     print(f"Test 1 (Valid Plan)   -> Valid: {is_valid} | Result: {msg}")

#     # Test Case 2: Invalid Plan (Non-existent column)
#     invalid_plan = QueryPlan(
#         thought_process="Invalid query referencing missing column",
#         primary_table="sales_data",
#         group_by=["fake_column_name"], # This column does not exist
#         aggregations=[AggregationSpec(column="revenue", function="sum", alias="total_revenue")]
#     )
#     is_valid, msg = validator.validate(invalid_plan)
#     print(f"Test 2 (Invalid Plan) -> Valid: {is_valid} | Result: {msg}")        