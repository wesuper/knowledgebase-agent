import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any # For type hinting crawl_result

def sanitize_filename(name: str) -> str:
    """
    Sanitizes a string to be a valid filename.
    (Code remains unchanged, it's a utility function)
    """
    if not name:
        return "untitled"
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', name)
    name = name.replace(' ', '_')
    name = re.sub(r'_+', '_', name)
    if name == "." or name == "..":
        name = "file"
    max_len = 200
    if len(name) > max_len:
        name = name[:max_len-3] + "..."
    if not name:
        name = "sanitized_file"
    return name

def extract_and_store_content(
    crawl_result: Dict[str, Any], 
    original_url: str, # Keep original_url for context if title is missing or for logging
    base_output_dir: str = "agent_execution_directory/crew-paper"
) -> str | None:
    """
    Processes the output of Crawl4aiTool, sanitizes the title for a filename,
    and stores the content in a Markdown file. Media URLs are listed in the Markdown.

    Args:
        crawl_result: The dictionary output from Crawl4aiTool.execute().
                      Expected keys: 'title', 'markdown', 'images', 'videos', 'error'.
        original_url: The original URL that was crawled, for context and fallback naming.
        base_output_dir: The base directory where content will be stored.

    Returns:
        The path to the created Markdown file, or None if an error occurred or content is missing.
    """
    try:
        if not crawl_result or crawl_result.get("error"):
            error_detail = crawl_result.get("error", "Unknown error from crawl tool") if crawl_result else "Crawl result is None"
            print(f"ContentExtractor: Cannot process content for {original_url} due to crawl error: {error_detail}")
            return None

        markdown_content = crawl_result.get("markdown")
        if not markdown_content:
            print(f"ContentExtractor: No markdown content found for {original_url} in crawl result.")
            return None # Or handle as an error / empty file creation

        # --- Output Directory Setup ---
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        
        page_title = crawl_result.get('title')
        if not page_title: # Handle empty title from crawl_result
            print(f"Warning: No title found for {original_url}. Using a placeholder based on URL.")
            # Create a fallback title from the URL if necessary
            page_title = sanitize_filename(original_url.split('/')[-1] or original_url.split('/')[-2] or "Untitled_Page_From_URL")
        
        sanitized_title = sanitize_filename(page_title)

        output_path = Path(base_output_dir) / current_date_str / sanitized_title
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"ContentExtractor: Content for '{original_url}' will be saved in: {output_path}")

        # --- Markdown File ---
        markdown_filepath = output_path / (sanitized_title + ".md")

        # --- Media Handling (Placeholder based on crawl_result) ---
        media_content_lines = ["\n\n## Media Found"]
        media_dir_name = sanitize_filename(sanitized_title + "_Media")
        media_output_path = output_path / media_dir_name
        media_output_path.mkdir(parents=True, exist_ok=True)
        # print(f"ContentExtractor: Media directory created at: {media_output_path}")

        images = crawl_result.get('images', [])
        if images:
            media_content_lines.append("\n### Images:")
            for i, img_url in enumerate(images):
                media_content_lines.append(f"![Image {i+1}: {img_url}]({img_url})")
        else:
            media_content_lines.append("\nNo images found or extracted.")

        videos = crawl_result.get('videos', [])
        if videos:
            media_content_lines.append("\n### Videos:")
            for i, vid_url in enumerate(videos):
                media_content_lines.append(f"[Video {i+1}: {vid_url}]({vid_url})")
        else:
            media_content_lines.append("\nNo videos found or extracted.")
        
        # Append media information to the markdown content
        if len(media_content_lines) > 1: # if we added more than just the header
            full_markdown_content = markdown_content + "\n" + "\n".join(media_content_lines)
        else:
            full_markdown_content = markdown_content

        # Save the Markdown file
        with open(markdown_filepath, "w", encoding="utf-8") as f:
            f.write(full_markdown_content)
        
        print(f"ContentExtractor: Markdown content for {original_url} saved to: {markdown_filepath}")
        return str(markdown_filepath)

    except Exception as e:
        print(f"ContentExtractor: An error occurred while processing/saving content for {original_url}: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    # Example Usage (for testing this module directly)
    # This now requires a mock crawl_result or a call to the Crawl4aiTool first.
    
    print(f"Sanitized 'My Test /\\?*<>:|\" Document 123.pdf': {sanitize_filename('My Test /\\?*<>:|\" Document 123.pdf')}")
    
    # Mock crawl_result for testing extract_and_store_content
    mock_crawl_data = {
        "title": "Test Page Title with Slashes / and Spaces",
        "markdown": "# Hello World\n\nThis is test markdown content.",
        "images": ["http://example.com/image1.jpg", "http://example.com/image2.png"],
        "videos": ["http://example.com/video1.mp4"],
        "error": None
    }
    test_url_for_context = "http://example.com/testpage"

    print(f"\n--- Testing extract_and_store_content with mock data for URL: {test_url_for_context} ---")
    saved_path = extract_and_store_content(mock_crawl_data, test_url_for_context)
    if saved_path:
        print(f"Test content saved to: {saved_path}")
        # You might want to check the content of the created file and directory structure.
        # And clean up afterwards:
        # import shutil
        # containing_folder = Path(saved_path).parent
        # date_folder = containing_folder.parent
        # shutil.rmtree(date_folder.parent) # Removes agent_execution_directory
    else:
        print("Test content extraction and storage failed.")

    mock_crawl_data_no_title = {
        "title": "", # Empty title
        "markdown": "Markdown for a page with no title.",
        "images": [], "videos": [], "error": None
    }
    test_url_no_title = "http://example.com/another/page_no_title_here"
    print(f"\n--- Testing extract_and_store_content with mock data (no title) for URL: {test_url_no_title} ---")
    saved_path_no_title = extract_and_store_content(mock_crawl_data_no_title, test_url_no_title)
    if saved_path_no_title:
        print(f"Test content (no title) saved to: {saved_path_no_title}")
    else:
        print("Test content extraction (no title) failed.")

    mock_crawl_data_error = {
        "title": "Error Page",
        "markdown": None,
        "images": [], "videos": [],
        "error": "Simulated crawl failure."
    }
    test_url_error_page = "http://example.com/errorpage"
    print(f"\n--- Testing extract_and_store_content with mock data (crawl error) for URL: {test_url_error_page} ---")
    saved_path_error = extract_and_store_content(mock_crawl_data_error, test_url_error_page)
    if not saved_path_error:
        print("Test content extraction correctly failed due to crawl error.")
    else:
        print(f"Test content extraction (crawl error) unexpectedly created a file: {saved_path_error}")

    pass
