import json
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Any

def _parse_if_stringified_json(v: Any) -> Any:
    """Pre-validator helper to handle 8B model array-stringification quirks."""
    if isinstance(v, str):
        v_trimmed = v.strip()
        if v_trimmed.startswith("[") and v_trimmed.endswith("]"):
            try:
                return json.loads(v_trimmed)
            except Exception:
                pass
    return v

class JoinSpec(BaseModel):
    table: str = Field(..., description="Table name to join ('customer_data' or 'product_data')")
    on: str = Field(..., description="Key column name to join on ('customer_id' or 'product_id')")
    how: Literal["inner", "left", "right"] = Field(default="left", description="Join type")

class FilterSpec(BaseModel):
    column: str = Field(..., description="Column name to filter on")
    operator: Literal["==", "!=", ">", "<", ">=", "<=", "in"] = Field(..., description="Filter operator")
    value: Any = Field(..., description="Filter value or list of values")

class AggregationSpec(BaseModel):
    column: str = Field(..., description="Column to aggregate")
    function: Literal["sum", "mean", "count", "nunique", "min", "max"] = Field(default="sum", description="Aggregation function")
    alias: str = Field(..., description="Output column name")

class DerivedMetricSpec(BaseModel):
    formula: Literal["profit", "margin_pct", "aov"] = Field(
        ..., description="Formula: 'profit' (revenue-cost), 'margin_pct' ((revenue-cost)/revenue * 100), 'aov' (revenue/quantity)"
    )
    alias: str = Field(..., description="Output column name for the calculated metric")

class QueryPlan(BaseModel):
    thought_process: str = Field(..., description="Step-by-step logic explaining the query interpretation")
    primary_table: str = Field(default="sales_data", description="Base table for query execution")
    joins: List[JoinSpec] = Field(default_factory=list)
    filters: List[FilterSpec] = Field(default_factory=list)
    group_by: List[str] = Field(default_factory=list)
    time_granularity: Optional[Literal["month", "year", "day"]] = Field(
        None, description="Set to 'month' or 'year' when analyzing trends over time."
    )
    aggregations: List[AggregationSpec] = Field(default_factory=list)
    derived_metrics: List[DerivedMetricSpec] = Field(default_factory=list)
    chart_type: Literal["line", "bar", "pie", "area", "scatter", "table_only"] = Field(
        default="bar", description="Best chart type for displaying query results."
    )
    sort_by: Optional[str] = Field(None, description="Column name to sort by")
    ascending: bool = Field(default=False, description="Sort order")
    limit: Optional[int] = Field(None, description="Max rows to return")

    # PRE-VALIDATORS FOR 8B MODEL COMPATIBILITY
    @field_validator("joins", "filters", "group_by", "aggregations", "derived_metrics", mode="before")
    @classmethod
    def parse_array_fields(cls, v: Any) -> Any:
        return _parse_if_stringified_json(v)