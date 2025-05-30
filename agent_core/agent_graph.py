from langgraph.graph import StateGraph, END
from .graph_state import AgentState
from .graph_nodes import (
    detect_urls_node,
    request_user_confirmation_node,
    prepare_next_url_node,
    process_url_node,
    final_report_node
)

def should_proceed_to_processing(state: AgentState) -> str:
    """
    Conditional edge: Determines if user confirmed and there are URLs.
    """
    print("--- Condition: should_proceed_to_processing ---")
    if state.get("user_confirmation") and state.get("confirmed_urls"):
        print("Decision: Proceed to prepare_next_url.")
        return "prepare_next_url"
    else:
        print("Decision: No confirmation or no URLs, proceed to final_report.")
        if not state.get("final_message"): # Ensure a message if none set
            state["final_message"] = "User did not confirm or no URLs were available for processing."
        return "final_report"

def has_more_urls_to_process(state: AgentState) -> str:
    """
    Conditional edge: Checks if there's a URL in current_url_to_process,
    which is set by prepare_next_url_node.
    """
    print("--- Condition: has_more_urls_to_process ---")
    if state.get("current_url_to_process"):
        print(f"Decision: URL '{state.get('current_url_to_process')}' is ready, proceed to process_url.")
        return "process_url"
    else:
        print("Decision: No more URLs to process, proceed to final_report.")
        # Set a final message if processing loop finished and no other specific message is set
        if not state.get("final_message"):
            if state.get("error_message"):
                state["final_message"] = f"URL processing finished with errors: {state.get('error_message')}"
            elif state.get("processed_markdown_paths"):
                 state["final_message"] = f"Successfully processed all {len(state.get('processed_markdown_paths',[]))} confirmed URLs."
            else: # No errors, but also no paths processed (e.g. if confirmed_urls was empty but user_confirmation was true)
                 state["final_message"] = "URL processing finished, but no files were generated (check confirmed URLs)."
        return "final_report"

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("detect_urls", detect_urls_node)
workflow.add_node("request_user_confirmation", request_user_confirmation_node)
workflow.add_node("prepare_next_url", prepare_next_url_node)
workflow.add_node("process_url", process_url_node)
workflow.add_node("final_report", final_report_node)

# Define edges
workflow.set_entry_point("detect_urls")
workflow.add_edge("detect_urls", "request_user_confirmation")

# Conditional edge from user confirmation
workflow.add_conditional_edges(
    "request_user_confirmation",
    should_proceed_to_processing,
    {
        "prepare_next_url": "prepare_next_url",
        "final_report": "final_report" 
    }
)

# Corrected Loop for processing URLs:
# 1. process_url always goes back to prepare_next_url.
workflow.add_edge("process_url", "prepare_next_url")

# 2. prepare_next_url (after attempting to get a new URL) decides whether to
#    process another URL or go to the final report.
workflow.add_conditional_edges(
    "prepare_next_url",
    has_more_urls_to_process,
    {
        "process_url": "process_url",
        "final_report": "final_report"
    }
)

workflow.add_edge("final_report", END) # End of the graph

# Compile the graph
app = workflow.compile()

# Optional: For visualization (requires Pillow, pygraphviz, and graphviz)
# To generate: uncomment the following, ensure dependencies are installed.
# try:
#     from PIL import Image
#     import io
#     # Ensure the graphviz executables are on your PATH
#     # For example, on Ubuntu: sudo apt-get install graphviz
#     # On macOS: brew install graphviz
#     # Ensure python packages: pip install Pillow pygraphviz
#     img_data = app.get_graph().draw_mermaid_png()
#     with open("agent_graph.png", "wb") as f:
#         f.write(img_data)
#     print("\nGraph visualization saved to agent_graph.png")
# except Exception as e:
#     print(f"\nCould not generate graph visualization: {e}")
#     print("To generate visualization, ensure graphviz, Pillow, and pygraphviz are installed.")

if __name__ == '__main__':
    print("Agent graph compiled. Ready to be invoked from a runner script (e.g., main.py).")
    # Example of how to run for direct testing (usually done in main.py or a test file)
    # initial_state_example = AgentState(
    #     text_input="Visit https://www.google.com and https://www.wikipedia.org",
    #     processed_markdown_paths=[],
    #     # other fields will be None initially or default as per TypedDict rules
    #     detected_urls=None, confirmed_urls=None, user_confirmation=None,
    #     urls_to_process_stack=None, current_url_to_process=None,
    #     final_message=None, error_message=None
    # )
    # final_state_run = app.invoke(initial_state_example)
    # print("\n--- Example Invocation Final State ---")
    # import json
    # # Using a custom default function for json.dumps if AgentState contains non-serializable objects
    # print(json.dumps(final_state_run, indent=2, default=lambda o: f"<<non-serializable: {type(o).__name__}>>"))
    pass
