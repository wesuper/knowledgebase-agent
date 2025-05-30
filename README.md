# AI Content Processing Agent

This project is an AI-powered agent designed to detect URLs in user-provided text, extract content from these URLs, generate summaries and mind maps using Language Models (LLMs), and store the processed content in a structured way. The agent's workflow is orchestrated using LangGraph, and it features a modular LLM integration layer.

## Key Features

*   **URL Detection:** Identifies URLs from input text using regular expressions.
*   **User Confirmation:** Prompts the user to confirm which detected URLs should be processed.
*   **Web Content Extraction:** Uses `crawl4ai` (wrapped as a formal Tool) to scrape textual content (Markdown), images, and video links from web pages.
*   **Content Summarization:** Generates a concise summary of the extracted text using a configurable LLM provider.
*   **Mermaid Mind Map Generation:** Creates a Mermaid syntax mind map from the summary, also using an LLM.
*   **Structured Output:** Saves the extracted Markdown, prepended with its mind map, into a date-stamped and title-sanitized directory structure. Media links are included in the Markdown.
*   **LangGraph Orchestration:** The agent's operational flow, state management, and conditional logic are managed by LangGraph.
*   **Modular LLM Integration:** Supports different LLM providers through an abstraction layer (`LLMProvider`), with initial (placeholder) support for OpenAI. Configuration is managed via environment variables.
*   **Tool-Based Architecture:** External services like web scraping (`crawl4ai`) are integrated as formal "Tools".

## Prerequisites

*   **Python:** 3.10+ (as per current `pyproject.toml` configuration).
*   **uv:** Recommended for environment and package management. `uv` is a fast Python package installer and resolver, written in Rust. It can be used to create virtual environments and install dependencies. (Can also use `pip` with a standard virtual environment).
*   **Git:** For cloning the repository.
*   **(Optional) Graphviz:** If you wish to generate a visual representation of the LangGraph graph (see `agent_core/agent_graph.py`).

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and Activate Virtual Environment (Recommended with `uv`):**
    ```bash
    uv venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate   # On Windows
    ```
    Alternatively, using standard `venv`:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate   # On Windows
    ```

3.  **Install Dependencies (with `uv`):**
    ```bash
    uv pip install .
    ```
    Alternatively, using `pip`:
    ```bash
    pip install .
    ```
    This will install all necessary packages listed in `pyproject.toml`, including `langgraph`, `crawl4ai`, etc.

4.  **Configure Environment Variables for LLM:**
    The agent uses environment variables to configure the LLM provider. Create a `.env` file in the project root or set these variables in your environment:

    *   `LLM_PROVIDER`: Specifies the LLM provider to use.
        *   Example: `LLM_PROVIDER=openai` or `LLM_PROVIDER=placeholder` (defaults to `placeholder`).
    *   `OPENAI_API_KEY`: Your API key if using the OpenAI provider.
        *   Example: `OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
    *   `LLM_MODEL`: The model name to use for the selected provider.
        *   Example: `LLM_MODEL=gpt-3.5-turbo` (for OpenAI) or `LLM_MODEL=custom-placeholder` (for PlaceholderLLM). Defaults to `default` which might map to a provider-specific default like `gpt-3.5-turbo`.

    *Note: Currently, LLM calls are simulated with placeholder responses. Full API integration would require these keys for actual LLM interactions.*

## Running the Agent (CLI)

The agent is run via the `main.py` script:

```bash
python main.py
```

**Interaction Flow:**

1.  The script will first display the current LLM service configuration based on environment variables.
2.  It will then prompt you to "Enter text with URLs to process:".
3.  Paste or type text containing one or more URLs.
4.  If URLs are detected, they will be listed, and you'll be asked: "Do you want to proceed with these URLs? (yes/no):".
5.  Type `yes` to process the confirmed URLs or `no` to cancel.
6.  The agent will then process each confirmed URL:
    *   Scrape content using `crawl4ai`.
    *   Save the content to a Markdown file.
    *   Generate a (placeholder) summary and Mermaid mind map.
    *   Prepend the mind map to the Markdown file.
7.  Status messages will be printed throughout the process.
8.  A final message will indicate completion status, and any errors will be reported.

**Output Directory Structure:**
Processed content is saved in:
`agent_execution_directory/crew-paper/YYYY-MM-DD/Sanitized_Page_Title/Sanitized_Page_Title.md`
A `Sanitized_Page_Title_Media/` subdirectory is also created (currently for placeholder media links).

## Project Structure

```
.
├── agent_core/                # Core logic of the agent
│   ├── __init__.py
│   ├── agent_graph.py         # LangGraph definition and compilation
│   ├── content_extractor.py   # Saves crawled content to files
│   ├── graph_nodes.py         # Node functions for the LangGraph
│   ├── graph_state.py         # AgentState definition for LangGraph
│   ├── llm_services.py        # LLM provider abstraction and configuration
│   ├── summarizer.py          # Logic for summarization and mind map prepending
│   ├── tools.py               # Tool definitions (e.g., Crawl4aiTool)
│   └── url_detector.py        # URL detection and confirmation logic
├── main.py                    # Main CLI entry point for the agent
├── pyproject.toml             # Project metadata and dependencies (for uv/pip)
├── README.md                  # This file
└── agent_execution_directory/ # Default output directory (created on run)
    └── crew-paper/
```

## Architectural Design

The agent is built upon a modular architecture with clear separation of concerns, orchestrated by LangGraph.

*   **LangGraph Orchestration:**
    *   The core workflow is defined in `agent_core/agent_graph.py`.
    *   `StatefulGraph` from LangGraph is used to manage the sequence of operations.
    *   `AgentState` (`agent_core/graph_state.py`) defines the memory or state that flows through the graph, being updated by each node.
    *   Nodes (`agent_core/graph_nodes.py`) represent specific processing steps (e.g., detecting URLs, processing a single URL).
    *   Edges (conditional or direct) define the transitions between nodes based on the current state.

*   **Modular LLM Integration:**
    *   Located in `agent_core/llm_services.py`.
    *   An abstract base class `LLMProvider` defines a common interface for LLM operations (e.g., `generate_summary`, `generate_mermaid_mindmap`).
    *   Concrete implementations like `OpenAILLM` (for OpenAI) and `PlaceholderLLM` (for simulated responses) inherit from `LLMProvider`.
    *   A factory function `get_llm_provider()` dynamically instantiates the chosen LLM provider based on environment variables (`LLM_PROVIDER`, API keys, `LLM_MODEL`). This allows for easy switching or addition of LLM backends.

*   **Agent Components (PMA / PATA Model):**
    *   **Planning:** The LangGraph definition in `agent_graph.py` serves as the explicit, modifiable plan for the agent's execution sequence and conditional logic.
    *   **Memory:** The `AgentState` TypedDict in `graph_state.py` acts as the agent's working memory, carrying data between operational steps.
    *   **Tools:**
        *   `agent_core/tools.py` defines a formal structure for tools. `Crawl4aiTool` wraps the `crawl4ai` library for web scraping, making it a well-defined component.
        *   The LLM services in `llm_services.py` can also be viewed as specialized tools for text generation tasks.
    *   **Action:** The functions within `agent_core/graph_nodes.py` (e.g., `process_url_node`) execute the agent's actions by invoking tools, calling business logic functions (like file saving from `content_extractor.py` or summarization logic from `summarizer.py`), and updating the state.

## API Reference (Conceptual for Future Web Frontend)

While the current implementation is CLI-based, a future web service (e.g., using FastAPI) could expose the agent's functionality via the following conceptual API endpoints:

*   **`POST /api/agent/run`**
    *   **Request:**
        ```json
        {
          "text_input": "User-provided text with URLs like https://example.com"
        }
        ```
    *   **Response (Synchronous for now, could be async with session ID):**
        ```json
        {
          "status": "completed" | "failed" | "completed_with_errors",
          "message": "Descriptive message of the outcome.",
          "processed_files": [
            "/path/to/output/YYYY-MM-DD/Page_Title/Page_Title.md"
          ],
          "errors": "Details of any errors encountered."
        }
        ```

*   **`GET /api/agent/status/{session_id}`** (If asynchronous operation is implemented)
    *   **Request:** Path parameter `session_id` obtained from an async `/run` call.
    *   **Response:**
        ```json
        {
          "session_id": "string",
          "status": "pending" | "processing" | "completed" | "failed",
          "message": "Current status message.",
          "processed_files": [],
          "errors": null
        }
        ```

## Tool Integration: `crawl4ai`

*   The `crawl4ai` library is used for web content extraction.
*   It's wrapped within the `Crawl4aiTool` class in `agent_core/tools.py`. This formalizes its use as a distinct "tool" that the agent can leverage.
*   The `process_url_node` in the LangGraph flow calls `Crawl4aiTool.execute(url)` to get web page content.
*   The result (a dictionary containing title, markdown, media links, etc.) is then passed to `content_extractor.extract_and_store_content` for file system operations.

## Extensibility

*   **Adding New LLM Providers:**
    1.  Create a new class in `agent_core/llm_services.py` that implements the `LLMProvider` interface.
    2.  Update the `get_llm_provider()` factory function to recognize and instantiate your new provider based on an `LLM_PROVIDER` environment variable value and its specific API key/model configuration.
*   **Adding New Tools:**
    1.  Define a new tool class, potentially inheriting from the `Tool` base class in `agent_core/tools.py`.
    2.  Implement its `execute` method.
    3.  Integrate the tool into the relevant LangGraph node(s) in `agent_core/graph_nodes.py` where its functionality is needed.
*   **Modifying the Workflow:**
    *   The LangGraph definition in `agent_core/agent_graph.py` can be modified by adding, removing, or re-wiring nodes and edges to change the agent's behavior.

## Troubleshooting

*   **`uv: command not found`**: Ensure `uv` is installed and in your system's PATH. If not using `uv`, ensure you are using `pip` with a standard Python virtual environment.
*   **Python Version Issues**: The project is set for Python 3.10+. Ensure your environment uses a compatible version.
*   **API Key Missing**: If using `LLM_PROVIDER=openai` (or other future non-placeholder providers), ensure the corresponding API key (e.g., `OPENAI_API_KEY`) is correctly set in your environment variables or `.env` file. The agent will print warnings if keys are expected but not found, and LLM operations will use placeholder responses.
*   **`crawl4ai` Issues**: If `crawl4ai` fails (e.g., due to network issues or complex JavaScript on a page), the agent will attempt to handle the error for that specific URL and continue with others. Check console logs from `Crawl4aiTool` and `content_extractor`.
*   **LangGraph Recursion Errors**: For a very large number of URLs, LangGraph's default recursion limit might be hit. This can be adjusted in `main.py` when invoking the graph: `app.invoke(initial_state, {"recursion_limit": <new_limit>})`.

## Contributing

Contributions are welcome! Please follow these general guidelines:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (e.g., `feature/my-new-feature` or `fix/issue-description`).
3.  Make your changes, ensuring code is clean and well-commented where necessary.
4.  If adding new features, include or update relevant tests (tests are planned for future iterations).
5.  Ensure your changes don't break existing functionality.
6.  Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file (if one is added, typically MIT for open source projects like this) for details. For now, assume MIT License.
