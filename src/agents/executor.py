import pandas as pd
from typing import Dict
from src.schemas.plan_schema import QueryPlan

class ExecutorAgent:
    def __init__(self, dfs: Dict[str, pd.DataFrame]):
        self.dfs = dfs
    def execute(self, plan: QueryPlan) -> pd.DataFrame:
            """Executes the QueryPlan strictly using Pandas operations."""
            # 1. Base table copy
            df = self.dfs[plan.primary_table].copy()

            # 2. Joins
            for join in plan.joins:
                right_df = self.dfs[join.table].copy()
                df = pd.merge(df, right_df, on=join.on, how=join.how)

            # 3. Filters
            for f in plan.filters:
                if f.operator == "==":
                    df = df[df[f.column] == f.value]
                elif f.operator == "!=":
                    df = df[df[f.column] != f.value]
                elif f.operator == ">":
                    df = df[df[f.column] > f.value]
                elif f.operator == "<":
                    df = df[df[f.column] < f.value]
                elif f.operator == ">=":
                    df = df[df[f.column] >= f.value]
                elif f.operator == "<=":
                    df = df[df[f.column] <= f.value]
                elif f.operator == "in":
                    vals = f.value if isinstance(f.value, list) else [f.value]
                    df = df[df[f.column].isin(vals)]    

            # 4. Aggregations & GroupBy
            if plan.group_by or plan.aggregations:
                agg_dict = {}
                rename_dict = {}

                for agg in plan.aggregations:
                    # Store aggregated column and metric function
                    if agg.column not in agg_dict:
                        agg_dict[agg.column] = []
                    agg_dict[agg.column].append(agg.function)
                    
                if plan.group_by:
                    grouped = df.groupby(plan.group_by)
                    df = grouped.agg({agg.column: agg.function for agg in plan.aggregations}).reset_index()
                else:
                    # Global aggregation
                    res = {}
                    for agg in plan.aggregations:
                        val = df[agg.column].agg(agg.function)
                        res[agg.alias] = [val]
                    return pd.DataFrame(res)

                # Flatten multi-level columns if necessary and assign aliases
                for agg in plan.aggregations:
                    rename_dict[agg.column] = agg.alias
                df = df.rename(columns=rename_dict)

            # 5. Sorting
            if plan.sort_by and plan.sort_by in df.columns:
                df = df.sort_values(by=plan.sort_by, ascending=plan.ascending)

            # 6. Limit
            if plan.limit:
                df = df.head(plan.limit)

            return df                    


#----------------------------------------------------------------
# FOR TESTING PURPOSES
#----------------------------------------------------------------

# if __name__ == "__main__":
#     from src.utils.data_loader import DataLoader
#     from src.schemas.plan_schema import QueryPlan, AggregationSpec, FilterSpec, JoinSpec

#     # 1. Load Data
#     dfs = DataLoader.get_dataframes()
#     executor = ExecutorAgent(dfs)

#     # Test Case 1: Simple Aggregation (Total revenue by region)
#     plan_1 = QueryPlan(
#         thought_process="Calculate total revenue by region",
#         primary_table="sales_data",
#         group_by=["region"],
#         aggregations=[AggregationSpec(column="revenue", function="sum", alias="total_revenue")],
#         sort_by="total_revenue",
#         ascending=False
#     )
#     print("--- Test 1: Total Revenue by Region ---")
#     print(executor.execute(plan_1))

#     # Test Case 2: Join + Filter (Revenue by segment in Europe)
#     plan_2 = QueryPlan(
#         thought_process="Calculate revenue by segment in Europe",
#         primary_table="sales_data",
#         joins=[JoinSpec(table="customer_data", on="customer_id", how="left")],
#         filters=[FilterSpec(column="region", operator="==", value="Europe")],
#         group_by=["segment"],
#         aggregations=[AggregationSpec(column="revenue", function="sum", alias="total_revenue")]
#     )
#     print("\n--- Test 2: Revenue by Segment in Europe ---")
#     print(executor.execute(plan_2))    