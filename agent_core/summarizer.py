from pathlib import Path
from .llm_services import get_llm_provider # Import the new LLM service factory

# --- Core Logic ---

def process_content_for_summary_and_mindmap(markdown_file_path: str) -> tuple[str, str] | None:
    """
    Reads Markdown content, generates a summary and a Mermaid mind map using the configured LLM provider.

    Args:
        markdown_file_path: Path to the Markdown file.

    Returns:
        A tuple (summary, mermaid_mindmap), or None if an error occurs.
    """
    llm_provider = get_llm_provider() # Get the configured LLM provider

    if llm_provider is None:
        # This case might occur if get_llm_provider explicitly returns None on critical config errors,
        # though current implementation returns a PlaceholderLLM.
        print("Error: LLM provider could not be initialized. Cannot generate summary or mindmap.")
        return None

    try:
        # Read the content of the Markdown file
        markdown_content = Path(markdown_file_path).read_text(encoding="utf-8")
        
        if not markdown_content.strip():
            print(f"Warning: Markdown file {markdown_file_path} is empty or contains only whitespace.")
            # LLM provider should handle empty string gracefully if it proceeds.
            # Alternatively, return None or predefined strings for empty content here.
            # summary = "" 
            # mermaid_mindmap = "```mermaid\ngraph TD\nA[\"Empty Content\"];\n```"
            # return summary, mermaid_mindmap

        # Use LLM provider to generate summary
        summary = llm_provider.generate_summary(markdown_content)
        
        # Use LLM provider to generate Mermaid mind map
        mermaid_mindmap = llm_provider.generate_mermaid_mindmap(summary)
        
        return summary, mermaid_mindmap

    except FileNotFoundError:
        print(f"Error: File not found at {markdown_file_path}")
        return None
    except Exception as e:
        print(f"Error processing file {markdown_file_path} for summary/mindmap: {e}")
        return None

def prepend_mindmap_to_markdown(markdown_file_path: str, mermaid_mindmap: str) -> bool:
    """
    Prepends the given Mermaid mind map to the specified Markdown file.

    Args:
        markdown_file_path: Path to the Markdown file.
        mermaid_mindmap: The Mermaid mind map string (including ```mermaid ... ```).

    Returns:
        True on success, False on failure.
    """
    try:
        # Read the original content
        original_content = Path(markdown_file_path).read_text(encoding="utf-8")
        
        # Construct the new content
        # The mindmap should already be wrapped in ```mermaid ... ```
        new_content = f"{mermaid_mindmap}\n\n---\n\n{original_content}"
        
        # Write the new content back, overwriting the original file
        Path(markdown_file_path).write_text(new_content, encoding="utf-8")
        
        print(f"Mind map successfully prepended to {markdown_file_path}")
        return True

    except FileNotFoundError:
        print(f"Error: File not found at {markdown_file_path} during mindmap prepending.")
        return False
    except Exception as e:
        print(f"Error writing mindmap to {markdown_file_path}: {e}")
        return False

if __name__ == '__main__':
    # Example Usage (for testing this module directly)
    # This will now use the llm_services configuration.
    # To test different providers, set environment variables like LLM_PROVIDER.
    # e.g., export LLM_PROVIDER=openai
    
    # Create a dummy markdown file
    dummy_md_path = Path("dummy_test_article.md")
    dummy_md_content = """# My Test Article for LLM Abstraction
    
This is the first paragraph of the article. It demonstrates the new LLM abstraction layer.
This is the second paragraph. It should be summarized by the configured LLM provider.
The agent will process this, generate a summary and mindmap via the abstraction, and then prepend it.
    """
    dummy_md_path.write_text(dummy_md_content, encoding="utf-8")

    print(f"Created dummy file: {dummy_md_path.resolve()}")

    # 1. Process content for summary and mindmap
    # The behavior of this call will depend on environment variable settings now
    print("\nTesting process_content_for_summary_and_mindmap (check LLM provider based on ENV VARS or defaults)...")
    result = process_content_for_summary_and_mindmap(str(dummy_md_path))

    if result:
        summary, mindmap = result
        print("\n--- Generated Summary (via LLMProvider) ---")
        print(summary)
        print("\n--- Generated Mermaid Mindmap (via LLMProvider) ---")
        print(mindmap)

        # 2. Prepend mindmap to the file
        success_prepend = prepend_mindmap_to_markdown(str(dummy_md_path), mindmap)
        if success_prepend:
            print(f"\nSuccessfully updated {dummy_md_path.name} with mindmap.")
            print("\n--- File Content After Prepending ---")
            print(dummy_md_path.read_text(encoding="utf-8"))
        else:
            print(f"\nFailed to update {dummy_md_path.name} with mindmap.")
    else:
        print("\nFailed to generate summary and mindmap using LLMProvider.")

    # Clean up dummy file (optional)
    # try:
    #     dummy_md_path.unlink()
    #     print(f"\nCleaned up dummy file: {dummy_md_path.name}")
    # except OSError as e:
    #     print(f"Error deleting dummy file: {e}")
    pass
