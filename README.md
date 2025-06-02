# AI Content Processing Agent

This project is an AI-powered agent designed to detect URLs in user-provided text, extract content from these URLs, generate summaries and mind maps using Language Models (LLMs), and store the processed content in a structured way. The agent's workflow is orchestrated using LangGraph, and it features a modular LLM integration layer. It also includes a Next.js frontend for user interaction.

## Key Features

*   **URL Detection:** Identifies URLs from input text using regular expressions.
*   **User Confirmation (CLI & Backend):** Prompts the user to confirm which detected URLs should be processed (CLI mode). The backend API currently processes all submitted URLs.
*   **Web Content Extraction:** Uses `crawl4ai` (wrapped as a formal Tool) to scrape textual content (Markdown), images, and video links from web pages.
*   **Content Summarization:** Generates a concise summary of the extracted text using a configurable LLM provider (currently placeholder).
*   **Mermaid Mind Map Generation:** Creates a Mermaid syntax mind map from the summary, also using an LLM (currently placeholder).
*   **Structured Output:** Saves the extracted Markdown, prepended with its mind map, into a date-stamped and title-sanitized directory structure. Media links are included in the Markdown.
*   **LangGraph Orchestration:** The Python agent's operational flow, state management, and conditional logic are managed by LangGraph.
*   **Modular LLM Integration:** Supports different LLM providers through an abstraction layer (`LLMProvider`), with initial (placeholder) support for OpenAI. Configuration is managed via environment variables.
*   **Tool-Based Architecture:** External services like web scraping (`crawl4ai`) are integrated as formal "Tools".
*   **FastAPI Backend:** Provides API endpoints to run the agent and serve processed files.
*   **Next.js Frontend:** A user interface built with Next.js, TypeScript, and React to interact with the agent and view results.

## Prerequisites

### Backend (Python Agent):
*   **Python:** 3.10+ (as per current `pyproject.toml` configuration).
*   **uv:** Recommended for Python environment and package management. (Can also use `pip` with a standard virtual environment).
*   **Git:** For cloning the repository.
*   **(Optional) Graphviz:** If you wish to generate a visual representation of the LangGraph graph.

### Frontend (Next.js Application):
*   **Node.js:** >=18.x recommended.
*   **npm** (comes with Node.js) or **yarn**.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

### Backend Setup:

2.  **Create and Activate Python Virtual Environment (Recommended with `uv`):**
    ```bash
    # In the project root directory
    uv venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate   # On Windows
    ```
    Alternatively, using standard `venv`:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Python Dependencies (with `uv`):**
    ```bash
    # In the project root directory, with virtual environment activated
    uv pip install .
    ```
    Alternatively, using `pip`:
    ```bash
    pip install .
    ```
    This installs `fastapi`, `uvicorn`, `langgraph`, `crawl4ai`, etc.

4.  **Configure Backend Environment Variables (LLM):**
    Create a `.env` file in the project root or set these variables in your environment for the Python backend:
    *   `LLM_PROVIDER`: e.g., `openai` or `placeholder` (defaults to `placeholder`).
    *   `OPENAI_API_KEY`: Your OpenAI API key if using OpenAI.
    *   `LLM_MODEL`: e.g., `gpt-3.5-turbo`.
    *(Note: LLM calls are currently simulated with placeholder responses.)*

### Frontend Setup:

5.  **Navigate to Frontend Directory:**
    ```bash
    cd frontend
    ```

6.  **Install Frontend Dependencies:**
    ```bash
    npm install
    # or: yarn install
    ```

7.  **Configure Frontend Environment Variables (Optional but Recommended):**
    Create a file named `.env.local` in the `frontend/` directory:
    ```
    NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
    NEXT_PUBLIC_API_FILE_BASE_URL=http://localhost:8000/api/files
    ```
    If this file is not created, the frontend will default to `http://localhost:8000` for the API base and `http://localhost:8000/api/files` for fetching files, as defined in `frontend/src/services/agentApi.ts` and `frontend/src/pages/view/[...filePath].tsx`.

## Running the Application

You need to run both the backend server and the frontend development server.

1.  **Run the Backend Server:**
    Open a terminal, navigate to the project root, activate the Python virtual environment, and run:
    ```bash
    uvicorn backend_server:app --reload --port 8000
    ```
    The backend API will be available at `http://localhost:8000`.

2.  **Run the Frontend Development Server:**
    Open another terminal, navigate to the `frontend/` directory, and run:
    ```bash
    npm run dev
    # or: yarn dev
    ```
    The frontend application will be available at `http://localhost:3000`.

3.  **Using the Application:**
    *   Open `http://localhost:3000` in your browser.
    *   The LLM configuration (from the backend's environment) will be displayed.
    *   Enter text containing URLs into the textarea and click "Submit URLs".
    *   The agent (via the backend) will process the URLs.
    *   Results, including messages, errors, and links to processed files, will be displayed.
    *   Clicking on a processed file link will navigate to a view page showing the Mermaid mind map and Markdown content.

### Running the Agent (CLI - Alternative)

The core agent logic can also be run via a command-line interface (though the primary interaction is now intended via the frontend and backend API):
```bash
# Ensure Python virtual environment is active
python main.py
```
Follow the CLI prompts for input and confirmation. Output files are saved in the `agent_execution_directory/crew-paper/` directory.

## Output Directory Structure

Processed content from the agent is saved in:
`agent_execution_directory/crew-paper/YYYY-MM-DD/Sanitized_Page_Title/Sanitized_Page_Title.md`
A `Sanitized_Page_Title_Media/` subdirectory is also created (currently for placeholder media links).

## Project Structure

```
.
├── agent_core/                # Core Python agent logic
│   ├── __init__.py
│   ├── agent_graph.py         # LangGraph definition
│   ├── content_extractor.py   # Saves crawled content
│   ├── graph_nodes.py         # LangGraph nodes
│   ├── graph_state.py         # AgentState for LangGraph
│   ├── llm_services.py        # LLM provider abstraction
│   ├── summarizer.py          # Summarization and mind map logic
│   ├── tools.py               # Tool definitions (Crawl4aiTool)
│   └── url_detector.py        # URL detection/confirmation
├── backend_server.py          # FastAPI backend server
├── main.py                    # CLI entry point for the agent
├── pyproject.toml             # Python project metadata and dependencies
├── frontend/                  # Next.js frontend application
│   ├── public/                # Static assets
│   ├── src/                   # Frontend source code
│   │   ├── components/        # React components (InputForm, ResultsDisplay, MermaidRenderer)
│   │   ├── pages/             # Next.js pages (_app.tsx, index.tsx, view/[...filePath].tsx)
│   │   ├── services/          # API interaction logic (agentApi.ts)
│   │   └── styles/            # Global CSS (globals.css)
│   ├── next.config.js         # Next.js configuration
│   ├── package.json           # Frontend dependencies (npm)
│   ├── tsconfig.json          # TypeScript configuration for frontend
│   └── .env.local (optional)  # Frontend environment variables (gitignored)
├── README.md                  # This file
└── agent_execution_directory/ # Default output directory for agent (gitignored)
```

## Architectural Design

(This section remains largely the same, focusing on the Python agent's architecture.)

The Python agent is built upon a modular architecture with clear separation of concerns, orchestrated by LangGraph.

*   **LangGraph Orchestration:** ...
*   **Modular LLM Integration:** ...
*   **Agent Components (PMA / PATA Model):** ...

## Backend API for Frontend

The FastAPI backend (`backend_server.py`) provides the following key endpoints for the Next.js frontend:

*   **`POST /api/agent/run`**
    *   **Request Body:** `{ "text_input": "string" }`
    *   **Response Body:** The final state of the LangGraph agent (`AgentState` as JSON), including `status`, `message`, `processed_markdown_paths`, `error_summary`, etc.
    *   **Function:** Triggers the agent to process the input text.

*   **`GET /api/files/{file_path:path}`**
    *   **URL Parameter:** `file_path` represents the relative path to the file within the `agent_execution_directory/crew-paper/` directory (e.g., `YYYY-MM-DD/Title/Title.md`).
    *   **Response:** The raw content of the requested Markdown file.
    *   **Function:** Allows the frontend to fetch and display processed Markdown files.

## Tool Integration: `crawl4ai`

(This section remains largely the same.)
*   The `crawl4ai` library is used for web content extraction. ...

## Extensibility

(This section remains largely the same.)
*   **Adding New LLM Providers:** ...
*   **Adding New Tools:** ...
*   **Modifying the Workflow:** ...

## Troubleshooting

*   **Python/Backend Issues:**
    *   `uv: command not found`: Ensure `uv` is installed and in PATH if used.
    *   Python Version: Ensure Python 3.10+ is used.
    *   API Key Missing: For LLM providers, set environment variables (e.g., `OPENAI_API_KEY`).
    *   `crawl4ai` Issues: Check network or page complexity.
    *   LangGraph Recursion Errors: Adjust limit in `backend_server.py` if invoking the graph for very long chains (currently not an issue with direct invoke).
*   **Frontend Issues:**
    *   Node.js/npm Version: Ensure Node.js >= 18.x.
    *   `NEXT_PUBLIC_API_BASE_URL` not set: Frontend might default to `http://localhost:8000`. If backend is elsewhere, create `frontend/.env.local`.
    *   Backend Not Running: Ensure the FastAPI server is running (e.g., on port 8000) when using the frontend.
    *   CORS Errors: The backend is configured for `http://localhost:3000`. If frontend runs on a different port, update `CORSMiddleware` in `backend_server.py`.
*   **General:**
    *   Ensure both backend and frontend dependencies are installed correctly.
    *   Check console logs in both the browser (for frontend) and the terminal running FastAPI (for backend) for error messages.

## Contributing

(This section remains largely the same.)
Contributions are welcome! ...

## License

(This section remains largely the same.)
This project is licensed under the MIT License. ...
