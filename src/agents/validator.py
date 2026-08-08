from typing import Any, Dict, Tuple

from src.schemas.plan_schema import JoinSpec, QueryPlan


class ValidatorAgent:
    def __init__(self, metadata: Dict[str, Any]):
        self.metadata = metadata

    def _clean_col(self, col_name: str) -> str:
        """Strips table prefixes if present (e.g. 'customer_data.segment' -> 'segment')"""
        if not isinstance(col_name, str):
            return col_name
        return col_name.split(".")[-1] if "." in col_name else col_name

    def _sanitize_plan(self, plan: QueryPlan):
        """Mutates and cleans all column references inside the QueryPlan object directly."""
        if "." in plan.primary_table:
            plan.primary_table = plan.primary_table.split(".")[0]

        for f in plan.filters:
            f.column = self._clean_col(f.column)

        plan.group_by = [self._clean_col(c) for c in plan.group_by]

        for agg in plan.aggregations:
            agg.column = self._clean_col(agg.column)

        for join in plan.joins:
            join.on = self._clean_col(join.on)
            if "." in join.table:
                join.table = join.table.split(".")[0]

        if plan.sort_by:
            plan.sort_by = self._clean_col(plan.sort_by)

    def _auto_inject_missing_joins(self, plan: QueryPlan):
        """Auto-detects and adds missing joins if customer_data or product_data columns are used."""
        joined_tables = {plan.primary_table} | {j.table for j in plan.joins}

        # Collect all clean referenced columns in the plan
        referenced_cols = set(f.column for f in plan.filters)
        referenced_cols.update(plan.group_by)
        referenced_cols.update(agg.column for agg in plan.aggregations)

        # Check if customer_data columns are used but table isn't joined
        customer_cols = set(self.metadata.get("customer_data", {}).keys())
        if (referenced_cols & customer_cols) and "customer_data" not in joined_tables:
            plan.joins.append(
                JoinSpec(table="customer_data", on="customer_id", how="left")
            )
            joined_tables.add("customer_data")

        # Check if product_data columns are used but table isn't joined
        product_cols = set(self.metadata.get("product_data", {}).keys())
        if (referenced_cols & product_cols) and "product_data" not in joined_tables:
            plan.joins.append(
                JoinSpec(table="product_data", on="product_id", how="left")
            )
            joined_tables.add("product_data")

    def validate(self, plan: QueryPlan) -> tuple[bool, str]:
        # Step 1: Clean and sanitize all prefixes on the QueryPlan object
        self._sanitize_plan(plan)

        if plan.primary_table not in self.metadata:
            return False, f"Primary table '{plan.primary_table}' does not exist."

        # Step 2: Auto-inject missing table joins if LLM omitted them
        self._auto_inject_missing_joins(plan)

        available_columns = set(self.metadata[plan.primary_table].keys())

        # Step 3: Validate joins & gather all available columns
        for join in plan.joins:
            if join.table not in self.metadata:
                return False, f"Join table '{join.table}' does not exist."

            clean_join_on = self._clean_col(join.on)
            if (
                clean_join_on not in available_columns
                or clean_join_on not in self.metadata[join.table].keys()
            ):
                return False, f"Join key '{join.on}' missing from base or join table."

            available_columns.update(self.metadata[join.table].keys())

        # Step 4: Validate filters
        for f in plan.filters:
            if f.column not in available_columns:
                return (
                    False,
                    f"Filter column '{f.column}' is not available in joined tables.",
                )

        # Step 5: Validate group_by
        for col in plan.group_by:
            if col not in available_columns:
                return False, f"GroupBy column '{col}' is not available."

        # Step 6: Validate aggregations
        for agg in plan.aggregations:
            if agg.column not in available_columns:
                return False, f"Aggregation column '{agg.column}' is not available."

        return True, "Valid Plan"


# ----------------------------------------------------------------
# FOR TESTING PURPOSES
# ----------------------------------------------------------------

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
