from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any

class JoinSpec(BaseModel):
    table: str = Field(..., description="Table name to join (e.g. 'customer_data', 'product_data')")
    on: str = Field(..., description="Key column to join on (e.g. 'customer_id', 'product_id')")
    how: Literal["inner", "left", "right"] = Field(default="left", description="Join type")

class FilterSpec(BaseModel):
    column: str = Field(..., description="Column name to filter")
    operator: Literal["==", "!=", ">", "<", ">=", "<=", "in"] = Field(..., description="Filter comparison operator")
    value: Any = Field(..., description="Filter value. Use list for 'in' operator.")

class AggregationSpec(BaseModel):
    column: str = Field(..., description="Column to perform aggregation on")
    function: Literal["sum", "mean", "count", "nunique", "min", "max"] = Field(..., description="Pandas aggregation function")
    alias: str = Field(..., description="Output column name after aggregation")

class QueryPlan(BaseModel):
    thought_process: str = Field(..., description="Step-by-step explanation of query interpretation")
    primary_table: str = Field(default="sales_data", description="Base table to start processing from")
    joins: List[JoinSpec] = Field(default_factory=list, description="Joins to execute in order")
    filters: List[FilterSpec] = Field(default_factory=list, description="Filtering conditions to apply")
    group_by: List[str] = Field(default_factory=list, description="Columns to group by")
    aggregations: List[AggregationSpec] = Field(default_factory=list, description="Aggregations to compute")
    sort_by: Optional[str] = Field(None, description="Column name to sort results by")
    ascending: bool = Field(default=False, description="Sort order (False = descending)")
    limit: Optional[int] = Field(None, description="Maximum number of rows to return (e.g. for Top N)")