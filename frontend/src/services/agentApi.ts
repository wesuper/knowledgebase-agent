import axios from 'axios';

/**
 * Defines the expected structure of the API response from the backend.
 * This should align with the final state output of the Python LangGraph agent,
 * particularly fields like final_message, error_message, and processed_markdown_paths.
 */
export interface ApiResponse {
  status: 'completed' | 'error' | 'completed_with_errors'; // Reflects the overall outcome
  message: string; // Corresponds to final_message from the backend

  // Optional fields that might be present in the response
  text_input?: string; // Original text input, for reference
  detected_urls?: string[];
  confirmed_urls?: string[]; // Might not be directly relevant if interaction is different in web UI
  processed_markdown_paths?: string[];

  // 'errors' for specific error details, 'error_message' from backend state for a summary of errors
  error_details?: string[]; // For a list of specific errors if backend provides them
  error_summary?: string; // Corresponds to error_message from backend state
}

// Assume backend is running on http://localhost:8000
// This should be configurable in a real app using environment variables.
// For this task, we'll use a hardcoded URL as per instructions (if .env.local is skipped).
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
// Note: The Python backend (FastAPI) isn't serving at /api by default from the previous plan.
// It would serve directly at /agent/run. Adjusting to 'http://localhost:8000'.
const ACTUAL_API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';


export const runAgent = async (textInput: string): Promise<ApiResponse> => {
  try {
    // The backend endpoint is assumed to be /agent/run directly under the API root
    const response = await axios.post<ApiResponse>(`${ACTUAL_API_URL}/agent/run`, {
      text_input: textInput, // Ensure this matches the Pydantic model in FastAPI backend
    });

    // Assuming the backend returns a structure that directly maps to ApiResponse.
    // If the backend's final state has fields like `final_message`, `error_message`,
    // we might need to map them here to `message`, `error_summary` etc.
    // For now, let's assume the backend response is already shaped like ApiResponse.
    // A more robust mapping would be:
    // return {
    //   status: response.data.error_message ? 'completed_with_errors' : 'completed',
    //   message: response.data.final_message || "Operation successful.",
    //   processed_markdown_paths: response.data.processed_markdown_paths,
    //   error_summary: response.data.error_message,
    //   // other fields from response.data as needed
    // };
    return response.data;

  } catch (error) {
    let responseData: Partial<ApiResponse> = {}; // Use Partial for error construction

    if (axios.isAxiosError(error) && error.response) {
      // Backend responded with an error status code (e.g., 4xx, 5xx)
      console.error('Backend Error:', error.response.status, error.response.data);
      responseData = {
        status: 'error',
        message: `Backend Error: ${error.response.status} - ${error.response.data?.detail || error.message}`,
        error_summary: error.response.data?.detail || JSON.stringify(error.response.data), // FastAPI often uses 'detail'
        error_details: error.response.data?.errors || (error.response.data?.detail ? [error.response.data.detail] : [JSON.stringify(error.response.data)]),
      };
    } else if (axios.isAxiosError(error)) {
      // Network error or other Axios error without a response from backend (e.g., CORS, DNS, server down)
      console.error('Network/Axios Error:', error.message);
      responseData = {
        status: 'error',
        message: `Network Error: ${error.message}. Is the backend server running at ${ACTUAL_API_URL}?`,
        error_summary: error.message,
        error_details: [error.message],
      };
    } else {
      // Non-Axios error (e.g., issue in request setup or response handling)
      console.error('Unknown Error:', error);
      responseData = {
        status: 'error',
        message: `Unknown Error: ${String(error)}`,
        error_summary: String(error),
        error_details: [String(error)],
      };
    }
    // Ensure all required fields of ApiResponse are present, even in error cases.
    // 'message' is always set above. 'status' is always 'error'.
    // Other fields can be undefined or empty lists.
    return {
        status: responseData.status || 'error',
        message: responseData.message || 'An unexpected error occurred.',
        processed_markdown_paths: responseData.processed_markdown_paths || [],
        error_summary: responseData.error_summary,
        error_details: responseData.error_details,
        // Ensure other optional fields from ApiResponse are also present if that's the contract
    } as ApiResponse; // Type assertion to satisfy the return type
  }
};

// Example of how this might be used in a component (do not include in the file itself):
/*
  const handleSubmit = async (text: string) => {
    setIsLoading(true);
    setApiResponse(null); // Clear previous results
    try {
      const result = await runAgent(text);
      setApiResponse(result);
    } catch (e) {
      // This catch should ideally not be needed if runAgent handles all errors
      // and returns an ApiResponse-compatible error object.
      setApiResponse({
        status: 'error',
        message: 'Failed to run agent due to unexpected error in API call.',
        error_details: [String(e)],
      });
    }
    setIsLoading(false);
  };
*/
