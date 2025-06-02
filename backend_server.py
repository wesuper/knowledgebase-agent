from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import os # For path normalization and security checks

# Assuming agent_core is in the same directory or Python path
from agent_core.agent_graph import app as langgraph_app
from agent_core.graph_state import AgentState # Used for type hinting if needed, and initial state structure

# --- FastAPI App Initialization ---
app = FastAPI(title="AI Content Processing Agent API")

# --- CORS Configuration ---
# Adjust allow_origins if your frontend runs on a different port or domain
origins = [
    "http://localhost:3000", # Default Next.js frontend port
    # Add other origins if needed, e.g., a deployed frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Pydantic Models for Request/Response ---
class AgentRunRequest(BaseModel):
    text_input: str

# Note: The LangGraph app's final_state is a TypedDict (AgentState).
# FastAPI will automatically serialize dicts to JSON. If specific output shaping
# is needed, a Pydantic response_model can be defined. For now, returning the
# final_state dict directly is fine. The frontend's ApiResponse type should
# be designed to handle this structure.

# --- API Endpoints ---

@app.post("/api/agent/run")
async def agent_run_endpoint(request_data: AgentRunRequest) -> AgentState:
    """
    Endpoint to run the AI agent with the provided text input.
    Invokes the LangGraph application.
    """
    print(f"Received request for /api/agent/run with input: '{request_data.text_input[:100]}...'")
    try:
        # Initialize the state for the LangGraph application
        # Ensure this matches the structure expected by your AgentState TypedDict
        initial_state: AgentState = {
            "text_input": request_data.text_input,
            "detected_urls": None,
            "confirmed_urls": None,
            "user_confirmation": None,
            "urls_to_process_stack": None,
            "current_url_to_process": None,
            "processed_markdown_paths": [], # Initialize as empty list
            "final_message": None,
            "error_message": None,
        }

        # LangGraph's app.invoke is synchronous. For long-running tasks in a production FastAPI app,
        # consider using Background Tasks: `background_tasks.add_task(langgraph_app.invoke, initial_state)`
        # and returning an immediate response (e.g., a session ID for polling status).
        # For this project's scope, direct invocation is acceptable.
        final_state = langgraph_app.invoke(initial_state)

        print(f"LangGraph app invoked. Final state message: {final_state.get('final_message')}")
        # FastAPI will serialize the final_state dictionary (which matches AgentState structure) to JSON.
        return final_state
    except Exception as e:
        print(f"Error during agent run: {e}")
        import traceback
        traceback.print_exc()
        # Consider what status code is most appropriate. 500 for unhandled server errors.
        raise HTTPException(status_code=500, detail=f"An error occurred during agent processing: {str(e)}")


# Base directory for serving files. Ensure this path is correct.
# .resolve() makes it an absolute path.
BASE_FILES_DIR = Path("agent_execution_directory/crew-paper").resolve()

@app.get("/api/files/{file_path:path}")
async def get_file(file_path: str, request: Request):
    """
    Serves a specific file from the agent's output directory.
    The `file_path` parameter will capture everything after `/api/files/`.
    Example: /api/files/2023-10-26/My_File_Title/My_File_Title.md
    """
    print(f"Received request for file: {file_path} from IP: {request.client.host if request.client else 'Unknown'}")
    try:
        # Basic path sanitization: remove leading slashes to prevent absolute path interpretation by joinpath
        # and decode URL-encoded characters (FastAPI does this automatically for path parameters).
        sanitized_file_path = file_path.lstrip('/')

        # Path traversal defense: os.path.normpath helps resolve ".." and "."
        # It's important that BASE_FILES_DIR is absolute and resolved.
        normalized_path_segment = os.path.normpath(sanitized_file_path)

        # Prevent construction of paths outside the intended root, e.g. ../../secret.txt
        if normalized_path_segment.startswith("..") or os.path.isabs(normalized_path_segment):
            print(f"Access denied: Invalid path '{file_path}' (normalized: '{normalized_path_segment}') attempts to escape base directory.")
            raise HTTPException(status_code=400, detail="Invalid file path.")

        requested_path = BASE_FILES_DIR.joinpath(normalized_path_segment).resolve()
        print(f"Attempting to serve resolved path: {requested_path}")

        # Security Check: Ensure the resolved path is still within the BASE_FILES_DIR.
        # This is a critical security measure.
        if not requested_path.is_relative_to(BASE_FILES_DIR): # Requires Python 3.9+
            # Alternative for older Python (less robust, be careful with symlinks):
            # if not str(requested_path).startswith(str(BASE_FILES_DIR)):
            print(f"Access denied: Path '{requested_path}' is outside the allowed base directory '{BASE_FILES_DIR}'.")
            raise HTTPException(status_code=403, detail="Access denied to this path.")

        if requested_path.is_file():
            print(f"Serving file: {requested_path}")
            # Return FileResponse, FastAPI handles content type based on extension.
            return FileResponse(requested_path)
        else:
            print(f"File not found at path: {requested_path}")
            raise HTTPException(status_code=404, detail="File not found.")

    except HTTPException as e:
        # Re-raise HTTPExceptions directly (e.g., from security checks)
        raise e
    except Exception as e:
        # Catch any other errors (e.g., issues with Path operations)
        print(f"Internal server error while trying to serve file {file_path}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# --- Main execution (for running with uvicorn) ---
if __name__ == "__main__":
    import uvicorn
    # This is for direct execution of this file.
    # Typically, you'd run: uvicorn backend_server:app --reload --port 8000
    print(f"Starting Uvicorn server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
