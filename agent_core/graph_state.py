from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    """
    Defines the state of the agent graph.
    It tracks all information needed by the nodes to perform their actions
    and make decisions for routing.
    """
    text_input: Optional[str]
    detected_urls: Optional[List[str]]
    confirmed_urls: Optional[List[str]]
    user_confirmation: Optional[bool]
    
    # For iterating through URLs
    urls_to_process_stack: Optional[List[str]] # Will hold a copy of confirmed_urls to pop from
    current_url_to_process: Optional[str]
    
    # Accumulates paths of generated markdown files
    processed_markdown_paths: List[str] 
    
    # For final reporting or error messages
    final_message: Optional[str]
    error_message: Optional[str]

    # To pass llm_provider to nodes if needed, though nodes can also call get_llm_provider() themselves
    # For simplicity, nodes will call get_llm_provider() for now.
    # llm_provider_instance: Optional[Any] # Could hold an LLMProvider instance
