import json # For pretty printing the final state
from agent_core.llm_services import get_llm_config # For configuration awareness
from agent_core.agent_graph import app # Import the compiled LangGraph app
from agent_core.graph_state import AgentState # Import the state definition

def main():
    """
    Main function to run the LangGraph-based URL processing agent.
    """
    # --- Configuration Awareness (Optional but good for UX) ---
    llm_config = get_llm_config()
    print("-" * 50)
    print("LLM Service Configuration:")
    print(f"  Provider: {llm_config.get('provider')}")
    print(f"  Model:    {llm_config.get('model')}")

    # This part provides feedback based on environment variables.
    # The actual LLM provider instantiation and warnings (if any) happen inside get_llm_provider()
    # when called by a graph node, but this gives upfront info.
    if llm_config.get('provider') == 'openai':
        if not llm_config.get('openai_api_key'):
            print("  Warning: OpenAI API key (OPENAI_API_KEY) not found in environment.")
            print("           The OpenAI provider will use placeholder responses if called.")
        else:
            # In a real app, you wouldn't print the key, just confirm its presence.
            print("  OpenAI API key detected (OpenAI provider will use placeholder responses for now).")
    elif llm_config.get('provider') == 'anthropic':
        if not llm_config.get('anthropic_api_key'):
            print("  Warning: Anthropic API key (ANTHROPIC_API_KEY) not found in environment.")
        else:
            print("  Anthropic API key detected.")
    elif llm_config.get('provider') == 'placeholder':
        print("  Using general placeholder LLM responses via PlaceholderLLM.")
    print("-" * 50)

    # Get initial text input from the user
    user_text_input = input("Enter text with URLs to process: ")

    if not user_text_input.strip():
        print("No input provided. Exiting.")
        return

    # Initialize the agent state
    initial_state = AgentState(
        text_input=user_text_input,
        detected_urls=None, # Will be populated by a node
        confirmed_urls=None, # Will be populated by a node
        user_confirmation=None, # Will be populated by a node
        urls_to_process_stack=None, # Will be populated after confirmation
        current_url_to_process=None, # Will be managed by iteration logic
        processed_markdown_paths=[], # Initialize as empty list
        final_message=None, # Will be populated by nodes or graph logic
        error_message=None # Will be populated if errors occur
    )

    print("\n--- Invoking Agent Graph ---")
    # Configuration for the graph run, e.g., recursion limit
    # config = {"recursion_limit": 15} # Adjust as needed for the number of URLs + processing steps

    # Invoke the graph with the initial state
    # Note: If your graph has many steps or URLs, you might need to increase recursion_limit
    # For now, LangGraph's default should be okay for a few URLs.
    try:
        # final_state = app.invoke(initial_state, config=config)
        final_state = app.invoke(initial_state) # Use default config for now
    except Exception as e:
        print(f"Error invoking the agent graph: {e}")
        import traceback
        traceback.print_exc()
        # Populate a final state for error display
        final_state = initial_state.copy() # Start with initial state
        final_state["error_message"] = (final_state.get("error_message","") + f" Graph invocation error: {str(e)}").strip()
        final_state["final_message"] = "Agent execution failed due to an internal error."


    print("\n--- Agent Graph Execution Finished ---")

    # Print results from the final state
    print("\n--- Final State ---")
    # Pretty print the dictionary, handling non-serializable types if any (though state should be simple)
    try:
        print(json.dumps(final_state, indent=2, default=lambda o: f"<<non-serializable: {type(o).__name__}>>"))
    except TypeError:
        print(str(final_state)) # Fallback if json.dumps fails

    print("\n--- Summary of Operation ---")
    if final_state.get("final_message"):
        print(f"Message: {final_state.get('final_message')}")

    if final_state.get("processed_markdown_paths"):
        print("Processed Markdown files:")
        for path in final_state.get("processed_markdown_paths", []):
            print(f"  - {path}")

    if final_state.get("error_message"):
        print(f"Errors encountered: {final_state.get('error_message')}")

if __name__ == "__main__":
    main()
