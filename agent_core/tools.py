from abc import ABC, abstractmethod
from typing import Any, Dict
from crawl4ai import Crawl4ai # Assuming crawl4ai is installed

class Tool(ABC):
    """
    Abstract Base Class for Tools.
    Defines a common interface for tools that the agent can use.
    """
    name: str
    description: str

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Executes the tool with the given input data."""
        pass

class Crawl4aiTool(Tool):
    """
    A tool that uses crawl4ai to extract content from a given URL.
    """
    name: str = "WebPageScraper"
    description: str = "Uses crawl4ai to extract content (markdown, images, videos) from a given URL."

    def __init__(self):
        """
        Initializes the Crawl4ai tool.
        """
        try:
            self.crawler = Crawl4ai()
            print("Crawl4aiTool: Crawler initialized successfully.")
        except Exception as e:
            print(f"Crawl4aiTool: Error initializing Crawl4ai: {e}")
            # In a real scenario, this might raise an error or set a state
            # indicating the tool is not operational.
            self.crawler = None 

    def execute(self, url: str) -> Dict[str, Any] | None:
        """
        Executes the crawl4ai scraper on the given URL.

        Args:
            url: The URL string to scrape.

        Returns:
            A dictionary-like object containing title, markdown, images, videos, etc.
            Returns None if crawling fails or the tool is not initialized.
        """
        if not self.crawler:
            print("Crawl4aiTool: Crawler not initialized. Cannot execute.")
            return None
            
        if not url or not isinstance(url, str):
            print("Crawl4aiTool: Invalid URL provided for execution.")
            return None

        print(f"Crawl4aiTool: Executing crawl on URL: {url}")
        try:
            # crawl4ai's result object might not be a plain dict,
            # but it's dictionary-like in terms of attribute access.
            # For AgentState, it's better if it's serializable.
            # For now, we return the result object directly.
            # If needed, convert to a plain dict: vars(result) or a custom method.
            result = self.crawler.run(url=url)
            
            if result:
                print(f"Crawl4aiTool: Successfully crawled {url}. Title: '{getattr(result, 'title', 'N/A')}'")
                # Example of converting to a dict if result has attributes like title, markdown etc.
                # This makes it more generically usable if we want to store it in state directly
                # or pass it around as a standard dict.
                # For now, the problem statement says "returning result directly is fine".
                # We will assume the result object can be handled by downstream functions.
                # If it's a Pydantic model or similar, it might already be fine.
                # Let's assume it has .title, .markdown, .images, .videos attributes.
                return {
                    "title": getattr(result, 'title', None),
                    "markdown": getattr(result, 'markdown', None),
                    "images": getattr(result, 'images', []),
                    "videos": getattr(result, 'videos', []),
                    "error": getattr(result, 'error', None), # include error if crawl4ai provides it
                    "raw_html": getattr(result, 'raw_html', None) # if available and needed
                }

            else:
                print(f"Crawl4aiTool: Crawl for {url} returned no result or an error.")
                return {"error": f"Crawl for {url} returned no result."}

        except Exception as e:
            print(f"Crawl4aiTool: An error occurred during crawl4ai execution for {url}: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Exception during crawl: {str(e)}"}

if __name__ == '__main__':
    # Example Usage (for testing this module directly)
    print("\n--- Testing Crawl4aiTool ---")
    # Test with a known simple URL. labs.google.com can be complex.
    # Using a placeholder URL as direct external calls can be problematic in some envs.
    # test_url = "https://www.example.com" 
    test_url_google = "https://www.google.com" # A generally accessible site

    # Note: This test requires crawl4ai to be installed and working,
    # and network access.
    scraper_tool = Crawl4aiTool()
    if scraper_tool.crawler: # Check if crawler was initialized
        print(f"\nAttempting to scrape: {test_url_google}")
        crawl_output = scraper_tool.execute(test_url_google)

        if crawl_output:
            print("\nCrawl Output (Processed Dict):")
            print(f"  Title: {crawl_output.get('title')}")
            print(f"  Markdown (first 100 chars): {crawl_output.get('markdown', '')[:100]}...")
            print(f"  Number of Images: {len(crawl_output.get('images', []))}")
            print(f"  Number of Videos: {len(crawl_output.get('videos', []))}")
            if crawl_output.get('error'):
                print(f"  Error during crawl: {crawl_output.get('error')}")
        else:
            print("Crawl execution returned None or failed.")
    else:
        print("Crawl4aiTool could not be initialized. Skipping direct test.")
    
    print("\n--- End of Crawl4aiTool Test ---")
    pass
