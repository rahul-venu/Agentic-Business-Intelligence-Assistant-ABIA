from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END
import pandas as pd

from src.schemas.plan_schema import QueryPlan
from src.agents.planner import PlannerAgent
from src.agents.validator import ValidatorAgent
from src.agents.executor import ExecutorAgent
from src.utils.data_loader import DataLoader
from src.utils.metadata import extract_schema_metadata
from src.config.settings import settings

class ABIAState(TypedDict, total=False):
    user_query: str
    plan: Optional[QueryPlan]
    result_df: Optional[pd.DataFrame]
    formatted_result: Optional[str]
    error: Optional[str]
    retry_count: int 

def build_workflow():
    dfs = DataLoader.get_dataframes()
    metadata = extract_schema_metadata(dfs)

    planner = PlannerAgent()
    validator = ValidatorAgent(metadata)
    executor = ExecutorAgent(dfs)  

    def planner_node(state: ABIAState) -> Dict[str, Any]:
        user_query = state.get("user_query", "")
        retry_count = state.get("retry_count", 0)
        error = state.get("error")

        plan = planner.plan(
            user_query=user_query,
            schema_metadata=metadata,
            error_context=error if error else None
        )
        
        return {
            "user_query": user_query,
            "plan": plan, 
            "error": None, 
            "retry_count": retry_count + 1
        }

    def validator_node(state: ABIAState) -> Dict[str, Any]:
        plan = state.get("plan")
        if not plan:
            return {"error": "No query plan generated."}

        is_valid, err_msg = validator.validate(plan)
        if not is_valid:
            return {"error": f"Validation Error: {err_msg}"}
        return {"error": None}

    def executor_node(state: ABIAState) -> Dict[str, Any]:
        plan = state.get("plan")
        if not plan:
            return {"error": "No query plan available for execution."}

        try:
            res_df = executor.execute(plan)
            return {"result_df": res_df, "error": None}
        except Exception as e:
            return {"error": f"Pandas Execution Error: {str(e)}"}

    def responder_node(state: ABIAState) -> Dict[str, Any]:
        df = state.get("result_df")
        plan = state.get("plan")
        
        if df is None or df.empty:
            summary = "No data matched the query conditions."
        else:
            thought = plan.thought_process if plan else ""
            summary = f"### Logic Explanation\n{thought}\n\n### Query Result\n"
            summary += df.to_markdown(index=False, floatfmt=",.2f")
            
        return {"formatted_result": summary}

    # Conditional Routing Logic
    def route_validation(state: ABIAState) -> str:
        if state.get("error"):
            if state.get("retry_count", 0) <= settings.MAX_RETRIES:
                return "planner"
            return END
        return "executor"

    def route_execution(state: ABIAState) -> str:
        if state.get("error"):
            if state.get("retry_count", 0) <= settings.MAX_RETRIES:
                return "planner"
            return END
        return "responder"
    
    # Define Graph
    workflow = StateGraph(ABIAState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("responder", responder_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "validator")
    
    workflow.add_conditional_edges("validator", route_validation)
    workflow.add_conditional_edges("executor", route_execution)
    
    workflow.add_edge("responder", END)

    return workflow.compile()