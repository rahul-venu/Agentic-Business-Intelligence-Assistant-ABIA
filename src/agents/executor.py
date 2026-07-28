import pandas as pd
from typing import Dict
from src.schemas.plan_schema import QueryPlan

import pandas as pd
from typing import Dict
from src.schemas.plan_schema import QueryPlan

class ExecutorAgent:
    def __init__(self, dfs: Dict[str, pd.DataFrame]):
        self.dfs = dfs

    def _clean_col(self, col: str) -> str:
        if not isinstance(col, str):
            return col
        return col.split(".")[-1] if "." in col else col

    def _sanitize_plan(self, plan: QueryPlan):
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

    def execute(self, plan: QueryPlan) -> pd.DataFrame:
        # Sanitize plan before execution
        self._sanitize_plan(plan)

        df = self.dfs[plan.primary_table].copy()

        # 1. Joins
        for join in plan.joins:
            right_df = self.dfs[join.table].copy()
            df = pd.merge(df, right_df, on=join.on, how=join.how)

        # 2. Time Granularity Creation
        if plan.time_granularity and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            if plan.time_granularity == "month":
                df["month"] = df["date"].dt.to_period("M").astype(str)
                if "month" not in plan.group_by:
                    plan.group_by.insert(0, "month")
            elif plan.time_granularity == "year":
                df["year"] = df["date"].dt.year.astype(str)
                if "year" not in plan.group_by:
                    plan.group_by.insert(0, "year")

        # 3. Pre-aggregation Row Calculations
        for metric in plan.derived_metrics:
            if metric.formula == "profit":
                if "revenue" in df.columns and "cost" in df.columns:
                    df[metric.alias] = df["revenue"] - df["cost"]

        # 4. Filters
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

        # 5. GroupBy & Aggregations
        if plan.group_by or plan.aggregations:
            if plan.group_by:
                agg_dict = {agg.column: agg.function for agg in plan.aggregations}
                for metric in plan.derived_metrics:
                    if metric.formula == "profit" and metric.alias in df.columns:
                        agg_dict[metric.alias] = "sum"

                df = df.groupby(plan.group_by).agg(agg_dict).reset_index()
            else:
                res = {}
                for agg in plan.aggregations:
                    val = df[agg.column].agg(agg.function)
                    res[agg.alias] = [val]
                df = pd.DataFrame(res)

            rename_dict = {agg.column: agg.alias for agg in plan.aggregations}
            df = df.rename(columns=rename_dict)

        # 6. Post-aggregation Formula Calculations
        for metric in plan.derived_metrics:
            if metric.formula == "margin_pct":
                rev_col = next((c for c in df.columns if "revenue" in c.lower()), "revenue")
                if "cost" in df.columns and rev_col in df.columns:
                    df[metric.alias] = (((df[rev_col] - df["cost"]) / df[rev_col]) * 100).round(2)
                elif "profit" in df.columns and rev_col in df.columns:
                    df[metric.alias] = ((df["profit"] / df[rev_col]) * 100).round(2)
            elif metric.formula == "aov":
                rev_col = next((c for c in df.columns if "revenue" in c.lower()), "revenue")
                qty_col = next((c for c in df.columns if "quantity" in c.lower()), "quantity")
                if rev_col in df.columns and qty_col in df.columns:
                    df[metric.alias] = (df[rev_col] / df[qty_col]).round(2)

        # 7. Sort & Limit
        if plan.sort_by and plan.sort_by in df.columns:
            df = df.sort_values(by=plan.sort_by, ascending=plan.ascending)

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