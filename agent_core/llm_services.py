import os
from abc import ABC, abstractmethod

# --- LLM Provider Abstraction ---

class LLMProvider(ABC):
    """
    Abstract Base Class for LLM providers.
    Defines the interface for generating summaries and Mermaid mind maps.
    """
    @abstractmethod
    def generate_summary(self, text: str) -> str:
        """Generates a summary for the given text."""
        pass

    @abstractmethod
    def generate_mermaid_mindmap(self, summary: str) -> str:
        """Generates a Mermaid mind map for the given summary."""
        pass

# --- Concrete LLM Provider Implementations ---

class OpenAILLM(LLMProvider):
    """
    Concrete implementation for OpenAI LLM services.
    Uses placeholder logic for now.
    """
    def __init__(self, api_key: str | None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        if not self.api_key:
            print(f"Warning: OpenAI API key not provided for model {self.model}. Using placeholder responses.")
        # In a real implementation, you would initialize the OpenAI client here.
        # from openai import OpenAI
        # self.client = OpenAI(api_key=self.api_key)

    def generate_summary(self, text: str) -> str:
        """
        Generates a summary using (placeholder) OpenAI logic.
        """
        # Conceptual: response = self.client.chat.completions.create(...)
        # For now, placeholder:
        if not text:
            return f"[OpenAI Summary - Model: {self.model}]: Empty input text."
        return f"[OpenAI Summary - Model: {self.model}]: {text[:100].replacechr(10,' ').replacechr(13,' ')}..."

    def generate_mermaid_mindmap(self, summary: str) -> str:
        """
        Generates a Mermaid mind map using (placeholder) OpenAI logic.
        """
        # Conceptual: response = self.client.chat.completions.create(...)
        # For now, placeholder:
        sanitized_summary_preview = summary[:50].replace('"', '').replace("'", "")
        return f"""```mermaid
graph TD
    A["[OpenAI Mindmap - Model: {self.model}]"] --> B["Summary: {sanitized_summary_preview}..."];
    B --> C["Key Point 1 (OpenAI)"];
    B --> D["Key Point 2 (OpenAI)"];
```"""

class PlaceholderLLM(LLMProvider):
    """
    A generic placeholder LLM provider for default or fallback use.
    """
    def __init__(self, model: str = "default-placeholder"):
        self.model = model
        print(f"Using PlaceholderLLM (model: {self.model}).")

    def generate_summary(self, text: str) -> str:
        if not text:
            return f"[Placeholder Summary - Model: {self.model}]: Empty input text."
        return (f"[Placeholder Summary - Model: {self.model}]: Text length {len(text)}, "
                f"first 100 chars: {text[:100].replacechr(10,' ').replacechr(13,' ')}...")

    def generate_mermaid_mindmap(self, summary: str) -> str:
        sanitized_summary_preview = summary[:50].replace('"', '').replace("'", "")
        return f"""```mermaid
graph TD
    A["[Placeholder Mindmap - Model: {self.model}]"] --> B["Placeholder Summary: {sanitized_summary_preview}..."];
    B --> C["Generic Point A"];
    B --> D["Generic Point B"];
```"""

# --- Configuration and Factory ---

def get_llm_config() -> dict:
    """
    Loads LLM configuration from environment variables.
    """
    return {
        "provider": os.getenv("LLM_PROVIDER", "placeholder").lower(), # Default to placeholder
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        # Add other provider keys here, e.g., ANTHROPIC_API_KEY
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": os.getenv("LLM_MODEL", "default") # Model name can be generic or specific
    }

def get_llm_provider() -> LLMProvider:
    """
    Factory function to get an instance of the configured LLM provider.
    """
    config = get_llm_config()
    provider_name = config["provider"]
    model_name = config["model"]

    if provider_name == "openai":
        api_key = config["openai_api_key"]
        # API key presence is handled within OpenAILLM for now (prints warning)
        # Allowing instantiation even without key for placeholder behavior.
        print(f"Attempting to initialize OpenAI LLM provider with model: {model_name}.")
        return OpenAILLM(api_key=api_key, model=model_name if model_name != "default" else "gpt-3.5-turbo")
    # Example for another provider:
    # elif provider_name == "anthropic":
    #     api_key = config["anthropic_api_key"]
    #     if not api_key:
    #         print("Warning: Anthropic provider selected, but ANTHROPIC_API_KEY not found. Falling back to PlaceholderLLM.")
    #         return PlaceholderLLM(model="fallback-anthropic-no-key")
    #     print(f"Attempting to initialize Anthropic LLM provider with model: {model_name}.")
    #     return AnthropicLLM(api_key=api_key, model=model_name if model_name != "default" else "claude-2")
    elif provider_name == "placeholder":
        print(f"Using explicit PlaceholderLLM provider with model: {model_name}.")
        return PlaceholderLLM(model=model_name)
    else:
        print(f"Warning: Unknown LLM provider '{provider_name}'. Falling back to PlaceholderLLM.")
        return PlaceholderLLM(model=f"fallback-unknown-provider-{provider_name}")

if __name__ == '__main__':
    # Test the factory function and providers
    print("--- Testing LLM Service Configuration ---")

    # Scenario 1: Default (Placeholder)
    print("\nScenario 1: No ENV VARS (should default to PlaceholderLLM)")
    # Unset env vars for a clean test if possible (cannot do with os.environ directly in a lasting way for subprocesses)
    # This test relies on them not being set, or being set to 'placeholder'
    if "LLM_PROVIDER" in os.environ: del os.environ["LLM_PROVIDER"]
    if "OPENAI_API_KEY" in os.environ: del os.environ["OPENAI_API_KEY"]
    
    provider = get_llm_provider()
    summary = provider.generate_summary("This is a test text for default placeholder.")
    mindmap = provider.generate_mermaid_mindmap(summary)
    print(f"Summary: {summary}")
    print(f"Mindmap:\n{mindmap}")

    # Scenario 2: OpenAI configured, no API key (should use OpenAILLM with placeholders)
    print("\nScenario 2: LLM_PROVIDER=openai, no API key")
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["LLM_MODEL"] = "gpt-4-test"
    if "OPENAI_API_KEY" in os.environ: del os.environ["OPENAI_API_KEY"] # Ensure it's not set
    
    provider_openai_no_key = get_llm_provider()
    summary_openai_no_key = provider_openai_no_key.generate_summary("Test for OpenAI without API key.")
    mindmap_openai_no_key = provider_openai_no_key.generate_mermaid_mindmap(summary_openai_no_key)
    print(f"Summary: {summary_openai_no_key}")
    print(f"Mindmap:\n{mindmap_openai_no_key}")

    # Scenario 3: OpenAI configured, with dummy API key
    print("\nScenario 3: LLM_PROVIDER=openai, with dummy API key")
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["OPENAI_API_KEY"] = "dummy-test-key"
    os.environ["LLM_MODEL"] = "gpt-3.5-turbo-test"

    provider_openai_with_key = get_llm_provider()
    summary_openai_with_key = provider_openai_with_key.generate_summary("Test for OpenAI with dummy API key.")
    mindmap_openai_with_key = provider_openai_with_key.generate_mermaid_mindmap(summary_openai_with_key)
    print(f"Summary: {summary_openai_with_key}")
    print(f"Mindmap:\n{mindmap_openai_with_key}")
    
    # Cleanup environment variables used for testing
    del os.environ["LLM_PROVIDER"]
    if "OPENAI_API_KEY" in os.environ: del os.environ["OPENAI_API_KEY"]
    if "LLM_MODEL" in os.environ: del os.environ["LLM_MODEL"]
    print("\n--- End of LLM Service Configuration Test ---")
    pass
