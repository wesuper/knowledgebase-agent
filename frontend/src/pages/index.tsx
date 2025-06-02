import React, { useState } from 'react';
import InputForm from '@/components/InputForm';
import ResultsDisplay from '@/components/ResultsDisplay';
import { runAgent, ApiResponse } from '@/services/agentApi';

const HomePage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);

  const handleSubmit = async (inputText: string) => {
    setIsLoading(true);
    setApiResponse(null);

    try {
      console.log("Submitting text to agent:", inputText);
      const response = await runAgent(inputText);
      console.log("Received API response:", response);
      setApiResponse(response);
    } catch (e) {
      console.error("Unexpected error in handleSubmit:", e);
      setApiResponse({
        status: 'error',
        message: 'An unexpected error occurred on the client-side.',
        error_details: [String(e)],
        processed_markdown_paths: [],
        error_summary: String(e)
      });
    }
    setIsLoading(false);
  };

  let displayError: string | null = null;
  if (apiResponse?.status === 'error' || apiResponse?.status === 'completed_with_errors') {
    displayError = apiResponse.error_summary || apiResponse.message;
  }

  let displayMessage: string | null = null;
  if (apiResponse && apiResponse.status !== 'error') {
    displayMessage = apiResponse.message;
    if (apiResponse.status === 'completed_with_errors' && apiResponse.error_summary) {
        displayMessage += ` (Note: Some errors occurred - ${apiResponse.error_summary})`;
    }
  }

  return (
    // Use the global 'container' class for consistent layout and styling
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '40px', paddingTop: '20px' }}>
        <h1>AI Content Processing Agent</h1>
        <p style={{ fontSize: '1.1rem', color: '#555' }}>
          Enter text containing URLs. The agent will extract content, generate summaries,
          and create mind maps.
        </p>
      </header>

      <section style={{ marginBottom: '30px' }}>
        <InputForm onSubmit={handleSubmit} isLoading={isLoading} />
      </section>

      {isLoading && (
        <div style={{ textAlign: 'center', marginTop: '30px', marginBottom: '30px' }}>
          <p style={{ fontSize: '1.1rem', marginBottom: '15px' }}>Processing... Please wait.</p>
          <div style={{
            border: '5px solid #f3f3f3',
            borderTop: '5px solid #0070f3',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            animation: 'spin 1s linear infinite',
            margin: '20px auto'
          }}></div>
          {/* Keyframes are in globals.css now, but if they weren't, this would be one way: */}
          {/* <style jsx global>{`...`}</style> */}
        </div>
      )}

      {apiResponse && !isLoading && (
        <section>
          <ResultsDisplay
            error={displayError}
            message={displayMessage}
            processedFiles={apiResponse.processed_markdown_paths || null}
          />
        </section>
      )}

      {!isLoading && !apiResponse && (
        <div style={{ textAlign: 'center', marginTop: '40px', color: '#777', padding: '20px' }}>
          <p>Submit text with URLs above to begin processing.</p>
        </div>
      )}
      <style jsx global>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default HomePage;
