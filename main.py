import json

from langchain_core.tracers.langchain import wait_for_all_tracers
from src.graph.workflow import build_workflow


def run_app():
    app = build_workflow()

    # Load test queries
    with open("eval/test_queries.json") as f:
        queries = json.load(f)

    for item in queries:
        query = item["query"]
        print("=" * 60)
        print(f"USER QUERY: {query}")
        print("=" * 60)

        initial_state = {"user_query": query, "retry_count": 0, "error": None}

        # Execute Graph
        final_state = app.invoke(initial_state)

        if final_state.get("error"):
            print(f"Execution Failed: {final_state['error']}")
        else:
            print(final_state["formatted_result"])
            print("\n")


if __name__ == "__main__":
    try:
        run_app()
    finally:
        # Flush LangSmith traces before Python shuts down
        wait_for_all_tracers()
