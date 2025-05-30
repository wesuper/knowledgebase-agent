from typing import Dict, Any
from .graph_state import AgentState
from .url_detector import detect_urls as perform_detect_urls, confirm_urls as perform_confirm_urls
# Import the refactored content_extractor function
from .content_extractor import extract_and_store_content
from .summarizer import process_content_for_summary_and_mindmap, prepend_mindmap_to_markdown
from .tools import Crawl4aiTool # Import the new tool

# Node 1: Detect URLs (remains unchanged)
def detect_urls_node(state: AgentState) -> AgentState:
    print("--- Node: detect_urls_node ---")
    text_input = state.get("text_input")
    if not text_input:
        print("Error: Text input is missing.")
        state["error_message"] = "Text input is missing."
        state["final_message"] = "Operation failed: No text input provided."
        return state
    print(f"Detecting URLs in: '{text_input[:100]}...'")
    detected = perform_detect_urls(text_input)
    print(f"Detected URLs: {detected}")
    state["detected_urls"] = detected
    return state

# Node 2: Request User Confirmation (remains unchanged)
def request_user_confirmation_node(state: AgentState) -> AgentState:
    print("--- Node: request_user_confirmation_node ---")
    detected_urls_list = state.get("detected_urls")
    if not detected_urls_list:
        print("No URLs detected to confirm.")
        state["user_confirmation"] = False
        state["confirmed_urls"] = []
        state["final_message"] = "No URLs found in the input."
        return state
    print(f"Requesting confirmation for URLs: {detected_urls_list}")
    user_confirmed = perform_confirm_urls(detected_urls_list)
    if user_confirmed:
        print("User confirmed to proceed with detected URLs.")
        state["user_confirmation"] = True
        state["confirmed_urls"] = detected_urls_list
        state["urls_to_process_stack"] = list(detected_urls_list) 
    else:
        print("User declined to proceed.")
        state["user_confirmation"] = False
        state["confirmed_urls"] = []
        state["final_message"] = "Operation cancelled by user."
    return state

# Node 3: Prepare Next URL for Processing (remains unchanged)
def prepare_next_url_node(state: AgentState) -> AgentState:
    print("--- Node: prepare_next_url_node ---")
    urls_stack = state.get("urls_to_process_stack")
    if urls_stack and len(urls_stack) > 0:
        next_url = urls_stack.pop(0)
        print(f"Next URL to process: {next_url}")
        state["current_url_to_process"] = next_url
    else:
        print("No more URLs to process.")
        state["current_url_to_process"] = None
        # final_message might be set here if it's the definitive end of successful processing
        # However, the conditional edge logic in agent_graph.py also handles setting final_message
    return state

# Node 4: Process a Single URL (Refactored to use Crawl4aiTool)
def process_url_node(state: AgentState) -> AgentState:
    """
    Processes a single URL: uses Crawl4aiTool to get content, then processes this content
    for storage, summarization, and mind map prepending.
    """
    print("--- Node: process_url_node ---")
    current_url = state.get("current_url_to_process")
    if not current_url:
        print("Error: process_url_node called without a URL to process.")
        state["error_message"] = (state.get("error_message", "") + 
                                 "Attempted to process with no current URL. ").strip()
        return state

    print(f"Processing URL: {current_url} using Crawl4aiTool.")
    
    # Initialize and use the Crawl4aiTool
    crawl4ai_tool = Crawl4aiTool() # Instantiated here, or could be passed in state if initialized once globally
    
    if not crawl4ai_tool.crawler: # Check if crawler initialized correctly in the tool
        print(f"Error: Crawl4aiTool's crawler is not initialized. Cannot process {current_url}.")
        state["error_message"] = (state.get("error_message", "") +
                                 f"Crawl4aiTool not ready for {current_url}. ").strip()
        return state

    crawl_result = crawl4ai_tool.execute(current_url) # This now returns a dict or None

    markdown_filepath = None
    try:
        # 1. Extract and Store Content (now takes crawl_result)
        # The base_output_dir is default in extract_and_store_content
        markdown_filepath = extract_and_store_content(
            crawl_result=crawl_result, 
            original_url=current_url # Pass original URL for context
        )
        
        if not markdown_filepath:
            print(f"Failed to extract/store content for {current_url} (possibly due to crawl error or no markdown).")
            error_detail = crawl_result.get("error", "Content extraction/storage failed.") if crawl_result else "Crawl result was None."
            state["error_message"] = (state.get("error_message", "") + 
                                     f"Content processing failed for {current_url}: {error_detail}. ").strip()
            return state # Skip further processing for this URL

        print(f"Content for {current_url} saved to: {markdown_filepath}")
        current_processed_paths = state.get("processed_markdown_paths", [])
        current_processed_paths.append(markdown_filepath)
        state["processed_markdown_paths"] = current_processed_paths
        
        # 2. Generate Summary and Mindmap
        print(f"Generating summary and mindmap for: {markdown_filepath}")
        summary_result = process_content_for_summary_and_mindmap(markdown_filepath)
        
        if not summary_result:
            print(f"Failed to generate summary/mindmap for {markdown_filepath}.")
            state["error_message"] = (state.get("error_message", "") +
                                     f"Summary/mindmap generation failed for {markdown_filepath}. ").strip()
            return state # Skip prepending for this URL (already added to processed_markdown_paths)
            
        _summary, mermaid_mindmap = summary_result
        print(f"Summary and mindmap generated for {markdown_filepath}.")
        
        # 3. Prepend Mindmap
        if prepend_mindmap_to_markdown(markdown_filepath, mermaid_mindmap):
            print(f"Mindmap successfully prepended to {markdown_filepath}.")
        else:
            print(f"Failed to prepend mindmap to {markdown_filepath}.")
            state["error_message"] = (state.get("error_message", "") +
                                     f"Mindmap prepending failed for {markdown_filepath}. ").strip()

    except Exception as e:
        print(f"An unexpected error occurred in process_url_node for {current_url}: {e}")
        import traceback
        traceback.print_exc()
        state["error_message"] = (state.get("error_message", "") + 
                                 f"Unexpected error processing {current_url}: {str(e)}. ").strip()
    return state

# Node 5: Final Reporting Node (remains largely unchanged, but reflects on state)
def final_report_node(state: AgentState) -> AgentState:
    print("--- Node: final_report_node ---")
    processed_paths = state.get("processed_markdown_paths", [])
    errors = state.get("error_message")
    current_final_message = state.get("final_message")

    if not current_final_message: # If no overriding message (e.g. user cancel, no urls)
        if errors:
            state["final_message"] = f"Processing completed with errors. Check error_message field. Processed files: {len(processed_paths)}."
        elif processed_paths:
            state["final_message"] = f"Processing completed successfully for {len(processed_paths)} URL(s)."
        else: # No specific error, no paths, means something else (e.g. no URLs detected initially but not caught as final message)
            state["final_message"] = "Processing finished, but no content was generated or no URLs were confirmed."
    
    # Log the full error message if it exists, as final_message might be a summary
    if errors:
        print(f"Detailed errors during processing: {errors}")

    print(f"Final Message: {state['final_message']}")
    return state
