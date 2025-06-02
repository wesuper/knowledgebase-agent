import React from 'react';
import Link from 'next/link';

interface ResultsDisplayProps {
  processedFiles: string[] | null;
  message: string | null; // General message, could be success or info
  error: string | null;   // Specific error message string
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ processedFiles, message, error }) => {
  if (error) {
    // Use className from globals.css
    return <div className="error-message">Error: {error}</div>;
  }

  return (
    <div style={{ marginTop: '25px', padding: '15px', border: '1px solid #e0e0e0', borderRadius: '5px', backgroundColor: '#f9f9f9' }}>
      {/* Use success-message class for non-error messages */}
      {message && <div className="success-message">{message}</div>}

      {processedFiles && processedFiles.length > 0 && (
        <>
          <h4 style={{ marginTop: message ? '15px' : '0', marginBottom: '10px', fontSize: '1.2em' }}>Processed Files:</h4>
          <ul style={{ listStyleType: 'none', paddingLeft: '0' }}>
            {processedFiles.map((file, index) => {
              const basePathToRemove = 'agent_execution_directory/crew-paper/';
              let relativePath = file;
              if (file.startsWith(basePathToRemove)) {
                relativePath = file.substring(basePathToRemove.length);
              }
              const encodedPathParts = relativePath.split('/').map(part => encodeURIComponent(part));
              const viewUrl = `/view/${encodedPathParts.join('/')}`;

              return (
                <li key={index} style={{
                  marginBottom: '8px',
                  padding: '8px',
                  backgroundColor: '#fff',
                  border: '1px solid #eee',
                  borderRadius: '4px'
                }}>
                  <Link href={viewUrl} legacyBehavior>
                    <a target="_blank" rel="noopener noreferrer" style={{ color: '#0070f3', textDecoration: 'none', fontWeight: '500' }}>
                      {/* Display a more user-friendly name, e.g., the last part of the path */}
                      {relativePath.split('/').pop() || relativePath}
                    </a>
                  </Link>
                  <br/>
                  <small style={{color: '#777'}}>Full path: {file}</small>
                </li>
              );
            })}
          </ul>
        </>
      )}
      {/* Case: No error, no specific operational message, and no files processed (e.g., user cancelled) */}
      {!error && !message && (!processedFiles || processedFiles.length === 0) && (
        <p style={{ color: '#555', fontStyle: 'italic' }}>No results to display.</p>
      )}
    </div>
  );
};

export default ResultsDisplay;
